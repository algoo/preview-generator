# -*- coding: utf-8 -*-

from io import BytesIO
import json
import logging
import typing
import zipfile

from preview_generator.preview.generic_preview import OnePagePreviewBuilder


class ZipPreviewBuilder(OnePagePreviewBuilder):
    mimetype = ['application/x-compressed',
                'application/x-zip-compressed',
                'application/zip',
                'multipart/x-zip',
                'application/x-tar',
                'application/x-gzip',
                'application/x-gtar',
                'application/x-tgz',
                ]

    def build_text_preview(self, file_path: str, preview_name: str,
                           cache_path: str, page_id: int = 0,
                           extension: str = '.txt') -> None:
        """
        generate the text preview
        """

        with open(file_path, 'rb') as img:
            result = zip_to_txt(img)
            with open(cache_path + preview_name + extension, 'wb') as jpeg:
                buffer = result.read(1024)
                while buffer:
                    jpeg.write(buffer)
                    buffer = result.read(1024)

    def build_html_preview(self, file_path: str, preview_name: str,
                           cache_path: str, extension: str = '.html') -> None:
        """
        generate the text preview
        """

        with open(file_path, 'rb') as img:
            result = zip_to_html(img)
            with open(cache_path + preview_name + extension, 'wb') as jpeg:
                buffer = result.read(1024)
                while buffer:
                    jpeg.write(buffer)
                    buffer = result.read(1024)

    def build_json_preview(self, file_path: str, preview_name: str,
                           cache_path: str, page_id: int = 0,
                           extension: str = '.json') -> None:
        """
        generate the json preview
        """

        with open(file_path, 'rb') as img:
            result = zip_to_json(img)
            with open(cache_path + preview_name + extension, 'wb') as jpeg:
                buffer = result.read(1024)
                while buffer:
                    jpeg.write(buffer)
                    buffer = result.read(1024)


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

def zip_to_txt(zip: typing.IO[bytes]) -> BytesIO:
    logging.info('Converting zip to text')
    zz = zipfile.ZipFile(zip)
    output = BytesIO()
    for line, info in enumerate(zz.infolist()):
        date = "%d-%02d-%02d %02d:%02d:%02d" % info.date_time[:6]
        output.write(str.encode(
            "%-46s %s %12d\n" % (info.filename, date, info.file_size)))
    output.seek(0, 0)
    return output


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


def zip_to_json(zip: typing.IO[bytes]) -> BytesIO:
    logging.info('Converting zip to json')
    zz = zipfile.ZipFile(zip)
    output = BytesIO()
    files = []
    dictionnary = {}
    for line, info in enumerate(zz.infolist()):
        date = '%d-%02d-%02d %02d:%02d:%02d' % info.date_time[:6]
        files.append(dict(name=info.filename, size=info.file_size, date=date))
    dictionnary['files'] = files
    content = json.dumps(dictionnary)
    output.write(str.encode(content))
    output.seek(0, 0)
    return output
