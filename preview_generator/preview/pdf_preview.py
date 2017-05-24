from io import BytesIO

import typing
from PyPDF2 import PdfFileReader
from PyPDF2 import PdfFileWriter

from preview_generator import file_converter
from preview_generator.preview.generic_preview import PreviewBuilder


class PdfPreviewBuilder(PreviewBuilder):
    mimetype = ['application/pdf']

    def build_jpeg_preview(self, file_path: str, preview_name: str,
                           cache_path: str, page_id: int,
                           extension: str = '.jpg',
                           size: typing.Tuple[int, int] = (256, 256)) -> None:
        """
        generate the pdf small preview
        """

        with open(file_path, 'rb') as pdf:
            input_pdf = PdfFileReader(pdf)
            output_pdf = PdfFileWriter()
            output_pdf.addPage(input_pdf.getPage(int(page_id)))
            output_stream = BytesIO()
            output_pdf.write(output_stream)
            output_stream.seek(0, 0)
            result = file_converter.pdf_to_jpeg(output_stream, size)

            if page_id == -1:
                preview_path = '{path}{file_name}{extension}'.format(
                    file_name=preview_name,
                    path=cache_path,
                    extension=extension
                )
            else:
                preview_path = '{path}{file_name}{extension}'.format(
                    file_name=preview_name,
                    path=cache_path,
                    page_id=page_id,
                    extension=extension
                )
            with open(preview_path, 'wb') as jpeg:
                buffer = result.read(1024)
                while buffer:
                    jpeg.write(buffer)
                    buffer = result.read(1024)

    def get_page_number(self, file_path: str, preview_name: str,
                        cache_path: str) -> int:
        with open(cache_path + preview_name + '_page_nb', 'w') as count:
            count.seek(0, 0)

            with open(file_path, 'rb') as doc:
                inputpdf = PdfFileReader(doc)
                count.write(str(inputpdf.numPages))
        with open(cache_path + preview_name + '_page_nb', 'r') as count:
            count.seek(0, 0)
            return count.read()
