#!/usr/bin/python
#
# This script converts a presentation made in inkscape and saved
# as SVG to a PDF presentation.
#
# Invoke the script on the command line with:
#
#  compile_presv2.py <yoursvgname.svg>
#
# This is done by converting layers in the SVG to individual pdf files
# and merging them. Merging will only be done if the 'pdftk' program is
# available. This would be done manually with the command:
#
#  pdftk slide*.pdf output presentation.pdf
#
# The script has a few assumptions:
#
# 1. Slide labeled "TITLE" is the first slide of the presentation (the title
#    slide, obviously)
#
# 2. The master slide (the template for the presentation) is after the title
#    slide
#
# 3. The final "thank you" slide is labelled "END"
#
# 4. Additional layer/slide labelled "STOP" is put after "END" and possible
#    backup slides, so the script knows when to stop.
#
# 5. A layer labelled "NUMBER" may also be placed somewhere after "STOP".
#    It should contain only a text element positioned appropriately as a
#    placeholder for the slide number text. The Label property of this
#    text object should be changed to "slidenumber" (this will already be
#    set in the template svg). If you need to change it, click on the text
#    object and go to Object->Object Properties. The text can be anything
#    you like, pyscape will search for "NS" in the text and replace it
#    with the slide number if it is found. pyscape will also search for
#    "NT" and replace this with the total number of slides in the
#    presentation. e.g. the text "Slide NS of NT" would become
#    "Slide 02 of 10" for slide 2 of a 10 slide presentation.
#    The number text will not appear on the title slide.
#

import xml.etree.ElementTree as xmltree
import sys
import os
import subprocess
import shutil
import glob
import tempfile
import distutils.spawn

nargs = len(sys.argv)

# the svg file to work on
input_fname = str(sys.argv[1])

# temp files directory
tempdir = os.path.join (tempfile.gettempdir(), 'slides')

# make sure temp slide directory is cleared of old files by deleting it
# and all contents
if os.path.exists(tempdir):
    shutil.rmtree(tempdir)

# create the empty directory again
os.makedirs(tempdir)

# define temp name for svg, you don't really need to worry about this
tmp_fname = os.path.join (tempdir, 'temppi.svg')

# define some parameters
label = "{http://www.inkscape.org/namespaces/inkscape}label" #namespace for inkscape label
name = 'slidenumber' #just the name of the slidenumber quantity

def is_svg(filename):
    tag = None
    with open(filename, "r") as f:
        try:
            for event, el in xmltree.iterparse(f, ('start',)):
                tag = el.tag
                break
        except xmltree.ParseError:
            pass

    return tag == '{http://www.w3.org/2000/svg}svg'


if os.path.exists(input_fname):

    if is_svg (input_fname) == False:
        # it's not svg
        print ('The input file:\n{}\ndoes not appear to be a valid svg file.').format (input_fname)
        sys.exit()

    else:
        # read the svg file as XML tree
        tree = xmltree.parse(input_fname)
        root = tree.getroot()

else:
    print ('The input file:\n{}\ncould not be found').format (input_fname)
    sys.exit()

# loop through layers looking for NUMBER slide layer
foundNumberElement = False

for child in root:

    child.set('style','display:none')

    if child.get(label) == 'NUMBER':

        print ('Found NUMBER slide, now looking for label containing {}').format (name)

        numberlayer = child

        for subchild in child.iter():

            if subchild.tag == '{http://www.w3.org/2000/svg}text':

                print ('found text tag')

                print (subchild.attrib)

                labelFound = True
                try:
                    #idcontents = subchild.attrib['id']
                    labelcontents = subchild.attrib[label]

                except KeyError, e:
                    labelFound = False

                #if subchild.get('name')==name:
                if labelFound and (labelcontents == name):

                    print ('found label with contents {}').format (name)

                    tspans = subchild.findall('{http://www.w3.org/2000/svg}tspan')

                    number = tspans[0]
                    slide_num_text = tspans[0].text

                    print ('Template slide_num_text is: ' + slide_num_text)

                    #print (number)

                    foundNumberElement = True

                    break

            if foundNumberElement == True:
                break

        if foundNumberElement == False:

            print ('Number text element not found!')

        break

