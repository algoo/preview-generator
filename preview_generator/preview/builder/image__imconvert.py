# -*- coding: utf-8 -*-
from functools import partial
from shutil import which
from subprocess import CalledProcessError
from subprocess import DEVNULL
from subprocess import STDOUT
from subprocess import check_call
from subprocess import check_output
import tempfile
import typing

from preview_generator.exception import BuilderDependencyNotFound
from preview_generator.exception import IntermediateFileBuildingFailed
from preview_generator.extension import mimetypes_storage
from preview_generator.preview.builder.image__pillow import ImagePreviewBuilderPillow  # nopep8
from preview_generator.preview.generic_preview import ImagePreviewBuilder
from preview_generator.utils import ImgDims
from preview_generator.utils import MimetypeMapping
from preview_generator.utils import executable_is_available
from preview_generator.utils import imagemagick_supported_mimes

CONVERT_CMD = "convert"
CONVERT_TO_PNG_OPTIONS = [
    "-background",
    "None",
    "-layers",
    "merge",
]


def generate_convert_command(
    input_path: str,
    output_path: str,
    options: typing.List[str],
    input_format: str = None,
    output_format: str = None,
) -> typing.List[str]:
    if input_format:
        input_path = "{}:{}".format(input_format, input_path)
    if output_format:
        output_path = "{}:{}".format(output_format, output_path)
    return [CONVERT_CMD, input_path, *options, output_path]


convert_to_png_command = partial(
    generate_convert_command, options=CONVERT_TO_PNG_OPTIONS, output_format="png"
)


class ImagePreviewBuilderIMConvert(ImagePreviewBuilder):
    """IM means Image Magick"""

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

    weight = 20

    @classmethod
    def get_label(cls) -> str:
        return "Images - based on convert command (Image magick)"

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

        # HACK - G.M - 2019-11-14 - disable support for
        # postscript file and png in imagemagick to use
        # pillow instead
        mimes.remove("application/postscript")
        mimes.remove("image/png")
        mimes.append("application/x-xcf")
        mimes.append("image/x-xcf")

        return mimes

    @classmethod
    def get_supported_mimetypes(cls) -> typing.List[str]:
        """
        :return: list of supported mime types
        """
        if len(ImagePreviewBuilderIMConvert.MIMETYPES) == 0:
            ImagePreviewBuilderIMConvert.MIMETYPES = cls.__load_mimetypes()
        return ImagePreviewBuilderIMConvert.MIMETYPES

    @classmethod
    def get_mimetypes_mapping(cls) -> typing.List[MimetypeMapping]:
        mimetypes_mapping = []  # type: typing.List[MimetypeMapping]
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
    def dependencies_versions(cls) -> typing.Optional[str]:
        return "{} from {}".format(
            check_output(["convert", "--version"], universal_newlines=True).split("\n")[0],
            which("convert"),
        )

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
        with tempfile.NamedTemporaryFile(
            "w+b", prefix="preview-generator-", suffix=".png"
        ) as tmp_png:
            build_png_result_code = self._imagemagick_convert_to_png(
                source_path=file_path, dest_path=tmp_png.name, mimetype=mimetype
            )
            if build_png_result_code != 0:
                raise IntermediateFileBuildingFailed(
                    "Building PNG intermediate file using convert "
                    "failed with status {}".format(build_png_result_code)
                )
            return ImagePreviewBuilderPillow().build_jpeg_preview(
                tmp_png.name, preview_name, cache_path, page_id, extension, size
            )

    def _imagemagick_convert_to_png(
        self, source_path: str, dest_path: str, mimetype: typing.Optional[str] = None
    ) -> int:
        """
        Try convert using both explicit or implicit input type convert.
        """

        assert mimetype != ""
        # INFO - G.M - 2019-11-14 - use explicit input type to clarify conversion for imagemagick
        do_an_explicit_convert = False
        input_file_extension = ""  # type: str
        if mimetype is not None:
            input_file_extension = mimetypes_storage.guess_extension(mimetype, strict=False) or ""
            if input_file_extension:
                do_an_explicit_convert = True

        if do_an_explicit_convert:
            input_format = input_file_extension.lstrip(".")
            try:
                build_image_result_code = check_call(
                    convert_to_png_command(
                        input_path=source_path, input_format=input_format, output_path=dest_path
                    ),
                    stdout=DEVNULL,
                    stderr=STDOUT,
                )
            except CalledProcessError:
                build_image_result_code = check_call(
                    convert_to_png_command(input_path=source_path, output_path=dest_path),
                    stdout=DEVNULL,
                    stderr=STDOUT,
                )
        else:
            build_image_result_code = check_call(
                convert_to_png_command(input_path=source_path, output_path=dest_path),
                stdout=DEVNULL,
                stderr=STDOUT,
            )

        return build_image_result_code
