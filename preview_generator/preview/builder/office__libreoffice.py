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

from preview_generator.preview.generic_preview import PreviewBuilder
from preview_generator.utils import ImgDims
from preview_generator.preview.builder.image__wand import convert_pdf_to_jpeg


class OfficePreviewBuilderLibreoffice(PreviewBuilder):
    mimetype = [
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.oasis.opendocument.text',
        'application/vnd.oasis.opendocument.spreadsheet',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # nopep8
        'application/vnd.openxmlformats-officedocument.wordprocessingml.template',  # nopep8
        'application/vnd.ms-word.document.macroEnabled.12',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.template',
        'application/vnd.ms-excel.sheet.macroEnabled.12',
        'application/vnd.ms-excel.template.macroEnabled.12',
        'application/vnd.ms-excel.addin.macroEnabled.12',
        'application/vnd.ms-excel.sheet.binary.macroEnabled.12',
        'application/vnd.ms-powerpoint',
        'application/vnd.openxmlformats-fficedocument.presentationml.presentation',  # nopep8
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

    def build_jpeg_preview(self, file_path: str, preview_name: str,
                           cache_path: str, page_id: int,
                           extension: str = '.jpg',
                           size: ImgDims=None) -> None:
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
                    result = convert_office_document_to_pdf(
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
            result2 = convert_pdf_to_jpeg(output_stream, size)

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
                          cache_path: str, extension: str = '.pdf',
                          page_id: int = 0) -> None:
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
                    result = convert_office_document_to_pdf(odt, cache_path,
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

    # def _pdf_to_jpeg(
    #         self,
    #         pdf: typing.Union[str, typing.IO[bytes]],
    #         preview_size: ImgDims
    # ) -> BytesIO:
    #
    #     logging.info('Converting pdf to jpeg')
    #
    #     with WImage(file=pdf) as img:
    #         height, width = img.size
    #         if height < width:
    #             breadth = height
    #         else:
    #             breadth = width
    #         with WImage(
    #                 width=breadth,
    #                 height=breadth,
    #                 background=Color('white')
    #         ) as image:
    #             image.composite(
    #                 img,
    #                 top=0,
    #                 left=0
    #             )
    #             image.crop(0, 0, width=breadth, height=breadth)
    #
    #             from preview_generator.utils import compute_resize_dims
    #             from preview_generator.utils import compute_crop_dims
    #
    #             resize_dims = compute_resize_dims(
    #                 ImgDims(image.width, image.height),
    #                 preview_size
    #             )
    #
    #             image.resize(resize_dims.width, resize_dims.height)
    #
    #             crop_dims = compute_crop_dims(
    #                 ImgDims(image.width, image.height),
    #                 preview_size
    #             )
    #             image.crop(
    #                 crop_dims.left,
    #                 crop_dims.top,
    #                 crop_dims.right,
    #                 crop_dims.bottom
    #             )
    #             content_as_bytes = image.make_blob('jpeg')
    #             output = BytesIO()
    #             output.write(content_as_bytes)
    #             output.seek(0, 0)
    #             return output
    #
    #             # b, a = image.size
    #             # x, y = preview_size.width, preview_size.height
    #             # size_rate = (a / b) / (x / y)
    #             # if size_rate > 1:
    #             #     a = int(a * (y / b))
    #             #     b = int(b * (y / b))
    #             # else:
    #             #     b = int(b * (x / a))
    #             #     a = int(a * (x / a))
    #             # image.resize(b, a)
    #             # left = int((b / 2) - (y / 2))
    #             # top = int((a / 2) - (x / 2))
    #             # width = left + y
    #             # height = top + x
    #             # image.crop(left, top, width, height)
    #             # content_as_bytes = image.make_blob('jpeg')
    #             # output = BytesIO()
    #             # output.write(content_as_bytes)
    #             # output.seek(0, 0)
    #             # return output
    #             #


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
