import io
import os
import magic
import pytest

from preview_generator.exception import InputExtensionNotFound
from preview_generator.preview.builder.office__libreoffice import convert_office_document_to_pdf   # nopep8
from pathlib import Path

CACHE_DIR = '/tmp/preview-generator-tests/cache'


def test_convert_office_document_to_pdf__ok__with_input_extension_and_mimetype():
    content = io.BytesIO(b'Test content')
    output_filepath = CACHE_DIR+"/test.pdf"
    file = Path(output_filepath)
    assert not file.exists()
    convert_office_document_to_pdf(
        content,
        cache_path=CACHE_DIR,
        input_extension='.txt',
        mimetype='text/plain',
        output_filepath=output_filepath
    )
    assert file.is_file()
    mime = magic.Magic(mime=True)
    assert mime.from_file(output_filepath) == 'application/pdf'
    os.remove(output_filepath)


def test_convert_office_document_to_pdf__err__input_extension_not_found():
    content = io.BytesIO(b'Test content')
    output_filepath = CACHE_DIR+"/test.pdf"
    file = Path(output_filepath)
    assert not file.exists()
    with pytest.raises(InputExtensionNotFound):
        convert_office_document_to_pdf(
            content,
            cache_path=CACHE_DIR,
            input_extension='',
            mimetype='',
            output_filepath=output_filepath
        )
    assert not file.exists()
