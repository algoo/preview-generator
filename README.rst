==================================
Preview\_generator's Documentation
==================================


Old repository : https://pypi.python.org/pypi/PyPreviewGenerator/0.1.20

------------
Presentation
------------

This module allows to generate jpeg, pdf, text or html preview for virtually any kind of files including a cache management.
It allows to generate preview for a given page and put it in cache. The context of creation of this module (as an example of use context) was for **Tracim**, a github project (https://github.com/Tracim/tracim) where users can put file on a
repository in order to share it with other users. The only way to find a file was with his name. Hence it was decided to generate previews of the files in order to ease the location of one. **Only works on Linux**.

It is distributed with MIT license (https://choosealicense.com/licenses/mit/)

--------------
Format handled
--------------


+-----------------------+-----------+--------+--------+--------+-------+
|                       |   JPEG    |  PDF   | TEXT   | HTML   |  JSON |
+=======================+===========+========+========+========+=======+
| PNG                   |    ☑      |        |        |        |   ☑   |
+-----------------------+-----------+--------+--------+--------+-------+
| JPEG                  |    ☑      |        |        |        |   ☑   |
+-----------------------+-----------+--------+--------+--------+-------+
| BMP                   |    ☑      |        |        |        |   ☑   |
+-----------------------+-----------+--------+--------+--------+-------+
| GIF                   |    ☑      |        |        |        |   ☑   |
+-----------------------+-----------+--------+--------+--------+-------+
| PDF                   |    ☑      |        |        |        |       |
+-----------------------+-----------+--------+--------+--------+-------+
| Zip files             |           |        |   ☑    |   ☑    |   ☑   |
+-----------------------+-----------+--------+--------+--------+-------+
| Office files          |       ☑   |   ☑    |        |        |       |
| (word, LibreOffice)   |           |        |        |        |       |
+-----------------------+-----------+--------+--------+--------+-------+
| Text                  |           |        |   ☑    |        |       |
+-----------------------+-----------+--------+--------+--------+-------+


------------
Installation
------------

`pip install preview-generator`


-----------
Requirement
-----------

Some packages are needed but may also be already on your OS. You can check if they are already installed or you can just try to install preview-generator and if the `pip install preview-generator` command fails, do :

`apt-get install zlib1g-dev`

`apt-get install libjpeg-dev`

and try `pip install preview-generator` again.

This package uses several libraries :

  - wand
  - python-magick
  - pillow
  - PyPDF2

These should be automatically installed with the `pip install preview-generator` command. But if some error occurs quoting one of these library, try to install them 1 by 1 with a simple `pip install ...` to locate the library that causes the problem.

**WARNING!** about **LibreOffice**

If you want to use the conversion from an office file to pdf or jpeg, ensure that **LibreOffice** is already installed on the computer because the conversion is made by the Libreoffice's export feature.

LibreOffice's download page : https://fr.libreoffice.org/download/libreoffice-stable/


-----
Usage
-----

Getting a preview
-----------------

.. code:: python

  from preview-generator.manager import PreviewManager
  manager = PreviewManager(path='/home/user/Pictures/', create_folder= True)
  path_to_file = manager.get_jpeg_preview(
    file_path='/home/user/Pictures/myfile.gif',
    height=100,
    width=100,
  )
  print('Preview created at path : ', path_to_file)




The preview manager
-------------------

.. code:: python

  preview_manager = PreviewManager(cache_path)

*args :*

   *cache_path : a String of the path to the directory where the cache file will be stored*
   *create_folder : a boolean, when True will TRY to create the cache folder*

*returns :*

  *a PreviewManager Object*

The builders
------------

Here is the way it is meant to be used assuming that cache_path is an existing directory

For Office types into PDF :
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

  preview_manager = PreviewManager(cache_path)
  preview = preview_manager.get_pdf_preview(file_path,page=page_id)

-> Will create a preview from an office file into a pdf file

*args :*

  *file_path : the String of the path where is the file you want to get the preview*

  *page : the int of the page you want to get. If not mentioned all the pages will be returned. First page is page 0*

  *use_original_filename : a boolean that mention if the original file name should appear in the preview name. True by default*

*returns :*

  *a FileIO stream of bytes of the pdf preview*

For images(GIF, BMP, PNG, JPEG, PDF) into jpeg :
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

  preview_manager = PreviewManager(cache_path)
  preview = preview_manager.get_jpeg_preview(file_path,height=1024,width=526)

-> Will create a preview from an image file into a jpeg file of size 1024 * 526

*args :*

  *file_path : the String of the path where is the file you want to get the preview*

  *height : height of the preview in pixels*

  *width : width of the preview in pixels. If not mentioned, width will be the same as height*

  *use_original_filename : a boolean that mention if the original file name should appear in the preview name. True by default*

*returns :*

  *a FileIO stream of bytes of the jpeg preview*

Other conversions :
~~~~~~~~~~~~~~~~~~~

The principle is the same as above

**Zip to text or html :** will build a list of files into texte/html inside the json

**Office to jpeg :** will build the pdf out of the office file and then build the jpeg.

**Text to text :** mainly just a copy stored in the cache


---------------
Cache mechanism
---------------


Naming :
--------

The name of the preview generated in the cache directory will be :

{file_name}-[{size}-]{file_md5sum}[({page})]{extension}
  file_name = the name of the file you asked for a preview without the extension.

  size = the size you asked for the preview. In case of a Jpeg preview.

  file_md5sum = the md5sum of the entire path of the file. To avoid conflicts like files that have the same name but are in different directory.

  page = the page asked in case of pdf or office document preview.

  extensions = the extension of the preview (.jpeg for a jpeg, .txt for a text, etc)


Example :
---------

These scripts :

GIF to JPEG :
~~~~~~~~~~~~~


.. code:: python

  import os
  from preview-generator.manager import PreviewManager
  current_dir = os.path.dirname(os.path.abspath(__file__)) +'/'

  manager = PreviewManager(path=current_dir + 'cache')
  path_to_file = manager.get_jpeg_preview(
      file_path=current_dir + 'the_gif.gif',
      height=512,
      width=512,
  )

  print('Preview created at path : ', path_to_file)

will print

  Preview created at path : the_gif-512x512-60dc9ef46936cc4fff2fe60bb07d4260.jpeg

ODT to JPEG :
~~~~~~~~~~~~~

.. code:: python

  import os
  from preview-generator.manager import PreviewManager
  current_dir = os.path.dirname(os.path.abspath(__file__)) +'/'

  manager = PreviewManager(path=current_dir + 'cache')
  path_to_file = manager.get_jpeg_preview(
      file_path=current_dir + 'the_odt.odt',
      page=1,
      height=1024,
      width=1024,
  )

  print('Preview created at path : ', path_to_file)

will print

  Preview created at path : the_odt-1024x1024-c8b37debbc45fa96466e5e1382f6bd2e-page1.jpeg

ZIP to Text :
~~~~~~~~~~~~~
.. code:: python

  import os
  from preview-generator.manager import PreviewManager
  current_dir = os.path.dirname(os.path.abspath(__file__)) +'/'

  manager = PreviewManager(path=current_dir + 'cache')
  path_to_file = manager.get_text_preview(
      file_path=current_dir + 'the_zip.zip',
  )

  print('Preview created at path : ', path_to_file)

will print

  Preview created at path : the_zip-a733739af8006558720be26c4dc5569a.txt


--------------------
Adding new feature :
--------------------

Before all, I'd be glad if you could share your new feature with everybody. So if you want to, you can fork it on github ( https://github.com/algoo/preview-generator) (see `Developer’s Kit`_) and submit new features.

If you want to add a new preview builder to handle documents of type **foo** into **jpeg** (for example) here is how to proceed :

 - **Warning** If you need to look at other builders to find out how to proceed, avoid looking at any of the Office to something. It is a particular case and could misslead you.
 - Create a new class FooPreviewBuilder in a file foo_preview.py in preview-generator/preview
 - Make him inherit from the logical PreviewBuilder class

   * if it handles several pages it will be `class FooPreviewBuilder(PreviewBuilder)`
   * for single page it will be `class FooPreviewBuilder(OnePagePreviewBuilder)`
   * ...
 - define your own `build_jpeg_preview(...)` (in the case we want to make **foo** into **jpeg**) based on the same principle as other build_{type}_preview(...)
 - Inside this build_jpeg_preview(...) you will call a method file_converter.foo_to_jpeg(...)
 - Define your foo_to_jpeg(...) method in preview-generator.file_converter.py

   * inputs must be a stream of bytes and optional informations like a number of pages, a size, ...
   * output must also be a stream of bytes
 - Maybe you'll need to redefine some methods like `get_page_number()` or `exists_preview()` in your FooPreviewBuilder class


---------------
Developer’s Kit
---------------


Installation (dev) :
--------------------


From scratch on a terminal :
  - create your project directory (we will name it "the_project" but you can name it the way you want) : `mkdir the_project`
  - `cd the_project`
  - `git clone https://github.com/algoo/preview-generator`
  - building your environment :
     * install python virtualenv builder : `sudo apt install python3-venv`
     * build your virtual env (I can say that it work with python 3.4 but did not try with other versions)(env will be called "myenv", you can name it the way you want): `python3.4 -m venv myenv`
     * if it's not already, activate it : `source myenv/bin/activate`. (`deactivate` to deactivate)
  - install dependencies :
     * `apt-get install zlib1g-dev`
     * `apt-get install libjpeg-dev`
     * `pip install wand`
     * `pip install python-magick`
     * `pip install pillow`
     * `pip install PyPDF2`
     * if you use python 3.5 or less `pip install typing`

Running Pytest :
----------------
 Pytest is a motor for unit testing

* `pip install pytest`
* go into the "tests" directory : `cd path/to/you/project/directory/tests`
* run `py.test`


