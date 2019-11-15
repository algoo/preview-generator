# -*- coding: utf-8 -*-


import os
from shutil import which
from subprocess import DEVNULL
from subprocess import STDOUT
from subprocess import check_call
from subprocess import check_output
import tempfile
import typing
import uuid

from preview_generator.exception import BuilderDependencyNotFound
from preview_generator.exception import IntermediateFileBuildingFailed
from preview_generator.preview.builder.image__pillow import ImagePreviewBuilderPillow  # nopep8
from preview_generator.preview.generic_preview import ImagePreviewBuilder
from preview_generator.utils import ImgDims
from preview_generator.utils import executable_is_available
from preview_generator.utils import imagemagick_supported_mimes


class ImagePreviewBuilderIMConvert(ImagePreviewBuilder):

    MIMETYPES = []  # type: typing.List[str]
    SUPPORTED_RAW_CAMERA_MIMETYPE = [
        "image/x-sony-arw",
        "image/x-adobe-dng",
        "image/x-sony-sr2",
        "image/x-sony-srf",
        "image/x-sigma-x3f",
        "image/x-canon-crw",
        "image/x-canon-cr2",
        "image/x-epson-erf",
        "image/x-fuji-raf",
        "image/x-nikon-nef",
        "image/x-olympus-orf",
        "image/x-panasonic-raw",
        "image/x-panasonic-rw2",
        "image/x-pentax-pef",
        "image/x-kodak-dcr",
        "image/x-kodak-k25",
        "image/x-kodak-kdc",
        "image/x-minolta-mrw",
        "image/x-kde-raw",
    ]

    """ IM means Image Magick"""

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
            for mimetype in cls.SUPPORTED_RAW_CAMERA_MIMETYPE:
                mimes.append(mimetype)
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
        # inkscape tesselation-P3.svg  -e
        tmp_filename = "{}.png".format(str(uuid.uuid4()))
        if tempfile.tempdir:
            tmp_filepath = os.path.join(tempfile.tempdir, tmp_filename)
        else:
            tmp_filepath = tmp_filename
        build_png_result_code = check_call(
            ["convert", file_path, "-layers", "merge", tmp_filepath], stdout=DEVNULL, stderr=STDOUT
        )

        if build_png_result_code != 0:
            raise IntermediateFileBuildingFailed(
                "Building PNG intermediate file using convert "
                "failed with status {}".format(build_png_result_code)
            )

        return ImagePreviewBuilderPillow().build_jpeg_preview(
            tmp_filepath, preview_name, cache_path, page_id, extension, size
        )
