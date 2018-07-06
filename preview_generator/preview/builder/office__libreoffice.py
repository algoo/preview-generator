# -*- coding: utf-8 -*-

from io import BytesIO
import logging
import os
from subprocess import check_call
from subprocess import DEVNULL
from subprocess import STDOUT
import time
import typing

from PyPDF2 import PdfFileReader
from PyPDF2 import PdfFileWriter

from preview_generator.exception import BuilderDependencyNotFound
from preview_generator.exception import ExecutableNotFound
from preview_generator.preview.generic_preview import PreviewBuilder
from preview_generator.utils import check_executable_is_available
from preview_generator.utils import ImgDims
from preview_generator.preview.builder.image__wand import convert_pdf_to_jpeg
from pathlib import Path


class OfficePreviewBuilderLibreoffice(PreviewBuilder):
    @classmethod
    def get_supported_mimetypes(cls) -> typing.List[str]:
        return LO_MIMETYPES.keys()  # type: typing.List[str]

    @classmethod
    def check_dependencies(cls) -> bool:
        try:
            return check_executable_is_available('libreoffice')
        except ExecutableNotFound:
            raise BuilderDependencyNotFound(
                'this builder requires libreoffice to be available'
            )


    def build_jpeg_preview(
            self,
            file_path: str,
            preview_name: str,
            cache_path: str,
            page_id: int,
            extension: str = '.jpg',
            size: ImgDims=None
    ) -> None:

        with open(file_path, 'rb') as odt:
            if os.path.exists(
                    '{path}{file_name}.pdf'.format(
                        path=cache_path,
                        file_name=preview_name
                    )):
                input_pdf_stream = open(
                    '{path}.pdf'.format(
                        path=cache_path + preview_name,
                    ), 'rb')

            else:
                if self.cache_file_process_already_running(
                                cache_path + preview_name):
                    time.sleep(2)
                    return self.build_jpeg_preview(
                        file_path=file_path,
                        preview_name=preview_name,
                        cache_path=cache_path,
                        extension=extension,
                        page_id=page_id
                    )

                else:
                    input_pdf_stream = convert_office_document_to_pdf(
                        odt,
                        os.path.splitext(file_path)[1],  # get the file extension
                        cache_path,
                        preview_name
                    )

            input_pdf = PdfFileReader(input_pdf_stream)
            intermediate_pdf = PdfFileWriter()
            intermediate_pdf.addPage(input_pdf.getPage(int(page_id)))

            intermediate_pdf_stream = BytesIO()
            intermediate_pdf.write(intermediate_pdf_stream)
            intermediate_pdf_stream.seek(0, 0)
            jpeg_stream = convert_pdf_to_jpeg(intermediate_pdf_stream, size)

            jpeg_preview_path = '{path}{file_name}{extension}'.format(
                path=cache_path,
                file_name=preview_name,
                extension=extension
            )

            with open(jpeg_preview_path, 'wb') as jpeg_output_stream:
                buffer = jpeg_stream.read(1024)
                while buffer:
                    jpeg_output_stream.write(buffer)
                    buffer = jpeg_stream.read(1024)

    def get_page_number(self, file_path: str, preview_name: str,
                        cache_path: str) -> int:

        page_nb_file_path = cache_path + preview_name + '_page_nb'

        if not os.path.exists(page_nb_file_path):
            pdf_version_filepath = cache_path + preview_name + '.pdf'
            if not os.path.exists(pdf_version_filepath):
                self.build_pdf_preview(
                    file_path=file_path,
                    preview_name=preview_name,
                    cache_path=cache_path
                )

            with open(page_nb_file_path, 'w') as page_nb_file_stream:
                page_nb_file_stream.seek(0, 0)
                with open(pdf_version_filepath, 'rb') as pdf_stream:
                    pdf_reader = PdfFileReader(pdf_stream)
                    page_nb_file_stream.write(str(pdf_reader.numPages))

        with open(page_nb_file_path, 'r') as page_nb_stream:
            page_nb = int(page_nb_stream.read())
            return page_nb

    def has_pdf_preview(self) -> bool:
        """
        Override and return True if your builder allow PDF preview
        :return:
        """
        return True

    def build_pdf_preview(
            self,
            file_path: str,
            preview_name: str,
            cache_path: str,
            extension: str = '.pdf',
            page_id: int = -1) -> None:

        input_extension = os.path.splitext(file_path)[1]
        intermediate_pdf_filename = preview_name.split('-page')[0] + '.pdf'
        intermediate_pdf_file_path = os.path.join(
            cache_path,
            intermediate_pdf_filename
        )

        if not os.path.exists(intermediate_pdf_file_path):
            if os.path.exists(intermediate_pdf_file_path + '_flag'):
                # Wait 2 seconds, then retry
                time.sleep(2)
                return self.build_pdf_preview(
                    file_path=file_path,
                    preview_name=preview_name,
                    cache_path=cache_path,
                    extension=extension,
                    page_id=page_id
                )

            with open(file_path, 'rb') as input_stream:

                # first step is to convert full document to full pdf
                convert_office_document_to_pdf(
                    file_content=input_stream,
                    input_extension=input_extension,
                    cache_path=cache_path,
                    output_filepath=intermediate_pdf_file_path
                )

        if page_id < 0:
            return  # in this case, the intermediate file is the requested one

        pdf_in = PdfFileReader(intermediate_pdf_file_path)
        output_file_path = os.path.join(cache_path, '{}{}'.format(preview_name, extension))
        pdf_out = PdfFileWriter()
        pdf_out.addPage(pdf_in.getPage(page_id))

        with open(output_file_path, 'wb') as output_file:
            pdf_out.write(output_file)

    def cache_file_process_already_running(self, file_name: str) -> bool:
        if os.path.exists(file_name + '_flag'):
            return True
        else:
            return False

