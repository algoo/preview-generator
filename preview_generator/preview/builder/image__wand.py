# -*- coding: utf-8 -*-
import os
import typing

from wand.image import Image as WImage
import wand.version

from preview_generator.preview.generic_preview import ImagePreviewBuilder
from preview_generator.utils import ImgDims
from preview_generator.utils import imagemagick_supported_mimes


class ImagePreviewBuilderWand(ImagePreviewBuilder):

    weight = 40
    MIMETYPES = []  # type: typing.List[str]

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

        invalid_mimetypes = ["application/postscript", "application/x-xcf", "image/x-xcf"]

        for invalid_mimetype in invalid_mimetypes:
            try:
                mimetypes.remove(invalid_mimetype)
            except ValueError:
                pass
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
        with WImage(filename=file_path) as img:
            # https://legacy.imagemagick.org/Usage/thumbnails/
            img.auto_orient()
            img.merge_layers("merge")
            img.strip()
            img.sample()
            if img.width < size.width and img.height < size.height:
                flag = "<"
            else:
                flag = ">"
            resize_arg = "{width}x{height}{flag}".format(
                width=size.width,
                height=size.height,
                flag=flag
            )
            img.transform(resize=resize_arg)
            img.save(filename=dest_path)
