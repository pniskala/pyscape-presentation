#This script is supposed to convert a presentation made in inkscape and saved as SVG to seprate PDF files. You still need to combine the PDF files with pdftk (for example "pdftk output slide*.pdf output presentation.pdf"). The script has a few assumptions:
#1. Slide labeled "TITLE" is the first slide of the presentation (the title slide, obviously)
#2. The master slide (the template for the presentation) is after the title slide
#3. The final "thank you" slide is labeled "END"
#4. Additional layer/slide labeled "STOP" is put after "END" and possible backup slides, so the script knows when to stop.
#5. A layer labeled "NUMBER" should be plased somewhere after "STOP". It should contain only the text "XY" positioned appropriately as a placeholder for the slide number. If necessary, use the XML editor to modify the name of this text field to "slidenumber".

import xml.etree.ElementTree as et
import sys
import os
import subprocess


#the svg file to work on
input_fname = 'presentation.svg'

#output directoory, make sure this exists
outdir = './slides'

#define temp nime for svg, you don't really need to worry about this
tmp_fname = 'temppi.svg'

#define some parameters
label = "{http://www.inkscape.org/namespaces/inkscape}label" #namespace for inkscape label
name = 'slidenumber' #just the name of the slidenumber quantity

#read the svg file as XML tree
tree = et.parse(input_fname)
root = tree.getroot()

#change directory
os.chdir(outdir)

for child in root:
	child.set('style','display:none')
	if child.get(label)=='NUMBER':
		numberlayer = child
		for subchild in child.iter():
			if subchild.get('name')==name:
				number = subchild
		
#	if child.get(label)='NUMBER'):

slide_counter = -1
print 'Let us start...'
for child in root:
	print child.get(label)
#	print child.keys()
#	print child.items()
	if child.get(label)=='STOP':
#		print 'STOP'
		break
	if child.get(label)=='TITLE':
#		print 'TITLE'
		child.set('style','display:inline')
		tree.write(tmp_fname)
		subprocess.call(['inkscape','-A','slide00.pdf',tmp_fname])
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
		subprocess.call(['inkscape','-A',('slide%02d.pdf' % slide_counter),tmp_fname])
		child.set('style','display:none')
		slide_counter = slide_counter + 1
	elif slide_counter > 0:
		print ('slide %02d' % slide_counter)
		number.text = ('%02d' % slide_counter)
		child.set('style','display:inline')
		tree.write(tmp_fname)
		subprocess.call(['inkscape','-A',('slide%02d.pdf' % slide_counter),tmp_fname])
		child.set('style','display:none')
		slide_counter = slide_counter + 1

print 'Finished!'
#subprocess.call(['pdftk','slide*.pdf','cat output','presis.pdf'])
#pdftk in1.pdf in2.pdf cat output out1.pdf
#tree.write('drawing2.svg')
