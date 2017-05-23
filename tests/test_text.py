import os
from PyPreviewGenerator.manager import PreviewManager
current_dir = os.path.dirname(os.path.abspath(__file__)) +'/'

def test_text_to_text():
    manager = PreviewManager(
        path=current_dir + 'cache',
        create_folder=True
    )
    path_to_file = manager.get_text_preview(
        file_path=current_dir + 'the_text.txt'
    )
    assert os.path.exists(path_to_file) == True
    assert os.path.getsize(path_to_file) > 0

def test_zip_to_text():
    manager = PreviewManager(
        path=current_dir + 'cache',
        create_folder=True
    )
    path_to_file = manager.get_text_preview(
        file_path=current_dir + 'the_zip.zip'
    )
    assert os.path.exists(path_to_file) == True
    assert os.path.getsize(path_to_file) > 0