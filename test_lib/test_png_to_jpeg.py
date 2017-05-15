import os
from PyPreviewGenerator.manager import PreviewManager
current_dir = os.path.dirname(os.path.abspath(__file__)) +'/'

manager = PreviewManager(path=current_dir + 'cache')
path_to_file = manager.get_jpeg_preview(
    file_path=current_dir + 'the_png.png',
    height=512,
    width=512,
)

print('Preview created at path : ', path_to_file)