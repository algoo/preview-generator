# -*- coding: utf-8 -*-

import os

from preview_generator.preview import builder_factory


def test_builder_folder_name_exists() -> None:
    folder_path = builder_factory.get_builder_folder_name()
    assert os.path.exists(folder_path)
    assert os.path.isdir(folder_path)


def test_builder_folder_modules_found() -> None:
    folder_path = builder_factory.get_builder_folder_name()
    modules = builder_factory.get_builder_modules(folder_path)
    assert len(modules) >= 7
    assert "image__imconvert" in modules
    assert "image__pillow" in modules
    assert "office__libreoffice" in modules
    assert "pdf__pypdf2" in modules
    assert "plain_text" in modules
    assert "archive__zip" in modules
    assert "document__sketch" in modules


def test_builder_modules_import_working() -> None:
    folder_path = builder_factory.get_builder_folder_name()
    modules = builder_factory.get_builder_modules(folder_path)
    for module in modules:
        # in case of error, raises an ImportError
        builder_factory.import_builder_module(module)
