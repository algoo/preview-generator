import os
from PyPreviewGenerator.manager import PreviewManager
current_dir = os.path.dirname(os.path.abspath(__file__)) +'/'

def test_odt_to_pdf():
    manager = PreviewManager(
        path=current_dir + 'cache',
        create_folder=True
    )
    path_to_file = manager.get_pdf_preview(
        file_path=current_dir + 'the_odt.odt',
        page=1,
    )
    assert os.path.exists(path_to_file) == True
    assert os.path.getsize(path_to_file) > 0

def test_odt_to_pdf_no_page():
    manager = PreviewManager(
        path=current_dir + 'cache',
        create_folder=True
    )
    path_to_file = manager.get_pdf_preview(
        file_path=current_dir + 'the_odt.odt',
    )
    assert os.path.exists(path_to_file) == True
    assert os.path.getsize(path_to_file) > 0
