# -*- coding: utf-8 -*-

from io import BytesIO
import typing

from wand.image import Color
from wand.image import Image as WImage
import wand.version

from preview_generator.preview.builder.image__imconvert import ImagePreviewBuilderIMConvert
from preview_generator.preview.generic_preview import ImagePreviewBuilder
from preview_generator.utils import ImgDims
from preview_generator.utils import compute_resize_dims
from preview_generator.utils import imagemagick_supported_mimes


class ImagePreviewBuilderWand(ImagePreviewBuilder):
    """
    WARNING : This builder is deprecated, prefer ImagePreviewBuilderIMConvert instead which
    support the same list of format.
    """

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

        # INFO - G.M - 2021-04-30
        # Disable support for postscript,xcf and raw image format in wand, to ensure
        # proper builder is used (either imagemagick convert or pillow)

        invalid_mimetypes = ["application/postscript", "application/x-xcf", "image/x-xcf"]
        for (
            mimetype_mapping
        ) in ImagePreviewBuilderIMConvert().SUPPORTED_RAW_CAMERA_MIMETYPE_MAPPING:
            invalid_mimetypes.append(mimetype_mapping.mimetype)

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
        with open(file_path, "rb") as img:
            result = self.image_to_jpeg_wand(img, ImgDims(width=size.width, height=size.height))

            with open(
                "{path}{extension}".format(path=cache_path + preview_name, extension=extension),
                "wb",
            ) as jpeg:
                buffer = result.read(1024)
                while buffer:
                    jpeg.write(buffer)
                    buffer = result.read(1024)

    def image_to_jpeg_wand(
        self, jpeg: typing.Union[str, typing.IO[bytes]], preview_dims: ImgDims
    ) -> BytesIO:
        """
        for jpeg, gif and bmp
        :param jpeg:
        :param size:
        :return:
        """
        self.logger.info("Converting image to jpeg using wand")

        with WImage(file=jpeg, background=Color("white")) as image:

            preview_dims = ImgDims(width=preview_dims.width, height=preview_dims.height)

            resize_dim = compute_resize_dims(
                dims_in=ImgDims(width=image.size[0], height=image.size[1]), dims_out=preview_dims
            )
            image.resize(resize_dim.width, resize_dim.height)
            # INFO - jumenzel - 2019-03-12 - remove metadata, color-profiles from this image.
            image.strip()
            content_as_bytes = image.make_blob("jpeg")
            output = BytesIO()
            output.write(content_as_bytes)
            output.seek(0, 0)
            return output
