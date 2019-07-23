# -*- coding: utf-8 -*-

import typing

from preview_generator.preview.builder.office__libreoffice import OfficePreviewBuilderLibreoffice


class PlainTextPreviewBuilder(OfficePreviewBuilderLibreoffice):
    @classmethod
    def get_label(cls) -> str:
        return "Plain text files"

    @classmethod
    def get_supported_mimetypes(cls) -> typing.List[str]:
        return [
            "text/plain",
            "text/html",
            "text/xml",  # Info - B.L - Compatibility between debian and ubuntu
            "application/xml",
            "application/javascript",
        ]

    def build_text_preview(
        self,
        file_path: str,
        preview_name: str,
        cache_path: str,
        page_id: int = 0,
        extension: str = ".txt",
    ) -> None:
        """
        generate the text preview
        """
        with open(file_path, "rb") as txt:
            with open(
                "{path}{extension}".format(path=cache_path + preview_name, extension=extension),
                "wb",
            ) as output_text:
                buffer = txt.read(1024)
                while buffer:
                    output_text.write(buffer)
                    buffer = txt.read(1024)

    def has_text_preview(self) -> bool:
        return True
