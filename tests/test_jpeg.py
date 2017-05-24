import os
from preview_generator.manager import PreviewManager
from PIL import Image
current_dir = os.path.dirname(os.path.abspath(__file__)) +'/'

def test_gif_to_jpeg():
    manager = PreviewManager(
        path=current_dir + 'cache',
        create_folder=True
    )
    path_to_file = manager.get_jpeg_preview(
        file_path=current_dir + 'the_gif.gif',
        height=512,
        width=512,
    )
    assert os.path.exists(path_to_file) == True
    assert os.path.getsize(path_to_file) > 0
    with Image.open(path_to_file) as jpeg:
        assert jpeg.height == 512
        assert jpeg.width == 512

def test_gif_to_jpeg_no_size():
    manager = PreviewManager(
        path=current_dir + 'cache',
        create_folder=True
    )
    path_to_file = manager.get_jpeg_preview(
        file_path=current_dir + 'the_gif.gif',
    )
    assert os.path.exists(path_to_file) == True
    assert os.path.getsize(path_to_file) > 0
    with Image.open(path_to_file) as jpeg:
        assert jpeg.height == 256
        assert jpeg.width == 256


def test_png_to_jpeg():
    manager = PreviewManager(
        path=current_dir + 'cache',
        create_folder=True
    )
    path_to_file = manager.get_jpeg_preview(
        file_path=current_dir + 'the_png.png',
        height=512,
        width=512
    )
    assert os.path.exists(path_to_file) == True
    assert os.path.getsize(path_to_file) > 0
    with Image.open(path_to_file) as jpeg:
        assert jpeg.height == 512
        assert jpeg.width == 512

def test_png_to_jpeg_no_size():
    manager = PreviewManager(
        path=current_dir + 'cache',
        create_folder=True
    )
    path_to_file = manager.get_jpeg_preview(
        file_path=current_dir + 'the_png.png',
    )
    assert os.path.exists(path_to_file) == True
    assert os.path.getsize(path_to_file) > 0
    with Image.open(path_to_file) as jpeg:
        assert jpeg.height == 256
        assert jpeg.width == 256

def test_bmp_to_jpeg():
    manager = PreviewManager(
        path=current_dir + 'cache',
        create_folder=True
    )
    path_to_file = manager.get_jpeg_preview(
        file_path=current_dir + 'the_bmp.bmp',
        height=512,
        width=512
    )
    assert os.path.exists(path_to_file) == True
    assert os.path.getsize(path_to_file) > 0
    with Image.open(path_to_file) as jpeg:
        assert jpeg.height == 512
        assert jpeg.width == 512

def test_bmp_to_jpeg_no_size():
    manager = PreviewManager(
        path=current_dir + 'cache',
        create_folder=True
    )
    path_to_file = manager.get_jpeg_preview(
        file_path=current_dir + 'the_bmp.bmp',
    )
    assert os.path.exists(path_to_file) == True
    assert os.path.getsize(path_to_file) > 0
    with Image.open(path_to_file) as jpeg:
        assert jpeg.height == 256
        assert jpeg.width == 256

def test_pdf_to_jpeg():
    manager = PreviewManager(
        path=current_dir + 'cache',
        create_folder=True
    )
    path_to_file = manager.get_jpeg_preview(
        file_path=current_dir + 'the_pdf.pdf',
        height=512,
        width=512
    )
    assert os.path.exists(path_to_file) == True
    assert os.path.getsize(path_to_file) > 0
    with Image.open(path_to_file) as jpeg:
        assert jpeg.height == 512
        assert jpeg.width == 512

def test_pdf_to_jpeg_no_size():
    manager = PreviewManager(
        path=current_dir + 'cache',
        create_folder=True
    )
    path_to_file = manager.get_jpeg_preview(
        file_path=current_dir + 'the_pdf.pdf',
    )
    assert os.path.exists(path_to_file) == True
    assert os.path.getsize(path_to_file) > 0
    with Image.open(path_to_file) as jpeg:
        assert jpeg.height == 256
        assert jpeg.width == 256

def test_odt_to_jpeg():
    manager = PreviewManager(
        path=current_dir + 'cache',
        create_folder=True
    )
    path_to_file = manager.get_jpeg_preview(
        file_path=current_dir + 'the_odt.odt',
        height=512,
        width=512,
        page=1
    )
    assert os.path.exists(path_to_file) == True
    assert os.path.getsize(path_to_file) > 0
    with Image.open(path_to_file) as jpeg:
        assert jpeg.height == 512
        assert jpeg.width == 512

def test_odt_to_jpeg_no_size():
    manager = PreviewManager(
        path=current_dir + 'cache',
        create_folder=True
    )
    path_to_file = manager.get_jpeg_preview(
        file_path=current_dir + 'the_odt.odt',
        page=1
    )
    assert os.path.exists(path_to_file) == True
    assert os.path.getsize(path_to_file) > 0
    with Image.open(path_to_file) as jpeg:
        assert jpeg.height == 256
        assert jpeg.width == 256

def test_odt_to_jpeg_no_page():
    manager = PreviewManager(
        path=current_dir + 'cache',
        create_folder=True
    )
    path_to_file = manager.get_jpeg_preview(
        file_path=current_dir + 'the_odt.odt',
        height=512,
        width=512
    )
    assert os.path.exists(path_to_file) == True
    assert os.path.getsize(path_to_file) > 0
    with Image.open(path_to_file) as jpeg:
        assert jpeg.height == 512
        assert jpeg.width == 512

def test_odt_to_jpeg_no_size_no_page():
    manager = PreviewManager(
        path=current_dir + 'cache',
        create_folder=True
    )
    path_to_file = manager.get_jpeg_preview(
        file_path=current_dir + 'the_odt.odt',
    )
    assert os.path.exists(path_to_file) == True
    assert os.path.getsize(path_to_file) > 0
    with Image.open(path_to_file) as jpeg:
        assert jpeg.height == 256
        assert jpeg.width == 256