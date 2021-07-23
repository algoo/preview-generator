import os
import subprocess
import typing

from preview_generator.exception import BuilderDependencyNotFound
from preview_generator.preview.generic_preview import ImagePreviewBuilder
from preview_generator.utils import ImgDims
from preview_generator.utils import MimetypeMapping
from preview_generator.utils import executable_is_available

DARKTABLE_CLI_EXECUTABLE = "darktable-cli"
DARKTABLE_RAW_TO_PNG_OPTIONS = [
    "--apply-custom-presets",
    "0",
    "--hq",
    "0",
    "--core",
    "--conf",
    "plugins/imageio/format/jpeg/quality=75",
]


def generate_inkscape_command(
    input_path: str, output_path: str, options: typing.List[str], width: int, height: int
):
    return [
        DARKTABLE_CLI_EXECUTABLE,
        input_path,
        output_path,
        "--width",
        str(width),
        "--height",
        str(height),
        *options,
    ]


class ImagePreviewBuilderDarktable(ImagePreviewBuilder):
    weight = 150

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

    @classmethod
    def get_label(cls) -> str:
        return "Darktable Preview Builder"

    @classmethod
    def get_supported_mimetypes(cls) -> typing.List[str]:
        mimes = []
        for mimetype_mapping in cls.SUPPORTED_RAW_CAMERA_MIMETYPE_MAPPING:
            mimes.append(mimetype_mapping.mimetype)
        return mimes

    @classmethod
    def get_mimetypes_mapping(cls) -> typing.List[MimetypeMapping]:
        return cls.SUPPORTED_RAW_CAMERA_MIMETYPE_MAPPING

    @classmethod
    def check_dependencies(cls) -> None:
        if not executable_is_available("darktable-cli"):
            raise BuilderDependencyNotFound("this builder requires darktable-cli to be available")

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
        preview_file_path = "{path}{extension}".format(
            path=cache_path + preview_name, extension=extension,
        )
        output_preview_file_path = "{path}{extension}".format(
            path=cache_path + preview_name, extension=".jpg",
        )
        # TODO : use bpy instead to:
        # - set the render size
        # - get the frame number
        # - give proper name to preview
        # I didn't do it now, as bpy doesn't run on my debian unstable (hard to troubleshoot).
        command = generate_inkscape_command(
            file_path,
            preview_file_path,
            options=DARKTABLE_RAW_TO_PNG_OPTIONS,
            width=size.width,
            height=size.height,
        )
        subprocess.check_call(
            command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT,
        )
        # FIXME: weird hotfix as file created always end with .jpg for unclear reason
        os.rename(output_preview_file_path, preview_file_path)
