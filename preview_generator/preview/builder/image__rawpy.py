import tempfile
import typing

from wand.image import Image

from preview_generator.exception import BuilderDependencyNotFound
from preview_generator.preview.builder.image__wand import ImagePreviewBuilderWand
from preview_generator.preview.generic_preview import ImagePreviewBuilder
from preview_generator.utils import ImgDims
from preview_generator.utils import MimetypeMapping

rawpy_installed = True
try:
    import rawpy
except ImportError:
    rawpy_installed = False


class ImagePreviewBuilderRawpy(ImagePreviewBuilder):
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
        MimetypeMapping("image/x-samsung-srw", ".srw"),
    ]

    @classmethod
    def get_label(cls) -> str:
        return "Rawpy Preview Builder"

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
        if not rawpy_installed:
            raise BuilderDependencyNotFound("this builder requires rawpy to be available")

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
        with tempfile.NamedTemporaryFile(
            "w+b", prefix="preview-generator", suffix=".tiff"
        ) as tmp_tiff:
            with rawpy.imread(file_path) as raw:
                processed_image = raw.postprocess(use_auto_wb=True)
                with Image.from_array(processed_image) as img:
                    img.save(filename=tmp_tiff.name)

            return ImagePreviewBuilderWand().build_jpeg_preview(
                tmp_tiff.name, preview_name, cache_path, page_id, extension, size, mimetype
            )
