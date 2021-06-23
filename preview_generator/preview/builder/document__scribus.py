# -*- coding: utf-8 -*-

from io import BytesIO
import logging
import os
from shutil import which
from subprocess import DEVNULL
from subprocess import STDOUT
from subprocess import check_call
from subprocess import check_output
import typing

from preview_generator.exception import BuilderDependencyNotFound
from preview_generator.extension import mimetypes_storage
from preview_generator.preview.builder.document_generic import DocumentPreviewBuilder
from preview_generator.preview.builder.document_generic import create_flag_file
from preview_generator.preview.builder.document_generic import write_file_content
from preview_generator.utils import LOGGER_NAME
from preview_generator.utils import executable_is_available

xvfbwrapper_installed = True
try:
    from xvfbwrapper import Xvfb
except ImportError:
    xvfbwrapper_installed = False

SCRIPT_FOLDER_NAME = "scripts"
SCRIPT_NAME = "scribus_sla_to_pdf.py"
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT_PATH = os.path.join(parent_dir, SCRIPT_FOLDER_NAME, SCRIPT_NAME)


class DocumentPreviewBuilderScribus(DocumentPreviewBuilder):
    @classmethod
    def check_dependencies(cls) -> None:
        if not xvfbwrapper_installed:
            raise BuilderDependencyNotFound("this builder requires xvfbwrapper")
        if not executable_is_available("scribus"):
            raise BuilderDependencyNotFound("this builder requires scribus to be available")

    @classmethod
    def dependencies_versions(cls) -> typing.Optional[str]:
        with Xvfb():
            lines = check_output(["scribus", "-v"], stderr=STDOUT, universal_newlines=True)
        version = " ".join(line for line in lines.split("\n") if "version" in line.lower())
        return "{} from {}".format(version, which("scribus"))

    @classmethod
    def get_label(cls) -> str:
        return "application/vnd.scribus - based on Scribus"

    @classmethod
    def get_supported_mimetypes(cls) -> typing.List[str]:
        return ["application/vnd.scribus"]

    def _convert_to_pdf(
        self,
        file_content: typing.IO[bytes],
        input_extension: str,  # example: '.dxf'
        cache_path: str,
        output_filepath: str,
        mimetype: str,
    ) -> BytesIO:

        return convert_sla_to_pdf(
            file_content, input_extension, cache_path, output_filepath, mimetype
        )


def convert_sla_to_pdf(
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
    temporary_input_content_path = output_filepath
    if input_extension:
        temporary_input_content_path += input_extension
    with create_flag_file(output_filepath):

        logger.debug(
            "conversion is based on temporary file {}".format(temporary_input_content_path)
        )  # nopep8

        if not os.path.exists(output_filepath):
            write_file_content(file_content, output_filepath=temporary_input_content_path)  # nopep8
            logger.debug(
                "temporary file written: {}".format(temporary_input_content_path)
            )  # nopep8
            logger.debug(
                "converting {} to pdf into folder {}".format(
                    temporary_input_content_path, cache_path
                )
            )
            with Xvfb():
                check_call(
                    [
                        "scribus",
                        "-g",
                        "-py",
                        SCRIPT_PATH,
                        output_filepath,
                        "--",
                        temporary_input_content_path,
                    ],
                    stdout=DEVNULL,
                    stderr=STDOUT,
                )

        # HACK - D.A. - 2018-05-31 - name is defined by libreoffice
        # according to input file name, for homogeneity we prefer to rename it
        logger.debug(
            "renaming output file {} to {}".format(output_filepath + ".pdf", output_filepath)
        )

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
