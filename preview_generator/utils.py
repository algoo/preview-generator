# -*- coding: utf-8 -*-
from datetime import date
from datetime import datetime
from json import JSONEncoder
import os
import shutil
from subprocess import check_call
import tempfile
import typing

from PyPDF2 import PdfFileReader
from wand.version import formats as wand_supported_format

from preview_generator.extension import mimetypes_storage

LOGGER_NAME = "PreviewGenerator"
BLACKLISTED_IMAGEMAGICK_MIME = [
    "image/svg+xml",
    "image/svg",
    "application/pdf",
    "application/x-silverlight",
]
LOCKFILE_EXTENSION = ".lock"
# INFO - G.M - 2020-07-03 if another preview is created for same file,
# this is the default time preview Manager allow waiting for
# the other preview to be generated.
LOCK_DEFAULT_TIMEOUT = 20


def get_subclasses_recursively(_class: type, _seen: set = None) -> typing.Generator:
    """
    itersubclasses(cls)

    Generator over all subclasses of a given class, in depth first order.

    >>> list(get_subclasses_recursively(int)) == [bool]
    True
    >>> class A(object): pass
    >>> class B(A): pass
    >>> class C(A): pass
    >>> class D(B,C): pass
    >>> class E(D): pass
    >>>
    >>> for cls in get_subclasses_recursively(A):
    ...     print(cls.__name__)
    B
    D
    E
    C
    >>> # get ALL (new-style) classes currently defined
    >>> [cls.__name__ for cls in get_subclasses_recursively(object)] # doctest: +ELLIPSIS
    ['type', ...'tuple', ...]
    """

    if not isinstance(_class, type):
        raise TypeError(
            "itersubclasses must be called with " "new-style classes, not %.100r" % _class
        )
    if _seen is None:
        _seen = set()
    try:
        subs = _class.__subclasses__()
    except TypeError:  # fails only when cls is type
        subs = _class.__subclasses__(_class)  # type: ignore
    for sub in subs:
        if sub not in _seen:
            _seen.add(sub)
            yield sub
            for sub in get_subclasses_recursively(sub, _seen):
                yield sub


class ImgDims(object):
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height

    def ratio(self) -> float:
        return self.width / self.height

    def __str__(self) -> str:
        return "{}x{}".format(self.width, self.height)


class MimetypeMapping(object):
    def __init__(self, mimetype: str, file_extension: str) -> None:
        self.mimetype = mimetype
        self.file_extension = file_extension

    def __str__(self) -> str:
        return "MimetypeMapping:{}:{}".format(self.mimetype, self.file_extension)


class CropDims(object):
    def __init__(self, left: int, top: int, right: int, bottom: int) -> None:
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

    def __str__(self) -> str:
        return "({},{}) x ({},{})".format(self.left, self.top, self.right, self.bottom)


def compute_resize_dims(dims_in: ImgDims, dims_out: ImgDims) -> ImgDims:
    """
    Compute resize dimensions for transforming image in format into
    image out format. This is related to a crop operation which will allow
    to transform ratio from image in into a given ratio.
    :param dims_in:
    :param dims_out:
    :return:
    """
    img_ratio_in = dims_in.width / dims_in.height
    img_ratio_out = dims_out.width / dims_out.height

    if img_ratio_in > img_ratio_out:
        size_ratio = dims_out.width / dims_in.width
    else:
        size_ratio = dims_out.height / dims_in.height

    return ImgDims(
        width=round(dims_in.width * size_ratio), height=round(dims_in.height * size_ratio)
    )


def compute_crop_dims(dims_in: ImgDims, dims_out: ImgDims) -> CropDims:

    left = round((dims_in.width / 2) - (dims_out.width / 2))
    upper = round((dims_in.height / 2) - (dims_out.height / 2))
    right = left + dims_out.width
    lower = upper + dims_out.height

    return CropDims(left=left, top=upper, right=right, bottom=lower)


def executable_is_available(
    executable_name: typing.Union[str, typing.List[str], typing.Tuple[str]]
) -> bool:
    """Check if an executable is available in execution environment.

    :param executable_name: List or Tuple, or single command name
    :return: `True` if the exec if found, `False` otherwize
    """
    if isinstance(executable_name, (list, tuple)):
        for _exec_name in executable_name:
            print("_exec_name =", _exec_name)
            if shutil.which(_exec_name) is not None:
                return True
        return False
    return shutil.which(executable_name) is not None


class PreviewGeneratorJsonEncoder(JSONEncoder):
    def default(self, obj: typing.Any) -> str:
        if isinstance(obj, bytes):
            try:
                return obj.decode("ascii")
            except:  # noqa: E722
                return ""

        if isinstance(obj, (datetime, date)):
            serial = obj.isoformat()
            return serial

        return JSONEncoder.default(self, obj)


def get_decrypted_pdf(
    stream: typing.BinaryIO,
    strict: bool = True,
    warndest: typing.TextIO = None,
    overwriteWarnings: bool = True,
) -> PdfFileReader:
    """
    Return a PdfFileReader object decrypted with default empty key (if file is encrypted)
    The signature is taken from PdfFileReader.__init__

    See https://github.com/algoo/preview-generator/issues/52
    which is related to https://github.com/mstamy2/PyPDF2/issues/51

    :param stream:
    :param strict:
    :param warndest:
    :param overwriteWarnings:
    :return:
    """
    pdf = PdfFileReader(stream, strict, warndest, overwriteWarnings)
    if pdf.isEncrypted:
        #  TODO - D.A. - 2018-11-08 - manage password protected PDFs
        password = ""
        try:
            pdf.decrypt(password)
        except NotImplementedError:
            # If not supported, try and use qpdf to decrypt with '' first.
            # See https://github.com/mstamy2/PyPDF2/issues/378
            # Workaround for the "NotImplementedError: only algorithm code 1 and 2 are supported" issue.
            tf = tempfile.NamedTemporaryFile(
                prefix="preview-generator-", suffix=".pdf", delete=False
            )
            tfoname = tf.name + "_decrypted.pdf"
            stream.seek(0)
            tf.write(stream.read())
            tf.close()
            if password:
                check_call(["qpdf", "--password=" + password, "--decrypt", tf.name, tfoname])
            else:
                check_call(["qpdf", "--decrypt", tf.name, tfoname])
            pdf = PdfFileReader(tfoname, strict, warndest, overwriteWarnings)
            os.unlink(tf.name)
            os.unlink(tfoname)
    return pdf


def imagemagick_supported_mimes() -> typing.List[str]:
    all_supported = wand_supported_format("*")
    valid_mime = []  # type: typing.List[str]
    all_imagemagick_mime_supported = []  # type: typing.List[str]

    for supported in all_supported:
        fake_url = "./FILE.{0}".format(supported)  # Fake a url
        mime, enc = mimetypes_storage.guess_type(fake_url)
        if mime and mime not in all_imagemagick_mime_supported:
            all_imagemagick_mime_supported.append(mime)

    for mime in all_imagemagick_mime_supported:
        # INFO - G.M - 2019-11-15 - we drop text file format support (no working correctly)
        if mime.startswith("text/"):
            continue
        # INFO - G.M - 2019-11-15 - we drop video file format support (no working correctly either)
        if mime.startswith("video/"):
            continue
        # HACK - G.M - 2019-11-15 - check if some "chemical" file can be processed as image,
        # now considered them as not supported.
        if mime.startswith("chemical/"):
            continue
        if mime in BLACKLISTED_IMAGEMAGICK_MIME:
            continue
        valid_mime.append(mime)
    return valid_mime
