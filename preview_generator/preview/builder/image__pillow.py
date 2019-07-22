# -*- coding: utf-8 -*-
from abc import ABC
from abc import abstractmethod
from io import BytesIO
import logging
import typing

import PIL
from PIL import Image

from preview_generator.preview.generic_preview import ImagePreviewBuilder
from preview_generator.utils import ImgDims
from preview_generator.utils import compute_resize_dims

# INFO - G.M - 2019-06-25 - some configuration for jpeg saved,
# see https://pillow.readthedocs.io/en/latest/handbook/image-file-formats.html?highlight=JPEG#jpeg
# optimize -> extra pass to select optimal encoded
# quality -> compression level from 1 to 100
# progressive -> permit to see a blured version of file instead of partial image when image
# is not fully downloaded, nice for web usage.
DEFAULT_JPEG_OPTIMIZE = True
DEFAULT_JPEG_QUALITY = 75
DEFAULT_JPEG_PROGRESSIVE = True
# Pillow algorithm use for resampling, bilinear is not the fastest but is fast
# enough, this permit good enough image (using faster algorithm return much more
# aliasing. see https://pillow.readthedocs.io/en/latest/handbook/concepts.html?highlight=Bilinear#filters
# for algorithm list.
DEFAULT_JPEG_RESAMPLE_ALGORITHM = PIL.Image.BILINEAR
# Pillow deal with many different mode of image:
# https://pillow.readthedocs.io/en/latest/handbook/concepts.html#modes
# those are mode known to have alpha layer, so needing special process to
# have clean white background
# RGBA is RGB + Alpha channel
# LA is L (8-bit pixels, black and white) + Alpha channel
# color for
DEFAULT_RGB_BACKGROUND_COLOR = (255, 255, 255)  # This means white background
DEFAULT_BW_BACKGROUND_COLOR = 1
DEFAULT_SAVING_MODE = "RGB"


class ImageConvertStrategy(ABC):
    def __init__(self, logger: logging.Logger):
        assert logger is not None
        self.logger = logger

    @abstractmethod
    def save(
        self,
        origin_image: PIL.Image,
        file_output: BytesIO,
        optimize: bool = DEFAULT_JPEG_OPTIMIZE,
        quality: int = DEFAULT_JPEG_QUALITY,
        progressive: bool = DEFAULT_JPEG_PROGRESSIVE,
    ) -> BytesIO:
        pass


class ImageConvertStrategyNotTransparent(ImageConvertStrategy):
    """
    Image converter for all non transparent image
    """

    def save(
        self,
        origin_image: PIL.Image,
        file_output: BytesIO,
        optimize: bool = DEFAULT_JPEG_OPTIMIZE,
        quality: int = DEFAULT_JPEG_QUALITY,
        progressive: bool = DEFAULT_JPEG_PROGRESSIVE,
    ) -> BytesIO:
        try:
            origin_image.save(
                fp=file_output,
                format="jpeg",
                optimize=optimize,
                quality=quality,
                progressive=progressive,
            )
        except OSError:
            # INFO - G.M - in some case image mode cannot be directly convert to JPEG, in those
            # case, it raise OSError, we should fallback to a working mode and retry saving.
            origin_image = origin_image.convert(DEFAULT_SAVING_MODE)
            origin_image.save(
                fp=file_output,
                format="jpeg",
                optimize=optimize,
                quality=quality,
                progressive=progressive,
            )
        file_output.seek(0, 0)
        return file_output


class ImageConvertStrategyTransparent(ImageConvertStrategy):
    """
    Abstract image converter for Transparent Image
    """

    def _save_transparent_image(
        self,
        origin_image: PIL.Image,
        file_output: BytesIO,
        optimize: bool = DEFAULT_JPEG_OPTIMIZE,
        quality: int = DEFAULT_JPEG_QUALITY,
        progressive: bool = DEFAULT_JPEG_PROGRESSIVE,
        saving_mode: str = DEFAULT_SAVING_MODE,
        background_color: typing.Union[
            int, typing.Tuple[int, int, int]
        ] = DEFAULT_BW_BACKGROUND_COLOR,
    ) -> BytesIO:
        # INFO - G.M - 2019-06-25 - create uniform base image
        temp_image = Image.new(
            mode=saving_mode, size=(origin_image.width, origin_image.height), color=background_color
        )
        # INFO - G.M - 2019-06-25 - apply current image with transparency on top of the base image
        try:
            temp_image.paste(im=origin_image, box=(0, 0), mask=origin_image)
        except ValueError:
            self.logger.warning(
                "Failed the transparency mask superposition. "
                "Maybe your image does not contain a transparency mask"
            )
            temp_image.paste(origin_image)
        temp_image.save(
            fp=file_output,
            format="jpeg",
            optimize=optimize,
            quality=quality,
            progressive=progressive,
        )
        file_output.seek(0, 0)
        return file_output


