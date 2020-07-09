# -*- coding: utf-8 -*-
import tempfile
import typing
import zipfile

from preview_generator.preview.builder.image__pillow import ImagePreviewBuilderPillow  # nopep8
from preview_generator.preview.generic_preview import PreviewBuilder
from preview_generator.utils import ImgDims
from preview_generator.utils import MimetypeMapping


class ImagePreviewBuilderSketch(PreviewBuilder):
    SKETCH_MIMETYPES_MAPPING = [MimetypeMapping("application/sketch", ".sketch")]

    @classmethod
    def get_label(cls) -> str:
        return "Images generator from sketch files"

    @classmethod
    def get_supported_mimetypes(cls) -> typing.List[str]:
        mimetypes = []
        for mimetype_mapping in cls.get_mimetypes_mapping():
            mimetypes.append(mimetype_mapping.mimetype)
        return mimetypes

    @classmethod
    def get_mimetypes_mapping(cls) -> typing.List[MimetypeMapping]:
        return cls.SKETCH_MIMETYPES_MAPPING

    def build_jpeg_preview(
        self,
        file_path: str,
        preview_name: str,
        cache_path: str,
        page_id: int,
        extension: str = ".jpg",
        size: ImgDims = None,
        mimetype: str = "",
    ) -> None:
        if not size:
            size = self.default_size
        with tempfile.TemporaryDirectory(prefix="preview-generator-") as tmp_dir:
            with open(file_path, "rb") as filestream:
                zip = zipfile.ZipFile(filestream)
                zip.extract("previews/preview.png", tmp_dir)
                zip.close()

                ImagePreviewBuilderPillow().build_jpeg_preview(
                    tmp_dir + "/previews/preview.png",
                    preview_name,
                    cache_path,
                    page_id,
                    extension,
                    size,
                    mimetype,
                )

    def has_jpeg_preview(self) -> bool:
        return True

    def get_page_number(
        self, file_path: str, preview_name: str, cache_path: str, mimetype: str = ""
    ) -> int:
        return 1
