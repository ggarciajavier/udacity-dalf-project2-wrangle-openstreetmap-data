# -*- coding: utf-8 -*-
"""
This program is meant to read all the different tag types linked to a given
element type (e.g. nodes) contained in the OSM file.

Python version: 3.6.0
"""

import sys
import codecs
import xml.etree.cElementTree as ET
from collections import defaultdict


def count_elems(dict_in):
    """Produces a dictionary with the number of occurrences on each dictionary key"""
    
    counter = defaultdict(int)
    for key, values in dict_in.items():
        counter[key] = len(values)
    
    return counter


# ================================================== #
#               Main Function                        #
# ================================================== #
def get_tags(osm_file, element_type):
    """Saves all the different tags associated to a given element type (node, way) 
    and stores them in a dictionary"""
    
    tag_types = defaultdict(set)
    
    with codecs.open(osm_file, "r", encoding="utf-8") as osm:
        
        for event, elem in ET.iterparse(osm, events=("start",)):
            if (elem.tag == element_type):
                for tag in elem.iter('tag'):
                    tag_types[tag.attrib["k"]].add(tag.attrib["v"])
    
    tag_numbers = count_elems(tag_types)
    
    return tag_types, tag_numbers

if __name__ == '__main__':
    """Defines the required variables if the code is launched in stand-alone mode"""
    
    OSM_FILE = sys.argv[1]
    node_tag_types, node_tag_numbers = get_tags(OSM_FILE, 'node')
    way_tag_types, way_tag_numbers = get_tags(OSM_FILE, 'way')