# presentscape
A script and a template file file for preparing presentations via Inkscape and Python.

This simple Python script and the associated SVG file represent my workflow for preparing slideshow presentations, mainly for academic purposes. The idea is as follows:

1. Create the presentation using Inkscape based on the template in presentation_template.svg.
2. Convert the slides in the SVG file to PDF files and add the slide numbers using the Python script.
3. Combine the slides (the multiple PDF files) into a presentation (a single PDF file).

How I have structured the presentation according to the template presentation_template.svg:

1. With some exceptions, each layer represents a slide.
2. MASTER layer represents the template for the basic slides.
3. TITLE layer represents the title slide.
4. END layer represents the ending of the main presentation (e.g. the "Thank You & Acknowledgements" slide).
5. STOP indicates the end real ending of the presenation. The contents of the STOP layered are not converted to pdf in the Python script.
6. NUMBER layer defines the placing and the style of the slide numbering that is used by the Python script.
7. The regular slides of the presentation are included as layers between MASTER and END. Feel free to use any labels besides TITLE, MASTER, END, STOP or NUMBER for these layers. The same applies to backup/bonus slides after the official END slide.

to create the presentation from the presentation_template.svg run the following::

    python presentscape.py presentation_template.svg

On Linux, pyscape can also be run like a normal command, so the follwoing works::

    presentscape.py presentation_template.svg

More instructions for creating the slides can be found in the pyscape.py file.

The Python script has been tested using Python 2.7.6. Inkscape template has been tested with Inkscape 0.92.
