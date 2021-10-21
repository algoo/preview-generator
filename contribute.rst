===============================
Contribute to Preview-generator
===============================

--------------------
Adding new feature :
--------------------

Before all, I'd be glad if you could share your new feature with everybody. So if you want to, you can fork it on github ( https://github.com/algoo/preview-generator) (see `Developer’s Kit`_) and submit new features.

If you want to add a new preview builder to handle documents of type **foo** into **jpeg** (for example) here is how to proceed :

 - **Warning** If you need to look at other builders to find out how to proceed, avoid looking at any of the Office to something. It is a particular case and could misslead you.
 - Create a new class FooPreviewBuilder in a file foo_preview.py in preview_generator/preview
 - Make him inherit from the logical PreviewBuilder class
   * if it handles several pages it will be `class FooPreviewBuilder(PreviewBuilder)`
   * for single page it will be `class FooPreviewBuilder(OnePagePreviewBuilder)`
   * etc
 - define your own `build_jpeg_preview(...)` (in the case we want to make **foo** into **jpeg**) based on the same principle as other build\_{type}_preview(...)
 - Inside this build_jpeg_preview(...) you will call a method file_converter.foo_to_jpeg(...)
 - Define your foo_to_jpeg(...) method in preview_generator.preview.file_converter.py

   * inputs must be a stream of bytes and optional informations like a number of pages, a size, ...
   * output must also be a stream of bytes
 - Maybe you'll need to redefine some methods like `get_page_number()` or `exists_preview()` in your FooPreviewBuilder class


---------------
Developer’s Kit
---------------

--------------------
Installation (dev) :
--------------------


From scratch on a terminal :
  - create your project directory (we will name it "the_project" but you can name it the way you want) : `mkdir the_project`
  - `cd the_project`
  - `git clone https://github.com/algoo/preview-generator`
  - building your environment :
     * install python virtualenv builder : `sudo apt install python3-venv`
     * build your virtual env (env will be called "myenv", you can name it the way you want): `python3 -m venv myenv`
     * if it's not already, activate it : `source myenv/bin/activate`. (`deactivate` to deactivate)
  - install dependencies :
    * `apt-get install poppler-utils libfile-mimeinfo-perl libimage-exiftool-perl ghostscript libsecret-1-0 zlib1g-dev libjpeg-dev`
    * `pip install -e ".[dev, all]"`
    * install external apt dependencies for specific builder (see README.md)


-----------------
Code Convention :
-----------------

When using subclass of generic abstract class, convention is to prefix it with name
of the generic abstract class. For example:

    ImagePreviewBuilderIMConvert(ImagePreviewBuilder)

---------------
Running Tests :
---------------

 Pytest is a motor for unit testing

* `pip install -e '.[testing]'`
* go into the "tests" directory : `cd path/to/you/project/directory/tests`
* run `pytest`

---------------
Others checks :
---------------

Run mypy checks:

     mypy --ignore-missing-imports --disallow-untyped-defs .

Code formatting using black:

     black -l 100 preview_generator setup.py build_supported_mimetypes_table_rst.py tests

Sorting of import:

     `isort tests/**/*.py preview_generator/**/*.py setup.py build_supported_mimetypes_table_rst.py`

Flake8 check(unused import, variable and many other checks):

    flake8 preview_generator setup.py build_supported_mimetypes_table_rst.py tests

------------
Contribute :
------------

install preview_generator with dev dependencies (contains tests dependencies)

   pip install -e '.[dev]'

install pre-commit hooks:

  pre-commit install

Launch test :

  pytest

You now can commit and see if pre-commit is ok with your change.
