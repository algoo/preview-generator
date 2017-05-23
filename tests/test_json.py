import os
from PyPreviewGenerator.manager import PreviewManager
current_dir = os.path.dirname(os.path.abspath(__file__)) +'/'

def test_image_to_json():
    manager = PreviewManager(
        path=current_dir + 'cache',
        create_folder=True
    )
    path_to_file = manager.get_json_preview(
        file_path=current_dir + 'the_jpeg.jpeg'
    )
    assert os.path.exists(path_to_file) == True
    assert os.path.getsize(path_to_file) > 0

def test_zip_to_json():
    manager = PreviewManager(
        path=current_dir + 'cache',
        create_folder=True
    )
    path_to_file = manager.get_json_preview(
        file_path=current_dir + 'the_zip.zip'
    )
    assert os.path.exists(path_to_file) == True
    assert os.path.getsize(path_to_file) > 0