# -*- coding: utf-8 -*-

import json
import os
import shutil

from preview_generator.manager import PreviewManager

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = '/tmp/preview-generator-tests/cache'


def setup_function(function):
    shutil.rmtree(CACHE_DIR, ignore_errors=True)


def test_zip_to_text():
    manager = PreviewManager(path=CACHE_DIR, create_folder=True)
    path_to_file = manager.get_text_preview(
        file_path=os.path.join(CURRENT_DIR, 'the_zip.zip')
    )
    assert os.path.exists(path_to_file) == True
    assert os.path.getsize(path_to_file) > 0


def test_zip_to_json():
    manager = PreviewManager(path=CACHE_DIR, create_folder=True)
    path_to_file = manager.get_json_preview(
        file_path=os.path.join(CURRENT_DIR, 'the_zip.zip')
    )
    assert os.path.exists(path_to_file) == True
    assert os.path.getsize(path_to_file) > 0

    data = json.load(open(path_to_file))
    assert data['files']
    assert len(data['files']) == 4
    for _file in data['files']:
        assert _file['date']
        assert _file['name']
        assert _file['size'] > 0


def test_zip_to_html():
    manager = PreviewManager(path=CACHE_DIR, create_folder=True)
    input_filename = 'the_zip.zip'
    path_to_file = manager.get_html_preview(
        file_path=os.path.join(CURRENT_DIR, input_filename),
        use_original_filename=True
    )
    assert os.path.exists(path_to_file)
    assert os.path.getsize(path_to_file) > 0
    assert input_filename.replace('.zip', '') in path_to_file


def test_zip_to_html__no_original_name():
    manager = PreviewManager(path=CACHE_DIR, create_folder=True)

    input_filename = 'the_zip.zip'
    path_to_file = manager.get_html_preview(
        file_path=os.path.join(CURRENT_DIR, input_filename),
        use_original_filename=False
    )
    assert os.path.exists(path_to_file)
    assert os.path.getsize(path_to_file) > 0
    assert input_filename.replace('.zip', '') not in path_to_file

    # test default not to put original file name in cache file
    path_to_file2 = manager.get_html_preview(
        file_path=os.path.join(CURRENT_DIR, input_filename)
    )
    assert os.path.exists(path_to_file)
    assert os.path.getsize(path_to_file) > 0
    assert input_filename.replace('.zip', '') not in path_to_file2

