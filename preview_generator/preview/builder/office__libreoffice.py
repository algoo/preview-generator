# -*- coding: utf-8 -*-
import contextlib
import hashlib
from io import BytesIO
import logging
import os
from shutil import which
import signal
from subprocess import DEVNULL
from subprocess import Popen
from subprocess import STDOUT
from subprocess import check_output
import typing

from filelock import FileLock

from preview_generator.exception import BuilderDependencyNotFound
from preview_generator.exception import InputExtensionNotFound
from preview_generator.extension import mimetypes_storage
from preview_generator.preview.builder.document_generic import DocumentPreviewBuilder
from preview_generator.preview.builder.document_generic import create_flag_file
from preview_generator.preview.builder.document_generic import write_file_content
from preview_generator.utils import LOCKFILE_EXTENSION
from preview_generator.utils import LOCK_DEFAULT_TIMEOUT
from preview_generator.utils import LOGGER_NAME
from preview_generator.utils import MimetypeMapping
from preview_generator.utils import executable_is_available

LIBREOFFICE_LOCK_NAME = "libreoffice"
# NOTE - SG - 20210420 - The default timeout value is 60 seconds and can be overridden
# by the LIBREOFFICE_PROCESS_TIMEOUT variable.
# If this variable has a value lesser or equal than 0, the timeout is disabled
env_var = os.getenv("LIBREOFFICE_PROCESS_TIMEOUT", "60")
try:
    timeout_from_var = float(env_var)
except ValueError:
    raise ValueError(
        "Invalid value for LIBREOFFICE_PROCESS_TIMEOUT: it should be a number, got {}".format(
            env_var
        )
    )
if timeout_from_var > 0:
    LIBREOFFICE_PROCESS_TIMEOUT = timeout_from_var  # type: typing.Optional[float]
else:
    LIBREOFFICE_PROCESS_TIMEOUT = None


