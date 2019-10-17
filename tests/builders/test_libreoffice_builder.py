import io
import os
from pathlib import Path

import magic
import pytest

from preview_generator.exception import InputExtensionNotFound
from preview_generator.preview.builder.office__libreoffice import convert_office_document_to_pdf
from preview_generator.utils import executable_is_available

CACHE_DIR = "/tmp/preview-generator-tests/cache"

if not executable_is_available("libreoffice"):
    pytest.skip("libreoffice is not available.", allow_module_level=True)


def test_convert_office_document_to_pdf__ok__with_input_extension_and_mimetype() -> None:
    content = io.BytesIO(b"Test content")
    output_filepath = CACHE_DIR + "/test.pdf"
    _file = Path(output_filepath)
    assert not _file.exists()
    convert_office_document_to_pdf(
        content,
        cache_path=CACHE_DIR,
        input_extension=".txt",
        mimetype="text/plain",
        output_filepath=output_filepath,
    )
    assert _file.is_file()
    mime = magic.Magic(mime=True)
    assert mime.from_file(output_filepath) == "application/pdf"
    os.remove(output_filepath)


def test_convert_office_document_to_pdf__err__input_extension_not_found() -> None:
    content = io.BytesIO(b"Test content")
    output_filepath = CACHE_DIR + "/test.pdf"
    _file = Path(output_filepath)
    assert not _file.exists()
    with pytest.raises(InputExtensionNotFound):
        convert_office_document_to_pdf(
            content,
            cache_path=CACHE_DIR,
            input_extension="",
            mimetype="",
            output_filepath=output_filepath,
        )
    assert not _file.exists()
