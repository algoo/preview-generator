# -*- coding: utf-8 -*-


import os
import tempfile
import typing
import uuid

from preview_generator.exception import BuilderDependencyNotFound
from preview_generator.preview.builder.image__pillow import ImagePreviewBuilderPillow  # nopep8
from preview_generator.preview.generic_preview import PreviewBuilder
from preview_generator.utils import ImgDims

# HACK - G.M - 2019-11-05 - Hack to allow load of module without vtk installed
vtk_installed = True
try:
    from vtk import vtkActor
    from vtk import vtkNamedColors
    from vtk import vtkPNGWriter
    from vtk import vtkPolyDataMapper
    from vtk import vtkRenderer
    from vtk import vtkRenderWindow
    from vtk import vtkSTLReader
    from vtk import vtkVersion
    from vtk import vtkWindowToImageFilter
except ImportError:
    vtk_installed = False


class ImagePreviewBuilderVtk(PreviewBuilder):
    @classmethod
    def get_label(cls) -> str:
        return "Images generator from 3d file - based on Vtk"

    @classmethod
    def get_supported_mimetypes(cls) -> typing.List[str]:
        return [
            "model/stl",
            "application/sla",
            "application/vnd.ms-pki.stl",
            "application/x-navistyle",
        ]

    @classmethod
    def check_dependencies(cls) -> None:
        if not vtk_installed:
            raise BuilderDependencyNotFound("this builder requires vtk to be available")

    @classmethod
    def dependencies_versions(cls) -> typing.Optional[str]:
        vtk_version = vtkVersion()
        return "VTK version :{}".format(vtk_version.GetVTKVersion())

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

        colors = vtkNamedColors()

        reader = vtkSTLReader()  # TODO analyse wich file format is use
        reader.SetFileName(file_path)

        mapper = vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())

        actor = vtkActor()
        actor.SetMapper(mapper)

        rotation = (-70, 0, 45)
        R_x, R_y, R_z = rotation  # TODO set a good looking default orientation
        actor.RotateX(R_x)
        actor.RotateY(R_y)
        actor.RotateZ(R_z)

        # Create a rendering window and renderer
        ren = vtkRenderer()
        renWin = vtkRenderWindow()
        renWin.OffScreenRenderingOn()
        renWin.AddRenderer(ren)
        ren.SetBackground(colors.GetColor3d("white"))

        # Assign actor to the renderer
        ren.AddActor(actor)

        renWin.Render()

        # Write image
        windowto_image_filter = vtkWindowToImageFilter()
        windowto_image_filter.SetInput(renWin)
        # windowto_image_filter.SetScale(scale)  # image scale
        windowto_image_filter.SetInputBufferTypeToRGBA()
        writer = vtkPNGWriter()
        writer.SetFileName(tmp_filepath)
        writer.SetInputConnection(windowto_image_filter.GetOutputPort())
        writer.Write()

        return ImagePreviewBuilderPillow().build_jpeg_preview(
            tmp_filepath, preview_name, cache_path, page_id, extension, size, mimetype
        )

    def has_jpeg_preview(self) -> bool:
        return True

    def get_page_number(
        self, file_path: str, preview_name: str, cache_path: str, mimetype: str = ""
    ) -> int:
        return 1