class OfficePreviewBuilderLibreoffice(DocumentPreviewBuilder):
    @classmethod
    def get_label(cls) -> str:
        return "Documents - based on LibreOffice"

    @classmethod
    def get_supported_mimetypes(cls) -> typing.List[str]:
        return [k for k in typing.cast(str, LO_MIMETYPES.keys())]

    @classmethod
    def get_mimetypes_mapping(cls) -> typing.List[MimetypeMapping]:
        return [
            MimetypeMapping(
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", ".xlsx"
            )
        ]

    @classmethod
    def check_dependencies(cls) -> None:
        if not executable_is_available("libreoffice"):
            raise BuilderDependencyNotFound("this builder requires libreoffice to be available")

    @classmethod
    def dependencies_versions(cls) -> typing.Optional[str]:
        return "{} from {}".format(
            check_output(["libreoffice", "--version"], universal_newlines=True).strip(),
            which("libreoffice"),
        )

    def _convert_to_pdf(
        self,
        file_content: typing.IO[bytes],
        input_extension: str,  # example: '.dxf'
        cache_path: str,
        output_filepath: str,
        mimetype: str,
    ) -> BytesIO:

        return self.convert_office_document_to_pdf(
            file_content, input_extension, cache_path, output_filepath, mimetype
        )

    def _get_libreoffice_lock(self, cache_path: str) -> FileLock:
        # INFO - jumenzel - 2019-03-12 - Do not allow multiple concurrent libreoffice calls to avoid issue.
        # INFO - jumenzel - 2019-03-12 - Should we allow running multiple libreoffice instances ?
        # see https://github.com/algoo/preview-generator/issues/77
        file_lock_path = os.path.join(cache_path, LIBREOFFICE_LOCK_NAME + LOCKFILE_EXTENSION)
        return FileLock(file_lock_path, timeout=LOCK_DEFAULT_TIMEOUT)

    def convert_office_document_to_pdf(
        self,
        file_content: typing.IO[bytes],
        input_extension: typing.Optional[str],  # example: '.dxf'
        cache_path: str,
        output_filepath: str,
        mimetype: str,
    ) -> BytesIO:
        logger = logging.getLogger(LOGGER_NAME)
        logger.debug(
            "converting file bytes {} to pdf file {}".format(file_content, output_filepath)
        )  # nopep8
        if not input_extension:
            input_extension = mimetypes_storage.guess_extension(mimetype, strict=False)
        if not input_extension:
            raise InputExtensionNotFound("unable to found input extension from mimetype")  # nopep8
        temporary_input_content_path = output_filepath + input_extension  # nopep8
        with create_flag_file(output_filepath):
            logger.debug(
                "conversion is based on temporary file {}".format(temporary_input_content_path)
            )  # nopep8

            if not os.path.exists(output_filepath):
                write_file_content(file_content, output_filepath=temporary_input_content_path)
                logger.debug(
                    "temporary file written: {}".format(temporary_input_content_path)
                )  # nopep8
                logger.debug(
                    "converting {} to pdf into folder {}".format(
                        temporary_input_content_path, cache_path
                    )
                )

                libreoffice_lock = self._get_libreoffice_lock(cache_path)
                cache_path_hash = hashlib.md5(cache_path.encode("utf-8")).hexdigest()
                default_filters_by_mimetype = {"text/html": "-infilter=writerglobal8_HTML"}
                infilter = default_filters_by_mimetype.get(mimetype, "")
                with libreoffice_lock:
                    process = Popen(
                        [
                            "libreoffice",
                            "--headless",
                            infilter,
                            "--convert-to",
                            "pdf:writer_pdf_Export",
                            temporary_input_content_path,
                            "--outdir",
                            cache_path,
                            "-env:UserInstallation=file:///tmp/LibreOffice-conversion-{}".format(
                                cache_path_hash
                            ),  # nopep8
                        ],
                        stdout=DEVNULL,
                        stderr=STDOUT,
                        start_new_session=True,
                    )
                    process_timeout = LIBREOFFICE_PROCESS_TIMEOUT
                    if process_timeout is not None:
                        stop_process_timeout = process_timeout / 10  # type: typing.Optional[float]
                    else:
                        stop_process_timeout = None
                    try:
                        process.communicate(timeout=process_timeout)
                    except Exception as exc:
                        try:
                            # INFO - SG - 2021-04-16
                            # we waited long enough (or we got another exception), give a little time to the process
                            # to exit cleanly
                            logger.warning(
                                "The preview generation for {} took too long, try aborting it".format(
                                    temporary_input_content_path
                                )
                            )
                            os.killpg(process.pid, signal.SIGTERM)
                            process.communicate(timeout=stop_process_timeout)
                        except Exception:
                            # too slow to exit… let's kill
                            logger.warning(
                                "Preview generation process for {} doesn't respond, force stopping it".format(
                                    temporary_input_content_path
                                )
                            )
                            os.killpg(process.pid, signal.SIGKILL)
                            process.communicate(timeout=stop_process_timeout)
                        finally:
                            raise exc

            # HACK - D.A. - 2018-05-31 - name is defined by libreoffice
            # according to input file name, for homogeneity we prefer to rename it
            # HACK-HACK - B.L - 2018-10-8 - if file is given without its extension
            # in its name it won't have the double ".pdf"
            if os.path.exists(output_filepath + ".pdf"):
                logger.debug(
                    "renaming output file {} to {}".format(
                        output_filepath + ".pdf", output_filepath
                    )
                )
                os.rename(output_filepath + ".pdf", output_filepath)

            with contextlib.suppress(FileNotFoundError):
                logger.info(
                    "Removing temporary copy file {}".format(temporary_input_content_path)
                )  # nopep8
                os.remove(temporary_input_content_path)

        with open(output_filepath, "rb") as pdf_handle:
            pdf_handle.seek(0, 0)
            content_as_bytes = pdf_handle.read()
            output = BytesIO(content_as_bytes)
            output.seek(0, 0)
            return output


