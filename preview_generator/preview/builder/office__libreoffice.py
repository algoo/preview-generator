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


class OfficePreviewBuilderLibreoffice(PreviewBuilder):
    @classmethod
    def get_supported_mimetypes(cls) -> typing.List[str]:
        return [
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # nopep8
            'application/vnd.oasis.opendocument.text',
            'application/vnd.oasis.opendocument.spreadsheet',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # nopep8
            'application/vnd.openxmlformats-officedocument.wordprocessingml.template',  # nopep8
            'application/vnd.ms-word.document.macroEnabled.12',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # nopep8
            'application/vnd.openxmlformats-officedocument.spreadsheetml.template',  # nopep8
            'application/vnd.ms-excel.sheet.macroEnabled.12',
            'application/vnd.ms-excel.template.macroEnabled.12',
            'application/vnd.ms-excel.addin.macroEnabled.12',
            'application/vnd.ms-excel.sheet.binary.macroEnabled.12',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',  # nopep8
            'application/vnd.openxmlformats-officedocument.presentationml.template',  # nopep8
            'application/vnd.openxmlformats-officedocument.presentationml.slideshow',  # nopep8
            'application/vnd.ms-powerpoint.addin.macroEnabled.12',
            'application/vnd.ms-powerpoint.presentation.macroEnabled.12',
            'application/vnd.ms-powerpoint.template.macroEnabled.12',
            'application/vnd.ms-powerpoint.slideshow.macroEnabled.12',
            'application/vnd.oasis.opendocument.spreadsheet',
            'application/vnd.oasis.opendocument.text',
            'application/vnd.oasis.opendocument.text-template',
            'application/vnd.oasis.opendocument.text-web',
            'application/vnd.oasis.opendocument.text-master',
            'application/vnd.oasis.opendocument.graphics',
            'application/vnd.oasis.opendocument.graphics-template',
            'application/vnd.oasis.opendocument.presentation',
            'application/vnd.oasis.opendocument.presentation-template',
            'application/vnd.oasis.opendocument.spreadsheet-template',
            'application/vnd.oasis.opendocument.chart',
            'application/vnd.oasis.opendocument.chart',
            'application/vnd.oasis.opendocument.formula',
            'application/vnd.oasis.opendocument.database',
            'application/vnd.oasis.opendocument.image',
            'application/vnd.openofficeorg.extension',
            ]  # type: typing.List[str]

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

        intermediate_filename = preview_name.split('-page')[0]
        intermediate_pdf_file_path = os.path.join(
            cache_path,
            '{}.pdf'.format(intermediate_filename)
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
                    input_stream,
                    cache_path,
                    intermediate_filename
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


def create_flag_file(filepath: str) -> None:
    # the flag is used to avoid concurrent build of same previews
    try:
        os.mkdir(filepath+'_flag')
    except OSError:
        pass


def convert_office_document_to_pdf(
        file_content: typing.IO[bytes],
        cache_path: str,
        file_name: str
) -> BytesIO:

    cache_filename_path = cache_path + file_name

    create_flag_file(cache_filename_path)

    if not os.path.exists(cache_filename_path):

        with open('{path}{file_name}'.format(
                path=cache_path,
                file_name=file_name), 'wb') \
                as odt_temp:
            file_content.seek(0, 0)
            buffer = file_content.read(1024)
            while buffer:
                odt_temp.write(buffer)
                buffer = file_content.read(1024)

        try:
            logging.info('Creation of directory' + cache_path)
            os.makedirs(cache_path)
        except OSError:
            pass

        # TODO There's probably a cleaner way to convert to pdf
        check_call(
            [
                'libreoffice',
                '--headless',
                '--convert-to',
                'pdf:writer_pdf_Export',
                '{path}{extension}'.format(path=cache_path, extension=file_name),  # nopep8
                '--outdir',
                cache_path,
                '-env:UserInstallation=file:///tmp/LibreOffice_Conversion_${USER}',  # nopep8
            ],
            stdout=DEVNULL, stderr=STDOUT
        )

    try:
        logging.info('Removing directory' + cache_path + file_name + '_flag')
        os.removedirs(cache_path + file_name + '_flag')
    except OSError:
        pass

    try:
        logging.info('Removing directory {path}{file_name}'.format(
            path=cache_path,
            file_name=file_name
        )
        )
        os.remove('{path}{file_name}'.format(
            path=cache_path,
            file_name=file_name
        )
        )
    except OSError:
        pass

    with open('{path}{file_name}.pdf'.format(
            path=cache_path,
            file_name=file_name
    ), 'rb') as pdf:
        pdf.seek(0, 0)
        content_as_bytes = pdf.read()
        output = BytesIO(content_as_bytes)
        output.seek(0, 0)

        return output
