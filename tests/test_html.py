import os
import shutil

from PyPreviewGenerator.manager import PreviewManager
current_dir = os.path.dirname(os.path.abspath(__file__)) +'/'

def test_zip_to_html_no_cache_creation():
    try:
        shutil.rmtree(current_dir + 'cache')
    except OSError:
        pass

    manager = PreviewManager(
        path=current_dir + 'cache',
        create_folder=False
    )
    path_to_file = ''
    try:
        path_to_file = manager.get_html_preview(
            file_path=current_dir + 'the_zip.zip',
            use_original_filename=False
        )
    except Exception:
        pass
    assert os.path.exists('a/fake/path') == False
    assert os.path.exists(path_to_file) == False

def test_zip_to_html():
    manager = PreviewManager(
        path=current_dir + 'cache',
        create_folder=True,
    )
    path_to_file = manager.get_html_preview(
        file_path=current_dir + 'the_zip.zip'
    )
    assert os.path.exists('a/fake/path') == False
    assert os.path.exists(path_to_file) == True
    assert os.path.getsize(path_to_file) > 0

def test_zip_to_html_no_original_name():
    manager = PreviewManager(
        path=current_dir + 'cache',
        create_folder=True,
    )
    path_to_file = manager.get_html_preview(
        file_path=current_dir + 'the_zip.zip',
        use_original_filename=False
    )

    assert os.path.exists('a/fake/path') == False
    assert os.path.exists(path_to_file) == True
    assert os.path.getsize(path_to_file) > 0

