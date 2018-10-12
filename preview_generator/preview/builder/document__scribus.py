# -*- coding: utf-8 -*-

import os
import logging
import typing
import mimetypes
from io import BytesIO
from subprocess import check_call
from subprocess import DEVNULL
from subprocess import STDOUT
from subprocess import CalledProcessError

from preview_generator.exception import BuilderDependencyNotFound
from preview_generator.preview.builder.document_generic import (
    DocumentPreviewBuilder
)
from preview_generator.preview.builder.document_generic import create_flag_file
from preview_generator.preview.builder.document_generic import (
    write_file_content
)
from xvfbwrapper import Xvfb


SCRIPT_FOLDER_NAME = 'scripts'
SCRIPT_NAME = 'scribus_sla_to_pdf.py'
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT_PATH = os.path.join(parent_dir, SCRIPT_FOLDER_NAME, SCRIPT_NAME)


class DocumentPreviewBuilderScribus(DocumentPreviewBuilder):

    @classmethod
    def check_dependencies(cls) -> bool:
        try:
            # BUG - 2018/09/26 - Basile - using '-v' on scribus >= 1.5 gives
            # the version then crash, using FileNotFoundError to make the diff
            result = check_call(['scribus', '-v'])
            return True
        except FileNotFoundError:
            raise BuilderDependencyNotFound()
        except CalledProcessError:
            return True

    @classmethod
    def get_label(cls) -> str:
        return 'application/vnd.scribus - based on Scribus'

    @classmethod
    def get_supported_mimetypes(cls) -> typing.List[str]:
        return ['application/vnd.scribus']

    def _convert_to_pdf(
        self,
        file_content: typing.IO[bytes],
        input_extension: str,  # example: '.dxf'
        cache_path: str,
        output_filepath: str,
        mimetype: str
    ) -> BytesIO:

        return convert_sla_to_pdf(
            file_content, input_extension,
            cache_path, output_filepath, mimetype
        )


def convert_sla_to_pdf(
    file_content: typing.IO[bytes],
    input_extension: str,  # example: '.dxf'
    cache_path: str,
    output_filepath: str,
    mimetype: str
) -> BytesIO:
    logging.debug('converting file bytes {} to pdf file {}'.format(file_content, output_filepath))  # nopep8
    if not input_extension:
        input_extension = mimetypes.guess_extension(mimetype)
    temporary_input_content_path = output_filepath + input_extension  # nopep8
    flag_file_path = create_flag_file(output_filepath)

    logging.debug('conversion is based on temporary file {}'.format(temporary_input_content_path))  # nopep8

    if not os.path.exists(output_filepath):
        write_file_content(file_content, output_filepath=temporary_input_content_path)  # nopep8
        logging.debug('temporary file written: {}'.format(temporary_input_content_path))  # nopep8
        logging.debug('converting {} to pdf into folder {}'.format(
            temporary_input_content_path,
            cache_path
        ))
        with Xvfb() as xvfb:
            result = check_call(
                [
                    'scribus', '-g', '-py', SCRIPT_PATH,
                    output_filepath, '--', temporary_input_content_path
                ],
                stdout=DEVNULL, stderr=STDOUT
            )

    # HACK - D.A. - 2018-05-31 - name is defined by libreoffice
    # according to input file name, for homogeneity we prefer to rename it
    logging.debug('renaming output file {} to {}'.format(
        output_filepath+'.pdf', output_filepath)
    )

    logging.debug('Removing flag file {}'.format(flag_file_path))
    os.remove(flag_file_path)

    logging.info('Removing temporary copy file {}'.format(temporary_input_content_path))  # nopep8
    os.remove(temporary_input_content_path)

    with open(output_filepath, 'rb') as pdf_handle:
        pdf_handle.seek(0, 0)
        content_as_bytes = pdf_handle.read()
        output = BytesIO(content_as_bytes)
        output.seek(0, 0)
        return output
