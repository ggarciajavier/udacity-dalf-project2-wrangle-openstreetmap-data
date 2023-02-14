# -*- coding: utf-8 -*-
"""
Python version: 3.6.0
"""

import sys
import os
import codecs
import xml.etree.cElementTree as ET

OSM_FILE = sys.argv[1]

k = 2 # Parameter: take every k-th top level element
SAMPLE_FILE = (os.path.splitext(OSM_FILE)[0].strip('_full') + '_sample_k' + str(k) + os.path.splitext(OSM_FILE)[-1])


def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag

    Reference:
    http://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python
    """
    context = iter(ET.iterparse(osm_file, events=('start', 'end')))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


with codecs.open(SAMPLE_FILE, 'wb', encoding='utf-8') as output:
    output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    output.write('<osm>\n  ')

    # Write every kth top level element
    for i, element in enumerate(get_element(OSM_FILE)):
        if i % k == 0:
            output.write(ET.tostring(element).decode('utf-8'))

    output.write('</osm>')
