import subprocess
import typing

import pygments.cmdline
import weasyprint

from preview_generator import utils
from preview_generator.preview.builder.document_generic import DocumentPreviewBuilder
from preview_generator.utils import MimetypeMapping


class PandocTextPreviewBuilder(DocumentPreviewBuilder):
    weight = 75

    @classmethod
    def get_label(cls) -> str:
        return "code text files using code2pdf lib"

    @classmethod
    def get_supported_mimetypes(cls) -> typing.List[str]:
        # TODO: VERIFY mimetypes
        CODE_FORMATS = [
            'text/x-python'
        ]
        return CODE_FORMATS

    @classmethod
    def get_mimetypes_mapping(cls) -> typing.List[MimetypeMapping]:
        return [
        ]

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

    def _convert_to_pdf(
        self,
        file_content: typing.IO[bytes],
        file_path: str,
        input_extension: str,  # example: '.dxf'
        cache_path: str,
        output_filepath: str,
        mimetype: str,
    ) -> None:
        temp_html_file = "{}{}".format(output_filepath,'.html')
        subprocess.check_call(
            ['pygmentize', '-f', 'html',  '-O', 'full,style=tango', '-o', temp_html_file, file_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )
        from weasyprint import HTML
        css = weasyprint.CSS(string='@page { size: A3; margin: 1cm }')
        HTML(temp_html_file).write_pdf(output_filepath, stylesheets=[css])

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
