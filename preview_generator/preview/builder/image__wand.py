# -*- coding: utf-8 -*-
import os
import typing

from wand.image import Image
import wand.version
from wand.color import Color

from preview_generator.preview.generic_preview import ImagePreviewBuilder
from preview_generator.utils import ImgDims
from preview_generator.utils import imagemagick_supported_mimes
from preview_generator.utils import compute_resize_dims

DEFAULT_JPEG_QUALITY = 85
DEFAULT_JPEG_PROGRESSIVE = True


class ImagePreviewBuilderWand(ImagePreviewBuilder):

    weight = 40
    MIMETYPES = []  # type: typing.List[str]

    def __init__(
        self,
        quality: int = DEFAULT_JPEG_QUALITY,
        progressive: bool = DEFAULT_JPEG_PROGRESSIVE,
    ):
        super().__init__()
        self.quality = quality
        self.progressive = progressive

    @classmethod
    def get_label(cls) -> str:
        return "Images - based on WAND (image magick)"

    @classmethod
    def dependencies_versions(cls) -> typing.Optional[str]:
        return "wand {} from {}".format(wand.version.VERSION, ", ".join(wand.__path__))

    @classmethod
    def __load_mimetypes(cls) -> typing.List[str]:
        """
        Load supported mimetypes from WAND library
        :return: list of supported mime types
        """
        return imagemagick_supported_mimes()

    @classmethod
    def get_supported_mimetypes(cls) -> typing.List[str]:
        """
        :return: list of supported mime types
        """
        if len(ImagePreviewBuilderWand.MIMETYPES) == 0:
            ImagePreviewBuilderWand.MIMETYPES = cls.__load_mimetypes()
        mimetypes = ImagePreviewBuilderWand.MIMETYPES

        extra_mimetypes = ["application/x-xcf", "image/x-xcf"]
        mimetypes.extend(extra_mimetypes)

        return mimetypes

    def build_jpeg_preview(
        self,
        file_path: str,
        preview_name: str,
        cache_path: str,
        page_id: int,
        extension: str = ".jpeg",
        size: ImgDims = None,
        mimetype: str = "",
    ) -> None:
        if not size:
            size = self.default_size
        preview_name = preview_name + extension
        dest_path = os.path.join(cache_path, preview_name)
        self.image_to_jpeg_wand(file_path, size, dest_path)

    def image_to_jpeg_wand(
        self,
        file_path: str,
        preview_dims: ImgDims,
        dest_path: str,
    ) -> None:
        with Image(filename=file_path) as img:
            # https://legacy.imagemagick.org/Usage/thumbnails/
            img.auto_orient()
            img.background_color = Color("white")
            img.merge_layers("flatten")

            if self.progressive:
                img.interlace_scheme = "plane"

            img.compression_quality = self.quality

            resize_dim = compute_resize_dims(
                dims_in=ImgDims(width=img.width, height=img.height), dims_out=preview_dims
            )
            img.thumbnail(resize_dim.width, resize_dim.height)

            img.save(filename=dest_path)
