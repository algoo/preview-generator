# -*- coding: utf-8 -*-

# python setup.py sdist upload -r pypi


try:
    import logging
    import multiprocessing
    import os
except:
    pass

import sys
py_version = sys.version_info[:2]

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

try:
    documentation = open(os.path.join(here, 'README.rst')).read()
except IOError:
    documentation = ''

testpkgs = []

install_requires = ['python-magic', 'Wand', 'PyPDF2', 'Pillow']

if py_version <= (3, 5):
    install_requires.append("typing")

setup(
    name='preview_generator',
    version='0.1.41',
    description='Generation of file previews',
    long_description=documentation,
    author='Algoo',
    author_email='contact@algoo.fr',
    url='https://github.com/algoo/preview_generator',
    download_url='',
    keywords=['preview', 'preview_generator', 'thumbnail', 'cache'],
    classifiers=['Programming Language :: Python :: 3.4'],
    packages=find_packages(exclude=['ez_setup']),
    install_requires=install_requires,
    python_requires='>= 3.4',
    include_package_data=True,
    test_suite='py.test', #TODO : change test_suite
    tests_require=testpkgs,
    package_data={
        'preview_generator': [
            'i18n/*/LC_MESSAGES/*.mo',
            'templates/*/*',
            'public/*/*'
        ]
    }
)
