================================
Change log for Preview-generator
================================

----------
0.29 / 2022-21-04
----------

:warning: Support for python<3.6 is deprecated.

Misc
~~~~~
- Remove pillow and imconvert builders
- Drop support for python3.6
- Document issue with old version of libreoffice for spreadsheet #296
- Enhanced the test cases for xcf files

Fixed issues
~~~~~~~~~~~~
- fix aspec ratio issue: https://github.com/algoo/preview-generator/issues/293

----------
0.28 / 2021-11-24
----------

:warning: This release introduce many changes with two of the basic builders changed (image, pdf) and a new one added (raw).

Features
~~~~~~~~

- new Image builder based on Wand (which by the way deprecates Pillow and Imagemagick command line builders): #253
- WebP image format support added to the new Wand builder: #273
- new PDF builder based on poppler-utils (which replace old PDF builder): #192
- new RAW image builder using rawpy: #249

-----------------
0.27 / 2021-11-16
-----------------

Fixed issues
~~~~~~~~~~~~
- Repair loading builders without pytest and make code more explicit/safe about such issue: 47517e5dd2b153f3d541fa95f7e0121a3540a041


-----------------
0.26 / 2021-11-16
-----------------

Fixed issues
~~~~~~~~~~~~

- enforce office mimetypes supported by LibreOffice to avoid unknown mimetype issues related to system specific configuration:  #283

-----------------
0.25 / 2021-10-19
-----------------

Fixed issues
~~~~~~~~~~~~~

- fix issue with inkscape builder as required:  #263

-----------------
0.24 / 2021-10-18
-----------------

Fixed issues
~~~~~~~~~~~~

- add compatibility with inkscape v1: #263

-------------------
0.23 / 2021-06-29
-------------------

Features
~~~~~~~~

- experimental GLTF format support (3d) in vtk builder: cc69ad08ef67517b04afe62d6ed58b2eb00ce9b8
- builders have now a weight permitting to know which builder will be used in case of conflict: #237

Fixed issues
~~~~~~~~~~~~

- many builders dependencies are now optional: #235

-------------------
0.22 / 2021-06-23
-------------------

Fixed issues
~~~~~~~~~~~~

- many builders dependencies are now optionals: #235

-------------------
0.21 / 2021-06-22
-------------------

Fixed issues
~~~~~~~~~~~~

- remove the wand builder from default builders: #235

-------------------
0.20 / 2021-06-10
-------------------

Fixed issues
~~~~~~~~~~~~

- properly kill LibreOffice if the timeout is reached: #231


-------------------
0.19 / 2021-05-24
-------------------

Fixed issues
~~~~~~~~~~~~

- add Python 3.9 support: #227


-------------------
0.18 / 2021-05-06
-------------------

Fixed issues
~~~~~~~~~~~~

- fix PDF support with the new pivot code: #224


-------------------
0.17 / 2021-04-30
-------------------

Fixed issues
~~~~~~~~~~~~

- improve performance by using pivot in the manager: #222


-------------------
0.16.2 / 2021-04-21
-------------------

Fixed issues
~~~~~~~~~~~~

- properly terminate libreoffice processes when an exception is caught


-------------------
0.16.1 / 2021-04-20
-------------------

Fixed issues
~~~~~~~~~~~~

- set a default timeout for the libreoffice processes used during some previews.
  This default timeout can be changed via an environment variable, please see the "Office/Text Document" section in the `<README.rst>`_ file.
