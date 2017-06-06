import os
import time
from io import BytesIO

import typing
from PyPDF2 import PdfFileReader
from PyPDF2 import PdfFileWriter

from preview_generator import file_converter
from preview_generator.preview.generic_preview import PreviewBuilder


class OfficePreviewBuilder(PreviewBuilder):
    mimetype = [
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.oasis.opendocument.text',
        'application/vnd.oasis.opendocument.spreadsheet',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.template',
        'application/vnd.ms-word.document.macroEnabled.12',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.template',
        'application/vnd.ms-excel.sheet.macroEnabled.12',
        'application/vnd.ms-excel.template.macroEnabled.12',
        'application/vnd.ms-excel.addin.macroEnabled.12',
        'application/vnd.ms-excel.sheet.binary.macroEnabled.12',
        'application/vnd.ms-powerpoint',
        'application/vnd.openxmlformats-fficedocument.presentationml.presentation',
        'application/vnd.openxmlformats-officedocument.presentationml.template',
        'application/vnd.openxmlformats-officedocument.presentationml.slideshow',
        'application/vnd.ms-powerpoint.addin.macroEnabled.12',
        'application/vnd.ms-powerpoint.presentation.macroEnabled.12',
        'application/vnd.ms-powerpoint.template.macroEnabled.12',
        'application/vnd.ms-powerpoint.slideshow.macroEnabled.12',
        'application/vnd.oasis.opendocument.spreadsheet',
        'application/vnd.oasis.opendocument.text',
        ' application/vnd.oasis.opendocument.text-template',
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

    def build_jpeg_preview(self, file_path: str, preview_name: str,
                           cache_path: str, page_id: int,
                           extension: str = '.jpg',
                           size: typing.Tuple[int, int] = (256, 256)) -> None:
        """
        generate the text preview
        """

        with open(file_path, 'rb') as odt:
            if os.path.exists(
                    '{path}{file_name}.pdf'.format(
                        path=cache_path,
                        file_name=preview_name
                    )):
                result = open(
                    '{path}.pdf'.format(
                        path=cache_path + preview_name,
                    ), 'rb')

            else:
                if self.cache_file_process_already_running(
                                cache_path + preview_name):
                    time.sleep(2)
                    self.build_jpeg_preview(
                        file_path=file_path,
                        preview_name=preview_name,
                        cache_path=cache_path,
                        extension=extension,
                        page_id=page_id
                    )

                else:
                    result = file_converter.office_to_pdf(
                        odt,
                        cache_path,
                        preview_name
                    )

            input_pdf = PdfFileReader(result)
            output_pdf = PdfFileWriter()
            output_pdf.addPage(input_pdf.getPage(int(page_id)))
            output_stream = BytesIO()
            output_pdf.write(output_stream)
            output_stream.seek(0, 0)
            result2 = file_converter.pdf_to_jpeg(output_stream, size)

            preview_path = '{path}{file_name}{extension}'.format(
                file_name=preview_name,
                path=cache_path,
                extension=extension
            )

            with open(preview_path, 'wb') as jpeg:
                buffer = result2.read(1024)
                while buffer:
                    jpeg.write(buffer)
                    buffer = result2.read(1024)

    def get_page_number(self, file_path: str, preview_name: str,
                        cache_path: str) -> int:

        if not os.path.exists(cache_path + preview_name + '.pdf'):
            self.build_pdf_preview(
                file_path=file_path,
                preview_name=preview_name,
                cache_path=cache_path,
                extension='.pdf'
            )

        with open(cache_path + preview_name + '_page_nb', 'w') as count:
            count.seek(0, 0)
            if not os.path.exists(cache_path + preview_name + '.pdf'):
                self.build_pdf_preview(file_path, preview_name, cache_path)

            with open(cache_path + preview_name + '.pdf', 'rb') as doc:
                inputpdf = PdfFileReader(doc)
                count.write(str(inputpdf.numPages))
        with open(cache_path + preview_name + '_page_nb', 'r') as count:
            count.seek(0, 0)
            page_nb = count.read()
            return int(page_nb)

    def build_pdf_preview(self, file_path: str, preview_name: str,
                          cache_path: str, extension: str = '.pdf') -> None:
        """
        generate the pdf large preview
        """

        with open(file_path, 'rb') as odt:

            if os.path.exists('{path}.pdf'.format(
                    path=cache_path + preview_name,
            )):
                result = open('{path}.pdf'.format(
                    path=cache_path + preview_name,
                ), 'rb')

            else:
                if os.path.exists(cache_path + preview_name + '_flag'):
                    time.sleep(2)
                    self.build_pdf_preview(
                        file_path=file_path,
                        preview_name=preview_name,
                        cache_path=cache_path,
                        extension=extension)
                else:
                    result = file_converter.office_to_pdf(odt, cache_path,
                                                          preview_name)

            with open(cache_path + preview_name + extension, 'wb') as pdf:
                buffer = result.read(1024)
                while buffer:
                    pdf.write(buffer)
                    buffer = result.read(1024)

    def cache_file_process_already_running(self, file_name: str) -> bool:
        if os.path.exists(file_name + '_flag'):
            return True
        else:
            return False
