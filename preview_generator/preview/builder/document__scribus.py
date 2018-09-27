# -*- coding: utf-8 -*-

import os
import logging
import typing
import time
from io import BytesIO
from packaging import version
from pathlib import Path
from subprocess import check_call
from subprocess import DEVNULL
from subprocess import STDOUT
from subprocess import CalledProcessError

from PyPDF2 import PdfFileReader
from PyPDF2 import PdfFileWriter

from preview_generator.exception import PreviewGeneratorException
from preview_generator.exception import BuilderDependencyNotFound
from preview_generator.exception import ExecutableNotFound
from preview_generator.preview.generic_preview import PreviewBuilder
from preview_generator.preview.builder.image__wand import convert_pdf_to_jpeg
from preview_generator.utils import check_executable_is_available
from preview_generator.utils import ImgDims

SCRIPT_FOLDER_NAME = 'scripts'
SCRIPT_NAME = 'scribus_sla_to_pdf.py'
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT_PATH = os.path.join(parent_dir, SCRIPT_FOLDER_NAME, SCRIPT_NAME)
# TIMEOUT = 3


class DocumentPreviewBuilderScribus(PreviewBuilder):

    @classmethod
    def check_dependencies(cls) -> bool:
        try:
            # BUG - 2018/09/26 - Basile - using '-v' on scribus >= 1.5 gives
            # the version then crash, using FileNotFoundError to make the diff
            result = check_call(['scribus', '-v'])
        except FileNotFoundError:
            return False
        except CalledProcessError:
            return True

    @classmethod
    def get_label(cls) -> str:
        return 'application/vnd.scribus - based on Scribus'

    @classmethod
    def get_supported_mimetypes(cls) -> typing.List[str]:
        return ['application/vnd.scribus']

    def build_jpeg_preview(
        self,
        file_path: str,
        preview_name: str,
        cache_path: str,
        page_id: int,
        extension: str='.jpg',
        size: ImgDims=None
    ) -> None:

        import ipdb; ipdb.set_trace()
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
                full_path = os.path.join(cache_path, preview_name)
                if self.cache_file_process_already_running(full_path):
                    time.sleep(2)
                    return self.build_jpeg_preview(
                        file_path=file_path,
                        preview_name=preview_name,
                        cache_path=cache_path,
                        extension=extension,
                        page_id=page_id
                    )

                else:
                    input_pdf_stream = convert_scribus_document_to_pdf(
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

    def get_page_number(
        self,
        file_path: str,
        preview_name: str,
        cache_path: str
    ) -> int:

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
        page_id: int = -1
    ) -> None:

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
                convert_scribus_document_to_pdf(
                    file_content=input_stream,
                    input_extension=input_extension,
                    cache_path=cache_path,
                    output_filepath=intermediate_pdf_file_path
                )

        if page_id < 0:
            return  # in this case, the intermediate file is the requested one

        pdf_in = PdfFileReader(intermediate_pdf_file_path)
        output_file_path = os.path.join(
            cache_path, '{}{}'.format(preview_name, extension)
        )
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


def convert_scribus_document_to_pdf(
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
        result = check_call(
            [
                'scribus', '-g', '-py', SCRIPT_PATH,
                output_filepath, '--', temporary_input_content_path
            ],
            stdout=DEVNULL, stderr=STDOUT
        )

    # HACK - D.A. - 2018-05-31 - name is defined by libreoffice
    # according to input file name, for homogeneity we prefer to rename it
    logging.debug('renaming output file {} to {}'.format(
        output_filepath+'.pdf', output_filepath)
    )

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
