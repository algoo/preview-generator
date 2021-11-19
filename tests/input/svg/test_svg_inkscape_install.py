import importlib
import typing
import unittest.mock

import pytest

from preview_generator.preview.builder import image__inkscape as inkscape_builder_module


@pytest.mark.parametrize(
    "side_effect, inkscape_version, options",
    [
        (lambda _: b"Inkscape 1.0", "1.0", inkscape_builder_module.INKSCAPE_100_SVG_TO_PNG_OPTIONS),
        (
            lambda _: b"Inkscape 0.92",
            "0.92",
            inkscape_builder_module.INKSCAPE_0x_SVG_TO_PNG_OPTIONS,
        ),
        (
            FileNotFoundError(),
            "not_installed",
            inkscape_builder_module.INKSCAPE_100_SVG_TO_PNG_OPTIONS,
        ),
    ],
)
def test_inkscape_installation(
    side_effect: typing.Callable, inkscape_version: str, options: typing.Tuple[str, ...]
) -> None:
    with unittest.mock.patch("subprocess.check_output") as check_output_mock:
        check_output_mock.side_effect = side_effect
        builder_module = importlib.reload(inkscape_builder_module)
        builder_class = builder_module.ImagePreviewBuilderInkscape  # type: ignore
        assert inkscape_version in builder_class.dependencies_versions()
        assert builder_module.INKSCAPE_SVG_TO_PNG_OPTIONS == options  # type: ignore
