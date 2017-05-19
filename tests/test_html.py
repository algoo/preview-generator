import os
from PyPreviewGenerator.manager import PreviewManager
current_dir = os.path.dirname(os.path.abspath(__file__)) +'/'

def test_zip_to_html():
    manager = PreviewManager(path=current_dir + 'cache')
    path_to_file = manager.get_html_preview(
        file_path=current_dir + 'the_zip.zip'
    )
    assert os.path.exists('a/fake/path') == False
    assert os.path.exists(path_to_file) == True
    assert os.path.getsize(path_to_file) > 0
