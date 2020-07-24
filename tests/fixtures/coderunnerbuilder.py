# -*- coding: utf-8 -*-

"""
This is a test preview generator builder.
It executes the given file as a python code. The generated preview text contains
the output of this code.
This is unsafe and it should not be used in production.
To enable this builder, put it in the builder folder.
"""

import sys
import typing

from preview_generator.preview.generic_preview import PreviewBuilder
from preview_generator.utils import MimetypeMapping


class CodeRunnerPreviewBuilder(PreviewBuilder):
    @classmethod
    def get_label(cls) -> str:
        return "Plain text files"

    @classmethod
    def get_supported_mimetypes(cls) -> typing.List[str]:
        return ["application/x-preview-generator-test"]

    @classmethod
    def get_mimetypes_mapping(cls) -> typing.List[MimetypeMapping]:
        return [MimetypeMapping("application/x-preview-generator-test", ".runpy")]

    def build_text_preview(
        self,
        file_path: str,
        preview_name: str,
        cache_path: str,
        page_id: int = 0,
        extension: str = ".runpy",
    ) -> None:
        """
        generate the text preview
        """
        original_stdout = sys.stdout
        sys.stdout = open(cache_path + preview_name + extension, "w")
        with open(file_path, "rb") as f:
            exec(f.read())
        sys.stdout.close()
        sys.stdout = original_stdout

    def has_text_preview(self) -> bool:
        return True