class ImageConvertStrategyRGBA(ImageConvertStrategyTransparent):
    """
    Image converter for RGBA image
    """

    def save(
        self,
        origin_image: PIL.Image,
        file_output: BytesIO,
        optimize: bool = DEFAULT_JPEG_OPTIMIZE,
        quality: int = DEFAULT_JPEG_QUALITY,
        progressive: bool = DEFAULT_JPEG_PROGRESSIVE,
    ) -> BytesIO:
        return self._save_transparent_image(
            origin_image=origin_image,
            file_output=file_output,
            optimize=optimize,
            quality=quality,
            progressive=progressive,
            saving_mode="RGB",
            background_color=DEFAULT_RGB_BACKGROUND_COLOR,
        )


class ImageConvertStrategyLA(ImageConvertStrategyTransparent):
    """
    Image converter for LA image
    """

    def save(
        self,
        origin_image: PIL.Image,
        file_output: BytesIO,
        optimize: bool = DEFAULT_JPEG_OPTIMIZE,
        quality: int = DEFAULT_JPEG_QUALITY,
        progressive: bool = DEFAULT_JPEG_PROGRESSIVE,
    ) -> BytesIO:
        return self._save_transparent_image(
            origin_image=origin_image,
            file_output=file_output,
            optimize=optimize,
            quality=quality,
            progressive=progressive,
            saving_mode="L",
            background_color=DEFAULT_BW_BACKGROUND_COLOR,
        )


class PillowImageConvertStrategyFactory(object):
    """
    Factory class to retrieve image convert strategy according to image mode
    """

    def __init__(self, logger: logging.Logger):
        assert logger is not None
        self.logger = logger

    def get_strategy(self, image: PIL.Image) -> ImageConvertStrategy:
        """
        Get strategy to use for this image mode
        :param mode: pillow image mode
        :return:
        """

        # INFO - G.M - 2019-06-27 - support for color RGB + Alpha transparent image
        if image.mode == "RGBA":
            return ImageConvertStrategyRGBA(self.logger)
        # INFO - G.M - 2019-06-27 - RGBa are similar as RGBA but alpha is premultiplied.
        if image.mode == "RGBa":
            return ImageConvertStrategyRGBA(self.logger)
        # INFO - G.M - 2019-06-27 - LA are L (black and white 8 bit) + alpha layer
        elif image.mode == "LA":
            return ImageConvertStrategyLA(self.logger)
        else:
            return ImageConvertStrategyNotTransparent(self.logger)


class ImagePreviewBuilderPillow(ImagePreviewBuilder):
    def __init__(
        self,
        optimize: bool = DEFAULT_JPEG_OPTIMIZE,
        quality: int = DEFAULT_JPEG_QUALITY,
        progressive: bool = DEFAULT_JPEG_PROGRESSIVE,
        resample_filter_algorithm: int = DEFAULT_JPEG_RESAMPLE_ALGORITHM,
    ):
        super().__init__()

        self.optimize = optimize
        self.quality = quality
        self.progressive = progressive
        self.resample_filter_algorithm = resample_filter_algorithm

    @classmethod
    def get_label(cls) -> str:
        return "Bitmap images - based on Pillow"

    @classmethod
    def dependencies_versions(cls) -> typing.Optional[str]:
        return "PIL {} from {}".format(PIL.__version__, ", ".join(PIL.__path__))

    @classmethod
    def get_supported_mimetypes(cls) -> typing.List[str]:
        return ["image/png", "application/postscript", "image/x-eps"]

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
        """
        generate the jpg preview
        """
        if not size:
            size = self.default_size
        with open(file_path, "rb") as img:
            result = self.image_to_jpeg_pillow(img, size)
            preview_file_path = "{path}{extension}".format(
                path=cache_path + preview_name, extension=extension
            )
            with open(preview_file_path, "wb") as jpeg:
                buffer = result.read(1024)
                while buffer:
                    jpeg.write(buffer)
                    buffer = result.read(1024)

    def image_to_jpeg_pillow(
        self, png: typing.Union[str, typing.IO[bytes]], preview_dims: ImgDims
    ) -> BytesIO:
        self.logger.info("Converting image to jpeg using Pillow")

        with Image.open(png) as image:
            resize_dim = compute_resize_dims(
                dims_in=ImgDims(width=image.size[0], height=image.size[1]), dims_out=preview_dims
            )
            output = BytesIO()
            image = image.resize(
                (resize_dim.width, resize_dim.height), resample=self.resample_filter_algorithm
            )
            image_converter = PillowImageConvertStrategyFactory(self.logger).get_strategy(image)
            return image_converter.save(
                image,
                output,
                optimize=self.optimize,
                progressive=self.progressive,
                quality=self.quality,
            )
