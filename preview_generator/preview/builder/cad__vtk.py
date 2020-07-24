# -*- coding: utf-8 -*-


import tempfile
import typing

from preview_generator.exception import BuilderDependencyNotFound
from preview_generator.exception import UnsupportedMimeType
from preview_generator.extension import mimetypes_storage
from preview_generator.preview.builder.image__pillow import ImagePreviewBuilderPillow  # nopep8
from preview_generator.preview.generic_preview import PreviewBuilder
from preview_generator.utils import ImgDims
from preview_generator.utils import MimetypeMapping

# HACK - G.M - 2019-11-05 - Hack to allow load of module without vtk installed
vtk_installed = True
try:
    from vtk import vtkActor
    from vtk import vtkNamedColors
    from vtk import vtkPNGWriter
    from vtk import vtkPolyDataMapper
    from vtk import vtkRenderWindow
    from vtk import vtkRenderer
    from vtk import vtkSTLReader
    from vtk import vtkVersion
    from vtk import vtkWindowToImageFilter
    from vtk.vtkIOKitPython import vtkAbstractPolyDataReader
    from vtk.vtkIOKitPython import vtkOBJReader
    from vtk.vtkIOKitPython import vtkPLYReader
except ImportError:
    vtk_installed = False


class ImagePreviewBuilderVtk(PreviewBuilder):
    PLY_MIMETYPES_MAPPING = [MimetypeMapping("application/ply", ".ply")]
    OBJ_MIMETYPES_MAPPING = [
        MimetypeMapping("application/wobj", ".obj"),
        MimetypeMapping("application/object", ".obj"),
        MimetypeMapping("model/obj", ".obj"),
    ]
    STL_MIMETYPES_MAPPING = [
        MimetypeMapping("application/sla", ".stl"),
        MimetypeMapping("application/vnd.ms-pki.stl", ".stl"),
        MimetypeMapping("application/x-navistyle", ".stl"),
        MimetypeMapping("model/stl", ".stl"),
    ]

    @classmethod
    def get_label(cls) -> str:
        return "Images generator from 3d file - based on Vtk"

    @classmethod
    def get_supported_mimetypes(cls) -> typing.List[str]:
        mimetypes = []
        for mimetype_mapping in cls.get_mimetypes_mapping():
            mimetypes.append(mimetype_mapping.mimetype)
        return mimetypes

    @classmethod
    def get_mimetypes_mapping(cls) -> typing.List[MimetypeMapping]:
        return cls.STL_MIMETYPES_MAPPING + cls.OBJ_MIMETYPES_MAPPING + cls.PLY_MIMETYPES_MAPPING

    @classmethod
    def check_dependencies(cls) -> None:
        if not vtk_installed:
            raise BuilderDependencyNotFound("this builder requires vtk to be available")

    @classmethod
    def dependencies_versions(cls) -> typing.Optional[str]:
        vtk_version = vtkVersion()
        return "VTK version :{}".format(vtk_version.GetVTKVersion())

    @classmethod
    def _get_vtk_reader(cls, mimetype: str) -> "vtkAbstractPolyDataReader":
        if mimetype in [mapping.mimetype for mapping in cls.STL_MIMETYPES_MAPPING]:
            return vtkSTLReader()
        elif mimetype in [mapping.mimetype for mapping in cls.OBJ_MIMETYPES_MAPPING]:
            return vtkOBJReader()
        elif mimetype in [mapping.mimetype for mapping in cls.PLY_MIMETYPES_MAPPING]:
            return vtkPLYReader()
        else:
            raise UnsupportedMimeType("Unsupported mimetype: {}".format(mimetype))

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

        colors = vtkNamedColors()

        if not mimetype:
            guessed_mimetype, _ = mimetypes_storage.guess_type(file_path, strict=False)
            # INFO - G.M - 2019-11-22 - guessed_mimetype can be None
            mimetype = guessed_mimetype or ""
        reader = self._get_vtk_reader(mimetype)
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
        renWin.SetSize(size.width, size.height)
        ren.SetBackground(colors.GetColor3d("white"))

        # Assign actor to the renderer
        ren.AddActor(actor)

        renWin.Render()

        # Write image
        windowto_image_filter = vtkWindowToImageFilter()
        windowto_image_filter.SetInput(renWin)
        # windowto_image_filter.SetScale(scale)  # image scale
        windowto_image_filter.SetInputBufferTypeToRGBA()

        with tempfile.NamedTemporaryFile(
            "w+b", prefix="preview-generator-", suffix=".png"
        ) as tmp_png:
            writer = vtkPNGWriter()
            writer.SetFileName(tmp_png.name)
            writer.SetInputConnection(windowto_image_filter.GetOutputPort())
            writer.Write()

            return ImagePreviewBuilderPillow().build_jpeg_preview(
                tmp_png.name, preview_name, cache_path, page_id, extension, size, mimetype
            )

    def has_jpeg_preview(self) -> bool:
        return True

    def get_page_number(
        self, file_path: str, preview_name: str, cache_path: str, mimetype: str = ""
    ) -> int:
        return 1
