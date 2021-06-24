import subprocess
import typing
from abc import ABC

from preview_generator.preview.generic_preview import ImagePreviewBuilder
import glob
import configparser

from preview_generator.utils import ImgDims


class ThumbnailerBuilder(ImagePreviewBuilder, ABC):
    weight = 0
    mimetypes = []
    execute_command = None
    name = 'Unknown'

    @classmethod
    def get_label(cls) -> str:
        return "{} Thumbnailers Preview Builder".format(cls.name)

    @classmethod
    def get_supported_mimetypes(cls) -> typing.List[str]:
        return cls.mimetypes

    def build_jpeg_preview(
        self,
        file_path: str,
        preview_name: str,
        cache_path: str,
        page_id: int,
        extension: str = ".jpeg",
        size: ImgDims = None,
        mimetype: str = "",
    ) -> None:

        if not size:
            size = self.default_size
        preview_file_path = "{path}{extension}".format(
            path=cache_path + preview_name, extension=extension
        )
        command_template = self.execute_command.split()
        command = []
        for arg in command_template:
            if arg == "%s":
                arg = str(size.width)
            if arg == "%i":
                arg = file_path
            if arg == "%u":
                arg = file_path
            if arg == "%o":
                arg = preview_file_path
            command.append(arg)
        subprocess.check_call(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )


DEFAULT_THUMBNAILERS_DIR = "/usr/share/thumbnailers"
ThumbnailerClasses = []
thumbnailer_file_pattern = DEFAULT_THUMBNAILERS_DIR + "/*.thumbnailer"
files = glob.glob(thumbnailer_file_pattern)
for file in files:
    config = configparser.RawConfigParser()
    config.read(file)
    mimetypes = [mimetype for mimetype in config['Thumbnailer Entry']['MimeType'].split(';') if mimetype]
    execute_command = config['Thumbnailer Entry']['Exec']
    ThumbnailerClasses.append(type('{}ThumbnailerBuilder'.format(file), (ThumbnailerBuilder,), {'mimetypes':mimetypes, 'execute_command': execute_command, 'name': file}))


