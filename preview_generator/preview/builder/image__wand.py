# -*- coding: utf-8 -*-
import os
import typing

from wand.color import Color
from wand.exceptions import CoderError
from wand.exceptions import CoderFatalError
from wand.exceptions import CoderWarning
from wand.image import Image
import wand.version

from preview_generator.exception import BuilderDependencyNotFound
from preview_generator.extension import mimetypes_storage
from preview_generator.preview.generic_preview import ImagePreviewBuilder
from preview_generator.utils import ImgDims
from preview_generator.utils import MimetypeMapping
from preview_generator.utils import compute_resize_dims
from preview_generator.utils import executable_is_available
from preview_generator.utils import imagemagick_supported_mimes

DEFAULT_JPEG_QUALITY = 85
DEFAULT_JPEG_PROGRESSIVE = True


class ImagePreviewBuilderWand(ImagePreviewBuilder):

    weight = 30
    MIMETYPES = []  # type: typing.List[str]
    # TODO - G.M - 2019-11-21 - find better storage solution for mimetype mapping
    # dict and/or list.
    # see https://github.com/algoo/preview-generator/pull/148#discussion_r346381508
    SUPPORTED_RAW_CAMERA_MIMETYPE_MAPPING = [
        MimetypeMapping("image/x-sony-arw", ".arw"),
        MimetypeMapping("image/x-adobe-dng", ".dng"),
        MimetypeMapping("image/x-sony-sr2", ".sr2"),
        MimetypeMapping("image/x-sony-srf", ".srf"),
        MimetypeMapping("image/x-sigma-x3f", ".x3f"),
        MimetypeMapping("image/x-canon-crw", ".crw"),
        MimetypeMapping("image/x-canon-cr2", ".cr2"),
        MimetypeMapping("image/x-epson-erf", ".erf"),
        MimetypeMapping("image/x-fuji-raf", ".raf"),
        MimetypeMapping("image/x-nikon-nef", ".nef"),
        MimetypeMapping("image/x-olympus-orf", ".orf"),
        MimetypeMapping("image/x-panasonic-raw", ".raw"),
        MimetypeMapping("image/x-panasonic-rw2", ".rw2"),
        MimetypeMapping("image/x-pentax-pef", ".pef"),
        MimetypeMapping("image/x-kodak-dcr", ".dcr"),
        MimetypeMapping("image/x-kodak-k25", ".k25"),
        MimetypeMapping("image/x-kodak-kdc", ".kdc"),
        MimetypeMapping("image/x-minolta-mrw", ".mrw"),
    ]

    SUPPORTED_HEIC_MIMETYPE_MAPPING = [
        MimetypeMapping("image/heic", ".heic"),
        MimetypeMapping("image/heic", ".heif"),
    ]

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

        mimes = imagemagick_supported_mimes()  # type: typing.List[str]
        # HACK - G.M - 2019-10-31 - Handle raw format only if ufraw-batch is installed as most common
        # default imagemagick configuration delegate raw format to ufraw-batch.
        if executable_is_available("ufraw-batch"):
            for mimetype_mapping in cls.SUPPORTED_RAW_CAMERA_MIMETYPE_MAPPING:
                mimes.append(mimetype_mapping.mimetype)
        if executable_is_available("dwebp"):
            mimes.append("image/webp")
        return mimes

    @classmethod
    def get_mimetypes_mapping(cls) -> typing.List[MimetypeMapping]:
        mimetypes_mapping = [
            MimetypeMapping("image/webp", ".webp")
        ]  # type: typing.List[MimetypeMapping]
        mimetypes_mapping = (
            mimetypes_mapping
            + cls.SUPPORTED_RAW_CAMERA_MIMETYPE_MAPPING
            + cls.SUPPORTED_HEIC_MIMETYPE_MAPPING
        )
        return mimetypes_mapping

    @classmethod
    def check_dependencies(cls) -> None:
        if not executable_is_available("convert"):
            raise BuilderDependencyNotFound("this builder requires convert to be available")

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
        self.image_to_jpeg_wand(file_path, size, dest_path, mimetype=mimetype)

    def image_to_jpeg_wand(
        self, file_path: str, preview_dims: ImgDims, dest_path: str, mimetype: typing.Optional[str]
    ) -> None:
        try:
            with self._convert_image(file_path, preview_dims) as img:
                img.save(filename=dest_path)
        except (CoderError, CoderFatalError, CoderWarning) as e:
            assert mimetype
            file_ext = mimetypes_storage.guess_extension(mimetype, strict=False) or ""
            if file_ext:
                file_path = file_ext.lstrip(".") + ":" + file_path
                with self._convert_image(file_path, preview_dims) as img:
                    img.save(filename=dest_path)
            else:
                raise e

    def _convert_image(self, file_path: str, preview_dims: ImgDims) -> Image:
        """
        refer: https://legacy.imagemagick.org/Usage/thumbnails/
        like cmd: convert -layers merge  -background white -thumbnail widthxheight \
        -auto-orient -quality 85 -interlace plane input.jpeg output.jpeg
        """

        img = Image(filename=file_path)
        img.auto_orient()
        resize_dim = compute_resize_dims(
            dims_in=ImgDims(width=img.width, height=img.height), dims_out=preview_dims
        )

        img.iterator_reset()
        img.background_color = Color("white")
        img.merge_layers("merge")

        if self.progressive:
            img.interlace_scheme = "plane"

        img.compression_quality = self.quality

        img.thumbnail(resize_dim.width, resize_dim.height)

        return img
