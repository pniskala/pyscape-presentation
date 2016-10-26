#!/usr/bin/python
#
# This script converts a presentation made in inkscape and saved 
# as SVG to a PDF presentation. This is done by converting layers in 
# the SVG to individual pdf files and merging them. Merging will only 
# be done if the 'pdftk' program is available. This would be done 
# manually with the command:
# 
# pdftk slide*.pdf output presentation.pdf
#
# The script has a few assumptions:
#
# 1. Slide labeled "TITLE" is the first slide of the presentation (the title 
#    slide, obviously)
#
# 2. The master slide (the template for the presentation) is after the title 
#    slide
#
# 3. The final "thank you" slide is labeled "END"
#
# 4. Additional layer/slide labeled "STOP" is put after "END" and possible 
#    backup slides, so the script knows when to stop.
#
# 5. A layer labeled "NUMBER" should be plased somewhere after "STOP". It 
#    should contain only the text "XY" positioned appropriately as a 
#    placeholder for the slide number. If necessary, use the XML editor to 
#    modify the 'name' property of this text field to "slidenumber".


import xml.etree.ElementTree as et
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

# read the svg file as XML tree
tree = et.parse(input_fname)
root = tree.getroot()

for child in root:
	child.set('style','display:none')
	if child.get(label)=='NUMBER':
		numberlayer = child
		for subchild in child.iter():
			if subchild.get('name')==name:
				number = subchild
		
#	if child.get(label)='NUMBER'):

slide_counter = -1
print ('Beginning pdf creation ...')
print ('Creating individual slide pdf files in temporary directory:\n%s' % tempdir)
for child in root:
	print (child.get(label))
#	print child.keys()
#	print child.items()
	if child.get(label)=='STOP':
#		print 'STOP'
		break
	if child.get(label)=='TITLE':
#		print 'TITLE'
		child.set('style','display:inline')
		tree.write(tmp_fname)
		subprocess.call(['inkscape','-A', os.path.join(tempdir, 'slide00.pdf'), tmp_fname])
		child.set('style','display:none')
		slide_counter = 1
		continue
	if child.get(label)=='MASTER':
#		print 'MASTER'
		child.set('style','display:inline')
		numberlayer.set('style','display:inline')
	elif child.get(label)=='END':
		print ('slide %02d' % slide_counter)
		#number.text = ('%02d' % slide_counter)
		numberlayer.set('style','display:none')
		child.set('style','display:inline')
		tree.write(tmp_fname)
		subprocess.call(['inkscape','-A', os.path.join(tempdir, ('slide%02d.pdf' % slide_counter)), tmp_fname])
		child.set('style','display:none')
		slide_counter = slide_counter + 1
	elif slide_counter > 0:
		print ('slide %02d' % slide_counter)
		number.text = ('%02d' % slide_counter)
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


