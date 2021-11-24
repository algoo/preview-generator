# -*- coding: utf-8 -*-

from abc import ABC
import contextlib
from io import BytesIO
import os
from pathlib import Path
import time
import typing

from preview_generator import utils
from preview_generator.exception import PreviewAbortedMaxAttempsExceeded
from preview_generator.preview.builder.pdf__poppler_utils import PdfPreviewBuilderPopplerUtils
from preview_generator.preview.generic_preview import PreviewBuilder


class DocumentPreviewBuilder(PreviewBuilder, ABC):
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
        PdfPreviewBuilderPopplerUtils().check_dependencies()

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

        # TODO - G.M - 2021-10-21 Refactor this part with a lock and consider splitting
        # full and simple page pdf to make intermediate file preview easier.
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

        PdfPreviewBuilderPopplerUtils().build_pdf_preview(
            file_path=intermediate_pdf_file_path,
            preview_name=preview_name,
            cache_path=cache_path,
            page_id=page_id,
            extension=extension,
        )

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
