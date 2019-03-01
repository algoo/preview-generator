# coding: utf-8

from io import BytesIO
import typing
import os

from pikepdf import Pdf


from preview_generator.preview.generic_preview import PreviewBuilder
from preview_generator import utils
from preview_generator.preview.builder.image__wand import convert_pdf_to_jpeg


class PreviewBuilderPikePDF(PreviewBuilder):

    @classmethod
    def get_label(cls) -> str:
        return 'PDF documents - based on pikepdf'

    @classmethod
    def get_supported_mimetypes(cls) -> typing.List[str]:
        return ['application/pdf']

    def build_jpeg_preview(
            self,
            file_path: str,
            preview_name: str,
            cache_path: str,
            page_id: int,
            extension: str = '.jpg',
            size: utils.ImgDims = utils.ImgDims(256, 256),
            mimetype: str=''
    ) -> None:
        """
        generate the pdf small preview
        """

        input_pdf = Pdf.open(file_path)
        output_pdf = Pdf.new()
        output_stream = BytesIO()

        output_pdf.pages.append(input_pdf.pages[page_id])
        output_pdf.save(output_stream)
        output_stream.seek(0, 0)

        result = convert_pdf_to_jpeg(output_stream, size)
        preview_path = os.path.join(cache_path, preview_name + extension)
        with open(preview_path, 'wb') as jpeg:
            buffer = result.read(1024)
            while buffer:
                jpeg.write(buffer)
                buffer = result.read(1024)

    def build_pdf_preview(
            self,
            file_path: str,
            preview_name: str,
            cache_path: str,
            extension: str = '.pdf',
            page_id: int = -1,
            mimetype: str = ''
    ) -> None:
        input_pdf = Pdf.open(file_path)

        if page_id and page_id > -1:
            output_pdf = Pdf.new()
            output_pdf.pages.append(input_pdf.pages[page_id])
        else:
            output_pdf = input_pdf

        preview_path = os.path.join(cache_path, preview_name + extension)
        output_pdf.save(preview_path)

    def get_page_number(
            self, file_path: str,
            preview_name: str,
            cache_path: str,
            mimetype: typing.Optional[str] = None,
    ) -> int:
        preview_count_path = os.path.join(
            cache_path, preview_name + '_page_nb'
        )
        try:
            count_file = open(preview_count_path, 'r')
        except IOError:
            count_file = open(preview_count_path, 'w')
            count_file.write(len(Pdf.open(file_path).pages))

        page_count = count_file.read()
        count_file.close()
        return int(page_count)

    def has_jpeg_preview(self):
        return True

    def has_pdf_preview(self):
        return True