#sys.exit ()
#    if child.get(label)='NUMBER'):

# count the slides
num_slides = 0
for child in root:

    if child.get(label)=='STOP':

        break

    if child.get(label)=='TITLE':

        num_slides = 1
        continue

    if child.get(label)=='MASTER':
        continue

    elif child.get(label)=='END':

        num_slides = num_slides + 1
        continue

    elif num_slides > 0:

        num_slides = num_slides + 1

slide_counter = -1
print ('Beginning pdf creation ...')
print ('Creating individual slide pdf files in temporary directory:\n%s' % tempdir)

# ensure number layer is not displayed until we decide to
if numberlayer is not None:
    numberlayer.set('style','display:none')

for child in root:

    print (child.get(label))
#    print child.keys()
#    print child.items()
    if child.get(label) == 'STOP':

        print ('Found STOP, ending processing')
        break

    if child.get(label) == 'TITLE':

        print ('Processing TITLE')

        child.set('style','display:inline')
        tree.write(tmp_fname)
        subprocess.call(['inkscape','-A', os.path.join(tempdir, 'slide00.pdf'), tmp_fname])
        child.set('style','display:none')
        slide_counter = 1
        continue

    if child.get(label) == 'MASTER':

        print ('Found MASTER')
        child.set('style','display:inline')

        if foundNumberElement:
            numberlayer.set('style','display:inline')

    elif child.get(label) == 'END':

        print ('slide {:d}'.format(slide_counter))

        if foundNumberElement:

            temp_text = slide_num_text

            temp_text = temp_text.replace ('NS', '{:02d}'.format (slide_counter))
            temp_text = temp_text.replace ('NT', '{:d}'.format (num_slides))

            number.text = temp_text

            numberlayer.set('style','display:none')

        child.set('style','display:inline')
        tree.write(tmp_fname)
        subprocess.call(['inkscape','-A', os.path.join(tempdir, ('slide%02d.pdf' % slide_counter)), tmp_fname])
        child.set('style','display:none')
        slide_counter = slide_counter + 1

    elif slide_counter > 0:

        print ('Processing slide {:02d}'.format (slide_counter))

        if foundNumberElement:

            temp_text = slide_num_text

            temp_text = temp_text.replace ('NS', '{:02d}'.format (slide_counter))
            temp_text = temp_text.replace ('NT', '{:d}'.format (num_slides))

            number.text = temp_text

            print (number.text)

        #number.text = ('{:02d}'.format (slide_counter))

        child.set('style','display:inline')
        tree.write(tmp_fname)
        subprocess.call(['inkscape','-A', os.path.join(tempdir, ('slide%02d.pdf' % slide_counter)), tmp_fname])
        child.set('style','display:none')
        slide_counter = slide_counter + 1

# get the list of individual slide pdf files
tmplist = glob.glob(os.path.join(tempdir, 'slide*.pdf'))

# sort the file names so the slides are in the right order
tmplist.sort ()

# this works in python 2.7
pdftkloc = distutils.spawn.find_executable ('pdftk')

if pdftkloc is not None:
    print ('Combining slide pdfs into single pdf using pdftk')

    # use pdftk to catenate the pdfs into one
    subprocess.call(['pdftk'] + tmplist + ['output', 'presentation.pdf'])
    #pdftk in1.pdf in2.pdf cat output out1.pdf
    #tree.write('drawing2.svg')

    print ('Deleting temporary files')

    # clean up
    shutil.rmtree(tempdir)

else:
   print ('Cannot join individual slide pdfs into single pdf as pdftk program is not found.')
   print ('You will find the individual slide pdfs in the directory:\n%s.' % tempdir)

print ('Finished!')


