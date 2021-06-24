import subprocess
from abc import ABC

import typing
from enum import Enum

from preview_generator.preview.generic_preview import ImagePreviewBuilder
from preview_generator.utils import MimetypeMapping, ImgDims

class BlenderEngine(str, Enum):
    WORKBENCH_ENGINE = "BLENDER_WORKBENCH" # The fastest, don't render much (no texture, etc,…)
    EEVE_ENGINE = "BLENDER_EEVEE" # fastest real render, videogame-like render.
    CYCLE_ENGINE = "CYCLES" # Raytracing engine, very slow !

class ImagePreviewBuilderBlender(ImagePreviewBuilder):
    weight: int = 150
    engine: BlenderEngine = BlenderEngine.WORKBENCH_ENGINE
    thread_number: int = 4

    @classmethod
    def get_label(cls) -> str:
        return "Blender Preview Builder"

    @classmethod
    def get_supported_mimetypes(cls) -> typing.List[str]:
        return ['application/x-blender']

    @classmethod
    def get_mimetypes_mapping(cls) -> typing.List[MimetypeMapping]:
        return [MimetypeMapping("application/x-blender", ".blend")]


    @classmethod
    def check_dependencies(cls) -> None:
        #TODO - check bpy exist.
        pass

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
        preview_file_path = "{path}".format(
            path=cache_path + preview_name, extension=extension, page_id="####"
        )
        # TODO : use bpy instead to:
        # - set the render size
        # - get the frame number
        # - give proper name to preview
        # I didn't do it now, as bpy doesn't run on my debian unstable (hard to troubleshoot).
        command = ["blender", "-b", file_path, "-o", preview_file_path, "-E", self.engine, "-t", str(self.thread_number), "-f", str(page_id+1), "-F", "JPEG"]
        subprocess.check_call(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )
