# -*- coding: utf-8 -*-

from datetime import date
from datetime import datetime
from json import JSONEncoder
from subprocess import check_call
from subprocess import DEVNULL
from subprocess import STDOUT
import typing

from preview_generator.exception import ExecutableNotFound


def get_subclasses_recursively(
        _class: type,
        _seen: set=None
) -> typing.Generator:
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
        raise TypeError('itersubclasses must be called with '
                        'new-style classes, not %.100r' % _class)
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

    def __str__(self):
        return '{}x{}'.format(self.width, self.height)

class CropDims(object):
    def __init__(self, left: int, top: int, right: int, bottom: int) -> None:
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

    def __str__(self):
        return '({},{}) x ({},{})'.format(self.left, self.top, self.right, self.bottom)


def compute_resize_dims(dims_in: ImgDims, dims_out: ImgDims) -> ImgDims:
    """
    Compute resize dimensions for transforming image in format into
    image out format. This is related to a crop operation which will allow
    to transform ratio from image in into a given ratio.
    :param dims_in:
    :param dims_out:
    :return:
    """
    img_ratio_in = (dims_in.width / dims_in.height)
    img_ratio_out = (dims_out.width / dims_out.height)

    if img_ratio_in > img_ratio_out:
        size_ratio = dims_out.width / dims_in.width
    else:
        size_ratio = dims_out.height / dims_in.height

    return ImgDims(
        width=round(dims_in.width * size_ratio),
        height=round(dims_in.height * size_ratio)
    )


def compute_crop_dims(dims_in: ImgDims, dims_out: ImgDims) -> CropDims:

    left = round((dims_in.width / 2) - (dims_out.width / 2))
    upper = round((dims_in.height / 2) - (dims_out.height / 2))
    right = left + dims_out.width
    lower = upper + dims_out.height

    return CropDims(
        left=left,
        top=upper,
        right=right,
        bottom=lower
    )

def check_executable_is_available(executable_name: str) -> bool:
    """
    Check if an executable is available in execution environment.
    Exemple:
      - try to execute 'pdf2jpeg --version',
      - raises ExecutableNotFound if the call fails
    :param executable_name:
    :return:
    """
    try:
        result = check_call(
            [executable_name, '--version'],
            stdout=DEVNULL,
            stderr=STDOUT
        )
        if result == 0:
            return True

    except Exception as e:
        print('Error while checking dependencies: ', e)
        raise ExecutableNotFound

    return False


class PreviewGeneratorJsonEncoder(JSONEncoder):
    def default(self, obj: typing.Any) -> str:
        if isinstance(obj, bytes):
            try:
                return obj.decode('ascii')
            except:
                return ''

        if isinstance(obj, (datetime, date)):
            serial = obj.isoformat()
            return serial

        return JSONEncoder.default(self, obj)
