import os
from PyPreviewGenerator.manager import PreviewManager
current_dir = os.path.dirname(os.path.abspath(__file__)) +'/'

manager = PreviewManager(path=current_dir + 'cache')
path_to_file = manager.get_text_preview(
    file_path=current_dir + 'the_zip.zip',
)

print('Preview created at path : ', path_to_file)