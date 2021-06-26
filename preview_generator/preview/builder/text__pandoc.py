import typing

import pypandoc

from preview_generator import utils
from preview_generator.preview.builder.document_generic import DocumentPreviewBuilder
from preview_generator.preview.generic_preview import PreviewBuilder
from preview_generator.utils import MimetypeMapping


class PandocTextPreviewBuilder(DocumentPreviewBuilder):
    weight = 55

    FORMAT_CONVERTION_TABLE = {
        'text/markdown' : "markdown",
        'text/x-latex': 'latex'
    }
    @classmethod
    def get_label(cls) -> str:
        return "Plain text files using pandoc"

    @classmethod
    def get_supported_mimetypes(cls) -> typing.List[str]:
        # TODO: VERIFY mimetypes
        LIGHWEIGHT_MARKUP_FORMATS = [
            "text/plain",
            "text/markdown",
            "text/x-rst",
            "text/org",
            "text/asciidoc",
        ]
        COMPLEX_MARKUP_FORMAT = [
            "text/html",
            "application/epub+zip",
            "application/x-ipynb+json"
        ]
        OFFICE_FORMATS = [
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.oasis.opendocument.text",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        ]
        return LIGHWEIGHT_MARKUP_FORMATS + COMPLEX_MARKUP_FORMAT + OFFICE_FORMATS

    @classmethod
    def get_mimetypes_mapping(cls) -> typing.List[MimetypeMapping]:
        return [
            MimetypeMapping("text/plain", ".txt"),
            MimetypeMapping("text/x-rst", ".rst"),
            MimetypeMapping("text/org", ".org"),
            MimetypeMapping("text/asciidoc", ".asciidoc"),
            MimetypeMapping("text/html", ".html"),
            MimetypeMapping("application/epub+zip", ".epub"),
            MimetypeMapping("text/markdown", ".md"),
            MimetypeMapping("application/x-ipynb+json",".ipynb")
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
        pypandoc.convert_file(
            source_file=file_path,
            outputfile=output_filepath,
            format=self.FORMAT_CONVERTION_TABLE.get(mimetype),
            to="html",
            extra_args=['-s', '--pdf-engine=weasyprint']
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
