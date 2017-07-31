# -*- coding: utf-8 -*-

from io import BytesIO
import json
import logging
import typing
import zipfile

from preview_generator.utils import PreviewGeneratorJsonEncoder
from preview_generator.preview.generic_preview import OnePagePreviewBuilder

class FileInfo(object):
    FILE = 'file'
    DIR = 'dir'
    UNDEFINED = 'undefined'

    def __init__(self):
        self.last_modification = None
        self.name = ''
        self.type = FileInfo.UNDEFINED
        self.size = 0
        self.size__compressed = 0

    def to_dict(self):
        return {
            'lastModification': self.last_modification,
            'name': self.name,
            'size': self.size,
            'sizeCompressed': self.size__compressed
        }


class ArchiveInfo(object):
    def __init__(self):
        self.files = []  # typing.List[FileInfo]
        self.size = 0
        self.size__compressed = 0
        self.last_modification = None

    @property
    def compression_rate(self) -> float:
        return self.size / self.size__compressed

    @property
    def file_nb(self):
        return len(self.files)

    def to_dict(self):
        return {
            'fileNb': self.file_nb,
            'files': [file.to_dict() for file in self.files],
            'size': self.size,
            'sizeCompressed': self.size__compressed,
            'lastModification': self.last_modification,
            'compressionRate': self.compression_rate
        }

def archive_info_to_text(archive_info: ArchiveInfo) -> str:
    text = ''
    text__files = ''
    for property, value in archive_info.to_dict().items():
        if property == 'files':
            for file in value:
                text__files += '- {}: {} ({})\n'.format(
                    file['name'],
                    file['sizeCompressed'],
                    file['size']
                )
        else:
            text += '{}: {}\n'.format(property, value)

    text += 'files:\n'
    text += text__files
    return text


def archive_info_to_html(archive_info: ArchiveInfo) -> str:
    html = ''
    html__files = ''
    for property, value in archive_info.to_dict().items():
        if property == 'files':
            for file in value:
                html__files += '<li><b>{name}</b>:<ul><li>Size: {sizeCompressed}</li><li>Original size: {size}</li></ul>\n'.format(
                    name=file['name'],
                    sizeCompressed=file['sizeCompressed'],
                    size=file['size']
                )
        else:
            html += '<li>{}: {}</li>\n'.format(property, value)

    html += 'files:\n'
    html += html__files
    final_html = '<ul>{properties}<li>Files:<ul>{files}</ul></ul>'.format(
        properties=html,
        files=html__files
    )
    return final_html