def create_flag_file(filepath: str) -> str:
    """
    Create a flag file in order to avoid concurrent build of same previews
    :param filepath: file to protect
    :return: flag file path
    """
    flag_file_path = '{}_flag'.format(filepath)
    Path(flag_file_path).touch()
    return flag_file_path


def write_file_content(
        file_content: typing.IO[bytes],
        output_filepath: str
):
    with open(output_filepath, 'wb') as temporary_file:
        file_content.seek(0, 0)
        buffer = file_content.read(1024)
        while buffer:
            temporary_file.write(buffer)
            buffer = file_content.read(1024)


def convert_office_document_to_pdf(
        file_content: typing.IO[bytes],
        input_extension: str,  # example: '.dxf'
        cache_path: str,
        output_filepath: str
) -> BytesIO:
    logging.debug('converting file bytes {} to pdf file {}'.format(file_content, output_filepath))  # nopep8
    temporary_input_content_path = output_filepath + input_extension  # nopep8
    flag_file_path = create_flag_file(output_filepath)

    logging.debug('conversion is based on temporary file {}'.format(temporary_input_content_path))  # nopep8

    if not os.path.exists(output_filepath):
        write_file_content(file_content, output_filepath=temporary_input_content_path)  # nopep8
        logging.debug('temporary file written: {}'.format(temporary_input_content_path))  # nopep8
        logging.debug('converting {} to pdf into folder {}'.format(
            temporary_input_content_path,
            cache_path
        ))
        check_call(
            [
                'libreoffice',
                '--headless',
                '--convert-to',
                'pdf:writer_pdf_Export',
                temporary_input_content_path,
                '--outdir',
                cache_path,
                '-env:UserInstallation=file:///tmp/LibreOffice_Conversion_${USER}',  # nopep8
            ],
            stdout=DEVNULL,
            stderr=STDOUT
        )
    # HACK - D.A. - 2018-05-31 - name is defined by libreoffice
    # according to input file name, for homogeneity we prefer to rename it
    logging.debug('renaming output file {} to {}'.format(output_filepath+'.pdf', output_filepath))
    os.rename(output_filepath+'.pdf', output_filepath)

    logging.debug('Removing flag file {}'.format(flag_file_path))
    os.remove(flag_file_path)

    logging.info('Removing temporary copy file {}'.format(temporary_input_content_path))  # nopep8
    os.remove(temporary_input_content_path)

    with open(output_filepath, 'rb') as pdf_handle:
        pdf_handle.seek(0, 0)
        content_as_bytes = pdf_handle.read()
        output = BytesIO(content_as_bytes)
        output.seek(0, 0)
        return output


