# -*- coding: utf-8 -*-
# python setup.py sdist upload -r pypi


import os
import sys
from typing import List

from preview_generator import infos

py_version = sys.version_info[:2]

try:
    from setuptools import find_packages
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools

    use_setuptools()
    from setuptools import find_packages
    from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

try:
    documentation = open(os.path.join(here, "README.rst")).read()
except IOError:
    documentation = ""
except UnicodeDecodeError:
    documentation = ""

testpkgs = []  # type: List[str]

install_requires = [
    "python-magic",
    "Wand",
    "PyPDF2",
    "pyexifinfo",
    "xvfbwrapper",
    "pathlib",
    "pdf2image",
    "cairosvg",
    "ffmpeg-python",
    "filelock",
]

if py_version <= (3, 5):
    # NOTE - SG - 2021-04-19 - python 3.5 is dropped starting with 8.0.0
    install_requires.append("Pillow<8.0.0")
else:
    install_requires.append("Pillow")

tests_require = ["pytest"]

devtools_require = ["flake8", "isort", "mypy", "pre-commit"]

# add black for python 3.6+
if sys.version_info.major == 3 and sys.version_info.minor >= 6:
    devtools_require.append("black")

if py_version <= (3, 4):
    install_requires.append("typing")

# TODO - G.M - 2019-11-05 - restore vtk as normal requirement, vtk is not compatible
# with current version of vtk see https://gitlab.kitware.com/vtk/vtk/issues/17670,
if py_version < (3, 8):
    install_requires.append("vtk")

setup(
    name="preview_generator",
    version=infos.__version__,
    description=(
        "A library for generating preview (thumbnails, text or json overview) "
        "for file-based content"
    ),
    long_description=documentation,
    author="Algoo",
    author_email="contact@algoo.fr",
    url="https://github.com/algoo/preview-generator",
    download_url=(
        "https://github.com/algoo/preview-generator/archive/release_{}.tar.gz".format(
            infos.__version__
        )
    ),
    keywords=["preview", "preview_generator", "thumbnail", "cache"],
    classifiers=[
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    packages=find_packages(exclude=["ez_setup"]),
    install_requires=install_requires,
    python_requires=">= 3.5",
    include_package_data=True,
    extras_require={"testing": tests_require, "dev": tests_require + devtools_require},
    test_suite="py.test",  # TODO : change test_suite
    tests_require=testpkgs,
    package_data={"preview_generator": ["i18n/*/LC_MESSAGES/*.mo", "templates/*/*", "public/*/*"]},
    entry_points={"console_scripts": ["preview = preview_generator.__main__:main"]},
)
