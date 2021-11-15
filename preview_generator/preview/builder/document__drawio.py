# -*- coding: utf-8 -*-
from subprocess import DEVNULL
from subprocess import STDOUT
from subprocess import check_call
import tempfile
import typing

from preview_generator.exception import BuilderDependencyNotFound
from preview_generator.exception import IntermediateFileBuildingFailed
from preview_generator.preview.builder.image__wand import ImagePreviewBuilderWand
from preview_generator.preview.generic_preview import PreviewBuilder
from preview_generator.utils import ImgDims
from preview_generator.utils import MimetypeMapping
from preview_generator.utils import executable_is_available

xvfbwrapper_installed = True
try:
    from xvfbwrapper import Xvfb
except ImportError:
    xvfbwrapper_installed = False


class ImagePreviewBuilderDrawio(PreviewBuilder):
    DRAWIO_MIMETYPES_MAPPING = [MimetypeMapping("application/drawio", ".drawio")]
    weight = 120

    @classmethod
    def check_dependencies(cls) -> None:
        if not xvfbwrapper_installed:
            raise BuilderDependencyNotFound("this builder requires xvfbwrapper")
        if not executable_is_available("xvfb-run"):
            raise BuilderDependencyNotFound("this builder requires xvfb-run to be available")

        if not executable_is_available("drawio"):
            raise BuilderDependencyNotFound("this builder requires drawio to be available")

    @classmethod
    def get_label(cls) -> str:
        return "Images generator from Drawio files"

    @classmethod
    def get_supported_mimetypes(cls) -> typing.List[str]:
        mimetypes = []
        for mimetype_mapping in cls.get_mimetypes_mapping():
            mimetypes.append(mimetype_mapping.mimetype)
        return mimetypes

    @classmethod
    def get_mimetypes_mapping(cls) -> typing.List[MimetypeMapping]:
        return cls.DRAWIO_MIMETYPES_MAPPING

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
            "w+b", prefix="preview-generator-", suffix=".jpg"
        ) as tmp_jpg:
            with Xvfb():
                build_jpg_result_code = check_call(
                    [
                        "drawio",
                        "-x",
                        "-f",
                        "jpg",
                        "-o",
                        tmp_jpg.name,
                        file_path,
                        # INFO - G.M - 12/11/2021 - Add no-sandbox at the end as putting it before
                        # doesn't work, see:
                        # https://github.com/jgraph/drawio-desktop/issues/249#issuecomment-695179747
                        "--no-sandbox",
                    ],
                    stdout=DEVNULL,
                    stderr=STDOUT,
                    timeout=30,
                )

            if build_jpg_result_code != 0:
                raise IntermediateFileBuildingFailed(
                    "Building JPG intermediate file using drawio "
                    "failed with status {}".format(build_jpg_result_code)
                )

            ImagePreviewBuilderWand().build_jpeg_preview(
                tmp_jpg.name, preview_name, cache_path, page_id, extension, size, mimetype
            )

    def has_jpeg_preview(self) -> bool:
        return True

    def get_page_number(
        self, file_path: str, preview_name: str, cache_path: str, mimetype: str = ""
    ) -> int:
        return 1