# HACK - D.A. - 2018-05-31
# Code duplicated from https://raw.githubusercontent.com/LibreOffice/core/master/bin/get-bugzilla-attachments-by-mimetype
LO_MIMETYPES = {
# ODF
    'application/vnd.oasis.opendocument.base': 'odb',
    'application/vnd.oasis.opendocument.database': 'odb',
    'application/vnd.oasis.opendocument.chart': 'odc',
    'application/vnd.oasis.opendocument.chart-template': 'otc',
    'application/vnd.oasis.opendocument.formula': 'odf',
    'application/vnd.oasis.opendocument.formula-template': 'otf',
    'application/vnd.oasis.opendocument.graphics': 'odg',
    'application/vnd.oasis.opendocument.graphics-template': 'otg',
    'application/vnd.oasis.opendocument.graphics-flat-xml': 'fodg',
    'application/vnd.oasis.opendocument.presentation': 'odp',
    'application/vnd.oasis.opendocument.presentation-template': 'otp',
    'application/vnd.oasis.opendocument.presentation-flat-xml': 'fodp',
    'application/vnd.oasis.opendocument.spreadsheet': 'ods',
    'application/vnd.oasis.opendocument.spreadsheet-template': 'ots',
    'application/vnd.oasis.opendocument.spreadsheet-flat-xml': 'fods',
    'application/vnd.oasis.opendocument.text': 'odt',
    'application/vnd.oasis.opendocument.text-flat-xml': 'fodt',
    'application/vnd.oasis.opendocument.text-master': 'odm',
    'application/vnd.oasis.opendocument.text-template': 'ott',
    'application/vnd.oasis.opendocument.text-master-template': 'otm',
    'application/vnd.oasis.opendocument.text-web': 'oth',
# OOo XML
    'application/vnd.sun.xml.base': 'odb',
    'application/vnd.sun.xml.calc': 'sxc',
    'application/vnd.sun.xml.calc.template': 'stc',
    'application/vnd.sun.xml.chart': 'sxs',
    'application/vnd.sun.xml.draw': 'sxd',
    'application/vnd.sun.xml.draw.template': 'std',
    'application/vnd.sun.xml.impress': 'sxi',
    'application/vnd.sun.xml.impress.template': 'sti',
    'application/vnd.sun.xml.math': 'sxm',
    'application/vnd.sun.xml.writer': 'sxw',
    'application/vnd.sun.xml.writer.global': 'sxg',
    'application/vnd.sun.xml.writer.template': 'stw',
    'application/vnd.sun.xml.writer.web': 'stw',
# MSO
    'application/rtf': 'rtf',
    'text/rtf': 'rtf',
    'application/msword': 'doc',
    'application/vnd.ms-powerpoint': 'ppt',
    'application/vnd.ms-excel': 'xls',
    'application/vnd.ms-excel.sheet.binary.macroEnabled.12': 'xlsb',
    'application/vnd.ms-excel.sheet.macroEnabled.12': 'xlsm',
    'application/vnd.ms-excel.template.macroEnabled.12': 'xltm',
    'application/vnd.ms-powerpoint.presentation.macroEnabled.12': 'pptm',
    'application/vnd.ms-powerpoint.slide.macroEnabled.12': 'sldm',
    'application/vnd.ms-powerpoint.slideshow.macroEnabled.12': 'ppsm',
    'application/vnd.ms-powerpoint.template.macroEnabled.12': 'potm',
    'application/vnd.ms-word.document.macroEnabled.12': 'docm',
    'application/vnd.ms-word.template.macroEnabled.12': 'dotm',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.template': 'xltx',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'pptx',
    'application/vnd.openxmlformats-officedocument.presentationml.template': 'potx',
    'application/vnd.openxmlformats-officedocument.presentationml.slideshow': 'ppsx',
    'application/vnd.openxmlformats-officedocument.presentationml.slide': 'sldx',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.template': 'dotx',
    'application/vnd.visio': 'vsd',
    'application/visio.drawing': 'vsd',
    'application/vnd.visio2013': 'vsdx',
    'application/vnd.visio.xml': 'vdx',
    'application/x-mspublisher': 'pub',
#WPS Office
    'application/wps-office.doc': 'doc',
    'application/wps-office.docx': 'docx',
    'application/wps-office.xls': 'xls',
    'application/wps-office.xlsx': 'xlsx',
    'application/wps-office.ppt': 'ppt',
    'application/wps-office.pptx': 'pptx',
# W3C
    'application/xhtml+xml': 'xhtml',
    'application/mathml+xml': 'mml',
    'text/html': 'html',
    'application/docbook+xml': 'docbook',
# misc
    'text/csv': 'csv',
    'text/spreadsheet': 'slk',
    'application/x-qpro': 'qpro',
    'application/x-dbase': 'dbf',
    'application/vnd.corel-draw': 'cdr',
    'application/vnd.lotus-wordpro': 'lwp',
    'application/vnd.lotus-1-2-3': 'wks',
    'application/vnd.wordperfect': 'wpd',
    'application/wordperfect5.1': 'wpd',
    'application/vnd.ms-works': 'wps',
    'application/clarisworks' : 'cwk',
    'application/macwriteii' : 'mw',
    'application/vnd.apple.keynote': 'key',
    'application/vnd.apple.numbers': 'numbers',
    'application/vnd.apple.pages': 'pages',
    'application/x-iwork-keynote-sffkey': 'key',
    'application/x-iwork-numbers-sffnumbers': 'numbers',
    'application/x-iwork-pages-sffpages': 'pages',
    'application/x-hwp': 'hwp',
    'application/x-aportisdoc': 'pdb',
    'application/prs.plucker' : 'pdb_plucker',
    'application/vnd.palm' : 'pdb_palm',
    'application/x-sony-bbeb' : 'lrf',
    'application/x-pocket-word': 'psw',
    'application/x-t602': '602',
    'application/x-fictionbook+xml': 'fb2',
    'application/x-abiword': 'abw',
    'application/x-pagemaker': 'pmd',
    'application/x-gnumeric': 'gnumeric',
    'application/vnd.stardivision.calc': 'sdc',
    'application/vnd.stardivision.draw': 'sda',
    'application/vnd.stardivision.writer': 'sdw',
    'application/x-starcalc': 'sdc',
    'application/x-stardraw': 'sdd',
    'application/x-starwriter': 'sdw',
# relatively uncommon image mimetypes
    'image/x-freehand': 'fh',
    'image/cgm': 'cgm',
    'image/tif': 'tiff',
    'image/tiff': 'tiff',
    'image/vnd.dxf': 'dxf',
    'image/emf': 'emf',
    'image/x-emf': 'emf',
    'image/x-targa': 'tga',
    'image/x-sgf': 'sgf',
    'image/x-svm': 'svm',
    'image/wmf': 'wmf',
    'image/x-wmf': 'wmf',
    'image/x-pict': 'pict',
    'image/x-cmx': 'cmx',
    # 'image/svg+xml': 'svg',  # nopep8 HACK - D.A. - 2018-07-05 Do not use libreoffice for SVG as inkscape is better
    # 'image/bmp': 'bmp',
    # 'image/x-ms-bmp': 'bmp',
    # 'image/x-MS-bmp': 'bmp',
    'image/x-wpg': 'wpg',
    'image/x-eps': 'eps',
    'image/x-met': 'met',
    'image/x-portable-bitmap': 'pbm',
    'image/x-photo-cd': 'pcd',
    'image/x-pcx': 'pcx',
    'image/x-portable-graymap': 'pgm',
    'image/x-portable-pixmap': 'ppm',
    'image/vnd.adobe.photoshop': 'psd',
    'image/x-cmu-raster': 'ras',
    'image/x-sun-raster': 'ras',
    'image/x-xbitmap': 'xbm',
    'image/x-xpixmap': 'xpm',
}

