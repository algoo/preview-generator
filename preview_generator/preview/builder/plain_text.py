# -*- coding: utf-8 -*-

import typing

from preview_generator import file_converter
from preview_generator.preview.builder.office__libreoffice import OfficePreviewBuilderLibreoffice  # nopep8


class PlainTextPreviewBuilder(OfficePreviewBuilderLibreoffice):
    @classmethod
    def get_supported_mimetypes(cls) -> typing.List[str]:
        return [
            'text/plain',
            'text/html',
            'application/xml',
            'application/javascript'
        ]

    def build_text_preview(self, file_path: str, preview_name: str,
                           cache_path: str, page_id: int = 0,
                           extension: str = '.txt') -> None:
        """
        generate the text preview
        """
        with open(file_path, 'rb') as txt:
            result = file_converter.txt_to_txt(
                txt)  # type: typing.IO[typing.Any]
            with open('{path}{extension}'.format(
                    path=cache_path + preview_name,
                    extension=extension
            ),
                    'wb') as jpeg:
                buffer = result.read(1024)
                while buffer:
                    jpeg.write(buffer)
                    buffer = result.read(1024)
