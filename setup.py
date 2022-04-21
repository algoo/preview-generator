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
    # mimetype_guessing
    "python-magic",
    # wand builder
    "Wand",
    # commons
    "pyexifinfo",
    "filelock",
]

tests_require = ["pytest", "pytest-dotenv", "ImageHash"]
devtools_require = ["flake8", "isort", "mypy", "pre-commit", "black"]
cairo_require = ["cairosvg"]
scribus_require = drawio_require = ["xvfbwrapper"]
video_require = ["ffmpeg-python"]
cad3d_require = ["vtk"]
rawpy_require = ["rawpy"]
all_require = [cairo_require, scribus_require, video_require, drawio_require]

extras_require = {
    "cairosvg": cairo_require,
    "drawio": drawio_require,
    "scribus": scribus_require,
    "video": video_require,
    "3D": cad3d_require,
    "all": all_require,
    "raw": rawpy_require,
    # specials
    "testing": tests_require,
    "dev": tests_require + devtools_require,
}

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
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    packages=find_packages(exclude=["ez_setup"]),
    install_requires=install_requires,
    python_requires=">= 3.7",
    include_package_data=True,
    extras_require=extras_require,
    test_suite="py.test",  # TODO : change test_suite
    tests_require=testpkgs,
    package_data={"preview_generator": ["i18n/*/LC_MESSAGES/*.mo", "templates/*/*", "public/*/*"]},
    entry_points={"console_scripts": ["preview = preview_generator.__main__:main"]},
)