class ZipPreviewBuilder(OnePagePreviewBuilder):
    @classmethod
    def get_supported_mimetypes(cls) -> typing.List[str]:
        return [
            'application/x-compressed',
            'application/x-zip-compressed',
            'application/zip',
            'multipart/x-zip',
            'application/x-tar',
            'application/x-gzip',
            'application/x-gtar',
            'application/x-tgz',
        ]

    def build_text_preview(
            self,
            file_path: str,
            preview_name: str,
            cache_path: str,
            page_id: int = 0,
            extension: str = '.txt'
    ) -> None:
        """
        generate the text preview
        """
        with open(file_path, 'rb') as filestream:
            logging.info('Converting zip to text')
            zip = zipfile.ZipFile(filestream)
            info = self.zipfile_to_infos(zip)
            text_content = archive_info_to_text(info)

        cache_file_path = cache_path + preview_name + extension
        with open(cache_file_path, 'w') as file_handle:
            file_handle.write(text_content)

    def build_html_preview(
            self,
            file_path: str,
            preview_name: str,
            cache_path: str,
            extension: str = '.html'
    ) -> None:
        """
        generate the text preview
        """
        with open(file_path, 'rb') as filestream:
            logging.info('Converting zip to html')
            zip = zipfile.ZipFile(filestream)
            info = self.zipfile_to_infos(zip)
            text_content = archive_info_to_html(info)

        cache_file_path = cache_path + preview_name + extension
        with open(cache_file_path, 'w') as file_handle:
            file_handle.write(text_content)

    def build_json_preview(self, file_path: str, preview_name: str,
                           cache_path: str, page_id: int = 0,
                           extension: str = '.json') -> None:
        """
        generate the json preview
        """
        json_string = ''
        with open(file_path, 'rb') as filestream:
            logging.info('Converting zip to json')
            zip = zipfile.ZipFile(filestream)
            info = self.zipfile_to_infos(zip)

            json_string = json.dumps(
                info.to_dict(),
                cls=PreviewGeneratorJsonEncoder
            )

        cache_file_path = cache_path + preview_name + extension
        with open(cache_file_path, 'w') as json_file_handle:
            json_file_handle.write(json_string)

    def zipfile_to_infos(self, zipfile: zipfile.ZipFile) -> ArchiveInfo:
        archive_info = ArchiveInfo()
        for ziplineinfo in zipfile.infolist():
            fileinfo = FileInfo()
            from datetime import datetime
            fileinfo.last_modification = datetime(
                year=ziplineinfo.date_time[0],
                month=ziplineinfo.date_time[1],
                day=ziplineinfo.date_time[2],
                hour=ziplineinfo.date_time[3],
                minute=ziplineinfo.date_time[4],
                second=ziplineinfo.date_time[5]
            )

            fileinfo.name = ziplineinfo.filename
            fileinfo.size = ziplineinfo.file_size
            fileinfo.size__compressed = ziplineinfo.compress_size
            # if info.is_dir():
            #     fileinfo.type = FileInfo.DIR
            # else:
            #     fileinfo.type = FileInfo.FILE
            archive_info.files.append(fileinfo)

            archive_info.size += fileinfo.size
            archive_info.size__compressed += fileinfo.size__compressed
            if not archive_info.last_modification \
                    or archive_info.last_modification < fileinfo.last_modification:
                archive_info.last_modification = fileinfo.last_modification

        return archive_info


# INFO - D.A. - 2017-06-29
#
# The following previewer must be implemented but is not at all at the moment
#
#
#  class TargzPreviewBuilder(OnePagePreviewBuilder):
#     mimetype = ['application/gzip',
#                 'application/gtar',
#                 'application/tgz',
#                 ]
#
#     def build_text_preview(self, file_path: str, preview_name: str,
#                            cache_path: str, page_id: int = 0,
#                            extension: str = '.txt') -> None:
#         """
#         generate the text preview
#         """
#         raise Exception("Not implemented for tar gz document")
#
#     def build_html_preview(self, file_path: str, preview_name: str,
#                           cache_path: str, extension: str = '.html') -> None:
#         """
#         generate the text preview
#         """
#         raise Exception("Not implemented for tar gz document")
#
#     def build_json_preview(self, file_path: str, preview_name: str,
#                            cache_path: str, page_id: int = 0,
#                            extension: str = '.json') -> None:
#         """
#         generate the json preview
#         """
#         raise Exception("Not implemented for tar gz document")
#
#


def zip_to_html(zip: typing.IO[bytes]) -> BytesIO:
    logging.info('Converting zip to html')
    zz = zipfile.ZipFile(zip)  # type: ignore
    output = BytesIO()
    output.write(str.encode('<p><ul>'))
    for line, info in enumerate(zz.infolist()):
        date = "%d-%02d-%02d %02d:%02d:%02d" % info.date_time[:6]
        output.write(
            str.encode(
                '<li>file {line}</li>'
                '<ul>'
                '<li>name : {name}</li>'
                '<li>size : {size}</li>'
                '<li>date : {date}</li>'
                '</ul>'.format(
                    line=line,
                    name=info.filename,
                    size=info.file_size,
                    date=date,
                    )
            )
        )
    output.write(str.encode('</ul></p>'))
    output.seek(0, 0)
    return output