# HACK - D.A. - 2018-05-31
# Code duplicated from https://raw.githubusercontent.com/LibreOffice/core/master/bin/get-bugzilla-attachments-by-mimetype
LO_MIMETYPES = {
    # ODF
    # INFO - G.M - 2018-11-13 - Conversion of base to pdf is not correctly
    # supported by libreoffice itself
    # 'application/vnd.oasis.opendocument.base': 'odb',
    # 'application/vnd.oasis.opendocument.database': 'odb',
    "application/vnd.oasis.opendocument.chart": "odc",
    "application/vnd.oasis.opendocument.chart-template": "otc",
    "application/vnd.oasis.opendocument.formula": "odf",
    "application/vnd.oasis.opendocument.formula-template": "otf",
    "application/vnd.oasis.opendocument.graphics": "odg",
    "application/vnd.oasis.opendocument.graphics-template": "otg",
    "application/vnd.oasis.opendocument.graphics-flat-xml": "fodg",
    "application/vnd.oasis.opendocument.presentation": "odp",
    "application/vnd.oasis.opendocument.presentation-template": "otp",
    "application/vnd.oasis.opendocument.presentation-flat-xml": "fodp",
    "application/vnd.oasis.opendocument.spreadsheet": "ods",
    "application/vnd.oasis.opendocument.spreadsheet-template": "ots",
    "application/vnd.oasis.opendocument.spreadsheet-flat-xml": "fods",
    "application/vnd.oasis.opendocument.text": "odt",
    "application/vnd.oasis.opendocument.text-flat-xml": "fodt",
    "application/vnd.oasis.opendocument.text-master": "odm",
    "application/vnd.oasis.opendocument.text-template": "ott",
    "application/vnd.oasis.opendocument.text-master-template": "otm",
    "application/vnd.oasis.opendocument.text-web": "oth",
    # OOo XML
    # INFO - G.M - 2018-11-13 - Conversion of base to pdf is not correctly
    # supported by libreoffice itself
    # 'application/vnd.sun.xml.base': 'odb',
    "application/vnd.sun.xml.calc": "sxc",
    "application/vnd.sun.xml.calc.template": "stc",
    "application/vnd.sun.xml.chart": "sxs",
    "application/vnd.sun.xml.draw": "sxd",
    "application/vnd.sun.xml.draw.template": "std",
    "application/vnd.sun.xml.impress": "sxi",
    "application/vnd.sun.xml.impress.template": "sti",
    "application/vnd.sun.xml.math": "sxm",
    "application/vnd.sun.xml.writer": "sxw",
    "application/vnd.sun.xml.writer.global": "sxg",
    "application/vnd.sun.xml.writer.template": "stw",
    "application/vnd.sun.xml.writer.web": "stw",
    # MSO
    "application/rtf": "rtf",
    "text/rtf": "rtf",
    "application/msword": "doc",
    "application/vnd.ms-powerpoint": "ppt",
    "application/vnd.ms-excel": "xls",
    "application/vnd.ms-excel.sheet.binary.macroEnabled.12": "xlsb",
    "application/vnd.ms-excel.sheet.macroEnabled.12": "xlsm",
    "application/vnd.ms-excel.template.macroEnabled.12": "xltm",
    "application/vnd.ms-powerpoint.presentation.macroEnabled.12": "pptm",
    "application/vnd.ms-powerpoint.slide.macroEnabled.12": "sldm",
    "application/vnd.ms-powerpoint.slideshow.macroEnabled.12": "ppsm",
    "application/vnd.ms-powerpoint.template.macroEnabled.12": "potm",
    "application/vnd.ms-word.document.macroEnabled.12": "docm",
    "application/vnd.ms-word.template.macroEnabled.12": "dotm",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.template": "xltx",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": "pptx",
    "application/vnd.openxmlformats-officedocument.presentationml.template": "potx",
    "application/vnd.openxmlformats-officedocument.presentationml.slideshow": "ppsx",
    "application/vnd.openxmlformats-officedocument.presentationml.slide": "sldx",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.template": "dotx",
    "application/vnd.visio": "vsd",
    "application/visio.drawing": "vsd",
    "application/vnd.visio2013": "vsdx",
    "application/vnd.visio.xml": "vdx",
    "application/x-mspublisher": "pub",
    # WPS Office
    "application/wps-office.doc": "doc",
    "application/wps-office.docx": "docx",
    "application/wps-office.xls": "xls",
    "application/wps-office.xlsx": "xlsx",
    "application/wps-office.ppt": "ppt",
    "application/wps-office.pptx": "pptx",
    # W3C
    "application/xhtml+xml": "xhtml",
    "application/mathml+xml": "mml",
    "text/html": "html",
    "application/docbook+xml": "docbook",
    # misc
    "text/csv": "csv",
    "text/spreadsheet": "slk",
    "application/x-qpro": "qpro",
    "application/x-dbase": "dbf",
    "application/vnd.corel-draw": "cdr",
    "application/vnd.lotus-wordpro": "lwp",
    "application/vnd.lotus-1-2-3": "wks",
    "application/vnd.wordperfect": "wpd",
    "application/wordperfect5.1": "wpd",
    "application/vnd.ms-works": "wps",
    "application/clarisworks": "cwk",
    "application/macwriteii": "mw",
    "application/vnd.apple.keynote": "key",
    "application/vnd.apple.numbers": "numbers",
    "application/vnd.apple.pages": "pages",
    "application/x-iwork-keynote-sffkey": "key",
    "application/x-iwork-numbers-sffnumbers": "numbers",
    "application/x-iwork-pages-sffpages": "pages",
    "application/x-hwp": "hwp",
    "application/x-aportisdoc": "pdb",
    "application/prs.plucker": "pdb_plucker",
    "application/vnd.palm": "pdb_palm",
    "application/x-sony-bbeb": "lrf",
    "application/x-pocket-word": "psw",
    "application/x-t602": "602",
    "application/x-fictionbook+xml": "fb2",
    "application/x-abiword": "abw",
    "application/x-pagemaker": "pmd",
    "application/x-gnumeric": "gnumeric",
    "application/vnd.stardivision.calc": "sdc",
    "application/vnd.stardivision.draw": "sda",
    "application/vnd.stardivision.writer": "sdw",
    "application/x-starcalc": "sdc",
    "application/x-stardraw": "sdd",
    "application/x-starwriter": "sdw",
    # relatively uncommon image mimetypes
    "image/x-freehand": "fh",
    "image/cgm": "cgm",
    "image/tif": "tiff",
    "image/tiff": "tiff",
    "image/vnd.dxf": "dxf",
    "image/emf": "emf",
    "image/x-emf": "emf",
    "image/x-targa": "tga",
    "image/x-sgf": "sgf",
    "image/x-svm": "svm",
    "image/wmf": "wmf",
    "image/x-wmf": "wmf",
    "image/x-pict": "pict",
    "image/x-cmx": "cmx",
    # 'image/svg+xml': 'svg',  # nopep8 HACK - D.A. - 2018-07-05 Do not use libreoffice for SVG as inkscape is better
    # 'image/bmp': 'bmp',
    # 'image/x-ms-bmp': 'bmp',
    # 'image/x-MS-bmp': 'bmp',
    "image/x-wpg": "wpg",
    "image/x-eps": "eps",
    "image/x-met": "met",
    "image/x-portable-bitmap": "pbm",
    "image/x-photo-cd": "pcd",
    "image/x-pcx": "pcx",
    "image/x-portable-graymap": "pgm",
    "image/x-portable-pixmap": "ppm",
    "image/vnd.adobe.photoshop": "psd",
    "image/x-cmu-raster": "ras",
    "image/x-sun-raster": "ras",
    "image/x-xbitmap": "xbm",
    "image/x-xpixmap": "xpm",
}
