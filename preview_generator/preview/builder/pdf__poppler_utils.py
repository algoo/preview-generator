# -*- coding: utf-8 -*-

from subprocess import DEVNULL
from subprocess import STDOUT
from subprocess import check_call
from subprocess import check_output
import tempfile
import typing

from preview_generator import utils
from preview_generator.exception import BuilderDependencyNotFound
from preview_generator.exception import IntermediateFileBuildingFailed
from preview_generator.preview.builder.image__wand import ImagePreviewBuilderWand
from preview_generator.preview.generic_preview import PreviewBuilder
from preview_generator.utils import executable_is_available

PDFTOCAIRO_EXECUTABLE = "pdftocairo"
PDFINFO_EXECUTABLE = "pdfinfo"


class PdfPreviewBuilderPopplerUtils(PreviewBuilder):
    weight = 140

    @classmethod
    def get_label(cls) -> str:
        return "PDF documents - based on Poppler-Utils"

    @classmethod
    def check_dependencies(cls) -> None:
        for executable in ["pdftocairo", "pdfinfo"]:
            if not executable_is_available(executable):
                raise BuilderDependencyNotFound(
                    "this builder requires {} to be available (from poppler-utils)".format(
                        executable
                    )
                )

    @classmethod
    def get_supported_mimetypes(cls) -> typing.List[str]:
        return ["application/pdf"]

    def build_jpeg_preview(
        self,
        file_path: str,
        preview_name: str,
        cache_path: str,
        page_id: int,
        extension: str = ".jpg",
        size: utils.ImgDims = None,
        mimetype: str = "",
    ) -> None:
        """
        generate the pdf small preview
        """
        # INFO - G.M - 2021-10-21 - Page id in pdftocairo begins at 1 instead of 0
        page_id = page_id + 1
        if not size:
            size = self.default_size

        with tempfile.NamedTemporaryFile(
            "w+b", prefix="preview-generator-", suffix=".png"
        ) as tmp_png:
            build_png_result_code = check_call(
                [
                    PDFTOCAIRO_EXECUTABLE,
                    "-png",
                    "-singlefile",
                    "-scale-to",
                    str(size.max_dim()),
                    "-f",
                    str(page_id),
                    "-l",
                    str(page_id),
                    file_path,
                    # HACK - G.M - 2021-10-21 - For unclear reason, pdftocairo add a second .png
                    # extension to the file created.
                    tmp_png.name.rsplit(".png", 1)[0],
                ],
                stdout=DEVNULL,
                stderr=STDOUT,
            )
            if build_png_result_code != 0:
                raise IntermediateFileBuildingFailed(
                    "Building PNG intermediate file using pdftocairo failed with status {}".format(
                        build_png_result_code
                    )
                )
            return ImagePreviewBuilderWand().build_jpeg_preview(
                tmp_png.name, preview_name, cache_path, page_id, extension, size, mimetype
            )

    def build_pdf_preview(
        self,
        file_path: str,
        preview_name: str,
        cache_path: str,
        extension: str = ".pdf",
        page_id: int = -1,
        mimetype: str = "",
    ) -> None:
        """
        generate the pdf large preview
        """
        # INFO - G.M - 2021-10-21 - Page id in pdftocairo begin at 1 instead of 0
        page_id = page_id + 1
        preview_path = "{path}{file_name}{extension}".format(
            file_name=preview_name, path=cache_path, extension=extension
        )
        if page_id > 0:
            # page specific preview
            check_call(
                [
                    PDFTOCAIRO_EXECUTABLE,
                    "-pdf",
                    "-f",
                    str(page_id),
                    "-l",
                    str(page_id),
                    file_path,
                    preview_path,
                ],
                stdout=DEVNULL,
                stderr=STDOUT,
            )
        else:
            # Full preview
            check_call(
                [PDFTOCAIRO_EXECUTABLE, "-pdf", file_path, preview_path],
                stdout=DEVNULL,
                stderr=STDOUT,
            )

    def get_page_number(
        self,
        file_path: str,
        preview_name: str,
        cache_path: str,
        mimetype: typing.Optional[str] = None,
    ) -> int:
        # TODO - G.M - 2021-10-21 - Reintroduce caching here ?
        lines = check_output(["pdfinfo", file_path], stderr=STDOUT, universal_newlines=True).split(
            "\n"
        )
        for line in lines:
            section, data = line.split(":", maxsplit=1)
            if section == "Pages":
                return int(data.strip())
        # FIXME - G.M - 2021-10-21 - Better default case ?
        return 0

    def has_jpeg_preview(self) -> bool:
        return True

    def has_pdf_preview(self) -> bool:
        return True
