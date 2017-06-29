# -*- coding: utf-8 -*-

import json
import os
from PIL import Image
import pytest
import shutil

from preview_generator.exception import UnavailablePreviewType
from preview_generator.manager import PreviewManager

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = '/tmp/preview-generator-tests/cache'
IMAGE_FILE_PATH = os.path.join(CURRENT_DIR, 'tt.html')
IMAGE_FILE_PATH = '/home/damien/a_bouger_sur_tracim/ALGOOsas/01_LOGOS/EPS/ALGOO_LOGO_H_seul.eps'
IMAGE_FILE_PATH = '/tmp/mozilla.ps'

def setup_function(function):
    shutil.rmtree(CACHE_DIR)
#
# def test_to_jpeg():
#     manager = PreviewManager(
#         path=CACHE_DIR,
#         create_folder=True
#     )
#     path_to_file = manager.get_jpeg_preview(
#         file_path=IMAGE_FILE_PATH,
#         height=256,
#         width=512,
#         force=True
#     )
#     assert os.path.exists(path_to_file) == True
#     assert os.path.getsize(path_to_file) > 0
#     with Image.open(path_to_file) as jpeg:
#         assert jpeg.height == 256
#         assert jpeg.width == 512

# def test_get_nb_page():
#     manager = PreviewManager(path=CACHE_DIR, create_folder=True)
#     nb_page = manager.get_nb_page(file_path=IMAGE_FILE_PATH)  # FIXME must add parameter force=True/False in the API
#     assert nb_page == 1
#
# def test_to_jpeg__default_size():
#     manager = PreviewManager(path=CACHE_DIR, create_folder=True)
#     path_to_file = manager.get_jpeg_preview(
#         file_path=IMAGE_FILE_PATH,
#     )
#     assert os.path.exists(path_to_file) == True
#     assert os.path.getsize(path_to_file) > 0
#     with Image.open(path_to_file) as jpeg:
#         assert jpeg.height == 256
#         assert jpeg.width == 256

# def test_to_json():
#     manager = PreviewManager(path=CACHE_DIR, create_folder=True)
#     path_to_file = manager.get_json_preview(
#         file_path=IMAGE_FILE_PATH,
#         force=True
#     )
#
#     assert os.path.exists(path_to_file)
#     assert os.path.getsize(path_to_file) > 0
#
#     data = json.load(open(path_to_file))
#     assert data['width'] == 236
#     assert data['height'] == 212
#     assert data['size'] == 8791
#     assert data['mode'] == 'RGB'
#     assert data['info']
#
#     assert data['info']['dpi'] == [72, 72]
#     assert data['info']['jfif_version'] == [1, 1]
#     assert data['info']['jfif'] == 257
#     assert data['info']['jfif_unit'] == 1
#     assert data['info']['progression'] == 1
#     assert data['info']['progressive'] == 1
#     assert data['info']['jfif_density'] == [72, 72]

#
# def test_to_pdf():
#     manager = PreviewManager(path=CACHE_DIR, create_folder=True)
#     with pytest.raises(UnavailablePreviewType):
#         path_to_file = manager.get_pdf_preview(
#             file_path=IMAGE_FILE_PATH,
#             force=True
#         )
