# -*- coding: utf-8 -*-

import contextlib
from io import BytesIO
import os
from pathlib import Path
import time
import typing

from PyPDF2 import PdfFileWriter
from PyPDF2.utils import b_

from preview_generator import utils
from preview_generator.exception import BuilderDependencyNotFound
from preview_generator.exception import PreviewAbortedMaxAttempsExceeded
from preview_generator.preview.generic_preview import PreviewBuilder
from preview_generator.utils import executable_is_available


class DocumentPreviewBuilder(PreviewBuilder):
    def _convert_to_pdf(
        self,
        file_content: typing.IO[bytes],
        input_extension: str,
        cache_path: str,
        output_filepath: str,
        mimetype: str,
    ) -> BytesIO:

        """
        abstract function to transform a file given in bytes to pdf
        :param file_content: stream
        :param input_extension: str
        :param cache_path: str
        :param output_filepath: str
        """

        raise NotImplementedError

    @classmethod
    def check_dependencies(cls) -> None:
        if not executable_is_available("qpdf"):
            raise BuilderDependencyNotFound("this builder requires qpdf to be available")

    def _cache_file_process_already_running(self, file_name: str) -> bool:
        if os.path.exists(file_name + "_flag"):
            return True
        else:
            return False

    def build_jpeg_preview(
        self,
        file_path: str,
        preview_name: str,
        cache_path: str,
        page_id: int,
        extension: str = ".jpg",
        size: utils.ImgDims = None,
        mimetype: str = "",
        attempt: int = 0,
    ) -> None:
        raise NotImplementedError(
            "Convert to pdf first and use intermediate file to" "generate the jpeg preview."
        )

    def build_pdf_preview(
        self,
        file_path: str,
        preview_name: str,
        cache_path: str,
        extension: str = ".pdf",
        page_id: int = -1,
        mimetype: str = "",
        attempt: int = 0,
    ) -> None:

        intermediate_pdf_filename = preview_name.split("-page")[0] + ".pdf"
        intermediate_pdf_file_path = os.path.join(cache_path, intermediate_pdf_filename)

        if not os.path.exists(intermediate_pdf_file_path):
            if os.path.exists(intermediate_pdf_file_path + "_flag"):
                # Wait 2 seconds, then retry
                # Info - B.L - 2018/09/28 - Protection for concurent file access
                # If two person try to preview the same file one will override the file
                # while the other is reading it.
                if attempt >= 5:
                    raise PreviewAbortedMaxAttempsExceeded("Max attempts exceeded aborting preview")
                attempt += 1
                time.sleep(2)
                return self.build_pdf_preview(
                    file_path=file_path,
                    preview_name=preview_name,
                    cache_path=cache_path,
                    extension=extension,
                    page_id=page_id,
                    mimetype=mimetype,
                    attempt=attempt,
                )

            with open(file_path, "rb") as input_stream:
                input_extension = os.path.splitext(file_path)[1]
                # first step is to convert full document to full pdf
                self._convert_to_pdf(
                    file_content=input_stream,
                    input_extension=input_extension,
                    cache_path=cache_path,
                    output_filepath=intermediate_pdf_file_path,
                    mimetype=mimetype,
                )

        if page_id < 0:
            return  # in this case, the intermediate file is the requested one

        pdf_out = PdfFileWriter()
        with open(intermediate_pdf_file_path, "rb") as pdf_stream:
            # HACK - G.M - 2020-08-19 - Transform stream in a way pypdf2 can handle it
            # this should be removed with a future pdf builder.
            stream = BytesIO(b_(pdf_stream.read()))
            pdf_in = utils.get_decrypted_pdf(stream)
            output_file_path = os.path.join(cache_path, "{}{}".format(preview_name, extension))
            pdf_out.addPage(pdf_in.getPage(page_id))

        with open(output_file_path, "wb") as output_file:
            pdf_out.write(output_file)

    def get_page_number(
        self, file_path: str, preview_name: str, cache_path: str, mimetype: str = ""
    ) -> int:
        raise NotImplementedError(
            "Convert to pdf first and use intermediate file to generate the page number."
        )

    def has_pdf_preview(self) -> bool:
        """
        Override and return True if your builder allow PDF preview
        :return:
        """
        return True

    def has_jpeg_preview(self) -> bool:
        """
        Override and return True if your builder allow jpeg preview
        """
        return True


@contextlib.contextmanager
def create_flag_file(filepath: str) -> typing.Generator[str, None, None]:
    """
    Create a flag file in order to avoid concurrent build of same previews
    :param filepath: file to protect
    :return: flag file path
    """
    flag_file_path = Path("{}_flag".format(filepath))
    flag_file_path.touch()
    try:
        yield str(flag_file_path)
    finally:
        flag_file_path.unlink()


def write_file_content(file_content: typing.IO[bytes], output_filepath: str) -> None:
    with open(output_filepath, "wb") as temporary_file:
        file_content.seek(0, 0)
        buffer = file_content.read(1024)
        while buffer:
            temporary_file.write(buffer)
            buffer = file_content.read(1024)
