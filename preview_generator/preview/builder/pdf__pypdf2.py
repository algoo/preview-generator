# -*- coding: utf-8 -*-

from io import BytesIO
import os
import typing

from PyPDF2 import PdfFileWriter
from pdf2image import convert_from_bytes

from preview_generator import utils
from preview_generator.exception import BuilderDependencyNotFound
from preview_generator.preview.generic_preview import PreviewBuilder
from preview_generator.utils import ImgDims
from preview_generator.utils import compute_resize_dims
from preview_generator.utils import executable_is_available


def convert_pdf_to_jpeg(pdf: typing.IO[bytes], preview_size: ImgDims) -> BytesIO:

    pdf_content = pdf.read()
    images = convert_from_bytes(pdf_content)

    output = BytesIO()
    for image in images:
        resize_dims = compute_resize_dims(ImgDims(image.width, image.height), preview_size)
        resized = image.resize((resize_dims.width, resize_dims.height), resample=True)
        resized.save(output, format="JPEG")

    output.seek(0, 0)
    return output


class PdfPreviewBuilderPyPDF2(PreviewBuilder):
    @classmethod
    def get_label(cls) -> str:
        return "PDF documents - based on PyPDF2"

    @classmethod
    def check_dependencies(cls) -> None:
        if not executable_is_available("qpdf"):
            raise BuilderDependencyNotFound("this builder requires qpdf to be available")

    @classmethod
    def get_supported_mimetypes(cls) -> typing.List[str]:
        return ["application/pdf"]

    def build_jpeg_preview(
        self,
        file_path: str,
        preview_name: str,
        cache_path: str,
        page_id: int,
        extension: str = ".jpg",
        size: utils.ImgDims = None,
        mimetype: str = "",
    ) -> None:
        """
        generate the pdf small preview
        """
        if not size:
            size = self.default_size

        with open(file_path, "rb") as pdf:
            # HACK - D.A. - 2017-08-11 Deactivate strict mode
            # This avoid crashes when PDF are not standard
            # See https://github.com/mstamy2/PyPDF2/issues/244
            input_pdf = utils.get_decrypted_pdf(pdf, strict=False)
            output_pdf = PdfFileWriter()
            output_pdf.addPage(input_pdf.getPage(int(page_id)))
            output_stream = BytesIO()
            output_pdf.write(output_stream)
            output_stream.seek(0, 0)
            result = convert_pdf_to_jpeg(output_stream, size)

            preview_path = "{path}{file_name}{extension}".format(
                file_name=preview_name, path=cache_path, extension=extension
            )
            with open(preview_path, "wb") as jpeg:
                buffer = result.read(1024)
                while buffer:
                    jpeg.write(buffer)
                    buffer = result.read(1024)

    def build_pdf_preview(
        self,
        file_path: str,
        preview_name: str,
        cache_path: str,
        extension: str = ".pdf",
        page_id: int = -1,
        mimetype: str = "",
    ) -> None:
        """
        generate the pdf large preview
        """

        with open(file_path, "rb") as pdf:

            input_pdf = utils.get_decrypted_pdf(pdf)
            output_pdf = PdfFileWriter()
            if page_id is None or page_id <= -1:
                for i in range(input_pdf.numPages):
                    output_pdf.addPage(input_pdf.getPage(i))
            else:
                output_pdf.addPage(input_pdf.getPage(int(page_id)))
            output_stream = BytesIO()
            output_pdf.write(output_stream)
            output_stream.seek(0, 0)

            preview_path = "{path}{file_name}{extension}".format(
                file_name=preview_name, path=cache_path, extension=extension
            )

            with open(preview_path, "wb") as jpeg:
                buffer = output_stream.read(1024)
                while buffer:
                    jpeg.write(buffer)
                    buffer = output_stream.read(1024)

    def get_page_number(
        self,
        file_path: str,
        preview_name: str,
        cache_path: str,
        mimetype: typing.Optional[str] = None,
    ) -> int:
        if not os.path.exists(cache_path + preview_name + "_page_nb"):
            with open(cache_path + preview_name + "_page_nb", "w") as count:
                count.seek(0, 0)
                with open(file_path, "rb") as doc:
                    inputpdf = utils.get_decrypted_pdf(doc)
                    num_page = inputpdf.numPages
                    count.write(str(num_page))
                    return int(num_page)
        else:
            with open(cache_path + preview_name + "_page_nb", "r") as count:
                count.seek(0, 0)
                return int(count.read())

    def has_jpeg_preview(self) -> bool:
        return True

    def has_pdf_preview(self) -> bool:
        return True
