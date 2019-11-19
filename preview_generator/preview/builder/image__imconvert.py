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

import wand

from preview_generator.exception import BuilderDependencyNotFound
from preview_generator.exception import IntermediateFileBuildingFailed
from preview_generator.extension import mimetypes_storage
from preview_generator.preview.builder.image__pillow import ImagePreviewBuilderPillow  # nopep8
from preview_generator.preview.generic_preview import ImagePreviewBuilder
from preview_generator.utils import ImgDims
from preview_generator.utils import MimetypeMapping
from preview_generator.utils import executable_is_available


class ImagePreviewBuilderIMConvert(ImagePreviewBuilder):

    MIMETYPES = []  # type: typing.List[str]
    SUPPORTED_RAW_CAMERA_MIMETYPE_MAPPING = [
        ["image/x-sony-arw", ".arw"],
        ["image/x-adobe-dng", ".dng"],
        ["image/x-sony-sr2", ".sr2"],
        ["image/x-sony-srf", ".srf"],
        ["image/x-sigma-x3f", ".x3f"],
        ["image/x-canon-crw", ".crw"],
        ["image/x-canon-cr2", ".cr2"],
        ["image/x-epson-erf", ".erf"],
        ["image/x-fuji-raf", ".raf"],
        ["image/x-nikon-nef", ".nef"],
        ["image/x-olympus-orf", ".orf"],
        ["image/x-panasonic-raw", ".raw"],
        ["image/x-panasonic-rw2", ".rw2"],
        ["image/x-pentax-pef", ".pef"],
        ["image/x-kodak-dcr", ".dcr"],
        ["image/x-kodak-k25", ".k25"],
        ["image/x-kodak-kdc", ".kdc"],
        ["image/x-minolta-mrw", ".mrw"],
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

        all_supported = wand.version.formats("*")
        mimes = []  # type: typing.List[str]
        for supported in all_supported:
            url = "./FILE.{0}".format(supported)  # Fake a url
            mime, enc = mimetypes_storage.guess_type(url)
            if mime and mime not in mimes:
                if "video" not in mime:
                    # TODO - D.A. - 2018-09-24 - Do not skip video if supported
                    mimes.append(mime)
        svg_mime = "image/svg+xml"
        if svg_mime in mimes:
            # HACK - D.A. - 2018-11-07 do not convert SVG using convert
            #  The optionnal behavior is related to different configurations on Debian and Ubuntu
            # (need to remove the mimetype on Ubuntu but useless on Debian
            mimes.remove("image/svg+xml")

        # HACK - G.M - 2019-10-31 - Handle raw format only if ufraw-batch is installed
        # as most common default imagemagick configuration delegate raw format to ufraw-batch.
        if executable_is_available("ufraw-batch"):
            for mimetype_mapping in cls.SUPPORTED_RAW_CAMERA_MIMETYPE_MAPPING:
                mimes.append(mimetype_mapping[0])
        # HACK - G.M - 2019-11-14 - disable support for postscript file in imagemagick to use
        # pillow instead
        mimes.remove("application/postscript")
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
        mimetypes_mapping = []
        for mimetype_mapping in cls.SUPPORTED_RAW_CAMERA_MIMETYPE_MAPPING:
            mimetypes_mapping.append(
                MimetypeMapping(mimetype=mimetype_mapping[0], file_extension=mimetype_mapping[1])
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
        tmp_filename = "{}.png".format(str(uuid.uuid4()))
        if tempfile.tempdir:
            tmp_filepath = os.path.join(tempfile.tempdir, tmp_filename)
        else:
            tmp_filepath = tmp_filename

        build_png_result_code = self._imagemagick_convert(
            source_path=file_path, dest_path=tmp_filepath, mimetype=mimetype
        )
        if build_png_result_code != 0:
            raise IntermediateFileBuildingFailed(
                "Building PNG intermediate file using convert "
                "failed with status {}".format(build_png_result_code)
            )

        return ImagePreviewBuilderPillow().build_jpeg_preview(
            tmp_filepath, preview_name, cache_path, page_id, extension, size
        )

    def _imagemagick_convert(self, source_path: str, dest_path: str, mimetype: str = "") -> int:
        """
        Try convert using both explicit or implicit input type convert.
        """

        # INFO - G.M - 2019-11-14 - use explicit input type to clarify conversion for imagemagick
        do_an_explicit_convert = False
        input_file_extension = ""  # type: str
        if mimetype:
            input_file_extension = mimetypes_storage.guess_extension(mimetype, strict=False) or ""
            if input_file_extension:
                do_an_explicit_convert = True

        if do_an_explicit_convert:
            explicit_source_path = "{}:{}".format(input_file_extension.lstrip("."), source_path)
            build_image_result_code = check_call(
                ["convert", explicit_source_path, "-layers", "merge", dest_path],
                stdout=DEVNULL,
                stderr=STDOUT,
            )
            # INFO - G.M - 2019-11-14 - if explicit convert failed, fallback to
            # implicit input type convert
            if build_image_result_code != 0:
                build_image_result_code = check_call(
                    ["convert", source_path, "-layers", "merge", dest_path],
                    stdout=DEVNULL,
                    stderr=STDOUT,
                )
        else:
            build_image_result_code = check_call(
                ["convert", source_path, "-layers", "merge", dest_path],
                stdout=DEVNULL,
                stderr=STDOUT,
            )

        return build_image_result_code
