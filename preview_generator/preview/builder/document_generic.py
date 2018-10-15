# -*- coding: utf-8 -*-

from io import BytesIO
import os
import time
import typing

from pathlib import Path
from PyPDF2 import PdfFileReader
from PyPDF2 import PdfFileWriter

from preview_generator.preview.generic_preview import PreviewBuilder
from preview_generator.utils import ImgDims
from preview_generator.preview.builder.image__wand import convert_pdf_to_jpeg
from preview_generator.exception import PreviewGeneratorException


class DocumentPreviewBuilder(PreviewBuilder):

    def _convert_to_pdf(
        self,
        file_content: typing.IO[bytes],
        input_extension: str,
        cache_path: str,
        output_filepath: str,
        mimetype: str
    ) -> BytesIO:

        """
        abstract function to transform a file given in bytes to pdf
        :param file_content: stream
        :param input_extension: str
        :param cache_path: str
        :param output_filepath: str
        """

        raise NotImplementedError

    def _cache_file_process_already_running(self, file_name: str) -> bool:
        if os.path.exists(file_name + '_flag'):
            return True
        else:
            return False

    def build_jpeg_preview(
        self,
        file_path: str,
        preview_name: str,
        cache_path: str,
        page_id: int,
        extension: str='.jpg',
        size: ImgDims=None,
        mimetype: str='',
        attempt: int=0
    ) -> None:

        cache_file = os.path.join(cache_path, preview_name)

        if self._cache_file_process_already_running(cache_file):
            # Note - 10-10-2018 - Basile - infinite recursion protection
            if attempt >= 5:
                raise PreviewGeneratorException(
                    'Max attempts exceeded aborting preview'
                )
            attempt += 1
            time.sleep(2)
            return self.build_jpeg_preview(
                file_path=file_path, preview_name=preview_name,
                cache_path=cache_path, extension=extension, page_id=page_id,
                size=size, attempt=attempt, mimetype=mimetype
            )

        input_pdf_stream = None
        if os.path.exists(os.path.join(cache_path, preview_name + '.pdf')):
            input_pdf_stream = open(
                os.path.join(cache_path, preview_name + '.pdf'), 'rb'
            )

        if not input_pdf_stream:
            with open(file_path, 'rb') as _file:
                file, file_extension = os.path.splitext(file_path)
                output_path = os.path.join(cache_path, preview_name)
                input_pdf_stream = self._convert_to_pdf(
                    _file, file_extension, cache_path, output_path, mimetype
                )

        input_pdf = PdfFileReader(input_pdf_stream)
        intermediate_pdf = PdfFileWriter()
        intermediate_pdf.addPage(input_pdf.getPage(int(page_id)))

        intermediate_pdf_stream = BytesIO()
        intermediate_pdf.write(intermediate_pdf_stream)
        intermediate_pdf_stream.seek(0, 0)
        jpeg_stream = convert_pdf_to_jpeg(intermediate_pdf_stream, size)

        jpeg_preview_path = os.path.join(cache_path, preview_name + extension)
        with open(jpeg_preview_path, 'wb') as jpeg_output_stream:
            buffer = jpeg_stream.read(1024)
            while buffer:
                jpeg_output_stream.write(buffer)
                buffer = jpeg_stream.read(1024)

    def build_pdf_preview(
        self,
        file_path: str,
        preview_name: str,
        cache_path: str,
        extension: str = '.pdf',
        page_id: int = -1,
        mimetype: str = ''
    ) -> None:

        intermediate_pdf_filename = preview_name.split('-page')[0] + '.pdf'
        intermediate_pdf_file_path = os.path.join(
            cache_path,
            intermediate_pdf_filename
        )

        if not os.path.exists(intermediate_pdf_file_path):
            if os.path.exists(intermediate_pdf_file_path + '_flag'):
                # Wait 2 seconds, then retry
                # Info - B.L - 2018/09/28 - Protection for concurent file access
                # If two person try to preview the same file one will override the file
                # while the other is reading it.
                time.sleep(2)
                return self.build_pdf_preview(
                    file_path=file_path,
                    preview_name=preview_name,
                    cache_path=cache_path,
                    extension=extension,
                    page_id=page_id,
                    mimetype=mimetype
                )

            with open(file_path, 'rb') as input_stream:
                input_extension = os.path.splitext(file_path)[1]
                # first step is to convert full document to full pdf
                self._convert_to_pdf(
                    file_content=input_stream,
                    input_extension=input_extension,
                    cache_path=cache_path,
                    output_filepath=intermediate_pdf_file_path,
                    mimetype=mimetype
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

    def get_page_number(
        self,
        file_path: str,
        preview_name: str,
        cache_path: str,
        mimetype: typing.Optional[str] = None,
    ) -> int:

        page_nb_file_path = cache_path + preview_name + '_page_nb'

        if not os.path.exists(page_nb_file_path):
            pdf_version_filepath = cache_path + preview_name + '.pdf'
            if not os.path.exists(pdf_version_filepath):
                self.build_pdf_preview(
                    file_path=file_path,
                    preview_name=preview_name,
                    cache_path=cache_path,
                    mimetype=mimetype,
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
) -> None:
    with open(output_filepath, 'wb') as temporary_file:
        file_content.seek(0, 0)
        buffer = file_content.read(1024)
        while buffer:
            temporary_file.write(buffer)
            buffer = file_content.read(1024)
