# -*- coding: utf-8 -*-
"""
This program creates a dictionary of sets with one key for each street type
found in the input OSM file and the street names associated to each street type.
Additionally, a dictionary with the number of occurrences for each street type
is provided.

Python version: 3.6.0
"""

import sys
import re
import codecs
import xml.etree.cElementTree as ET
from collections import defaultdict


def add_street_type(street_types, street_name, street_type_re):
    """Creates a new entry in the dictionary with the street name"""
    
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        street_types[street_type].add(street_name)


def count_elems(dict_in):
    """Produces a dictionary with the number of occurrences on each dictionary key"""
    
    counter = defaultdict(int)
    for key, values in dict_in.items():
        counter[key] = len(values)
    
    return counter


# ================================================== #
#               Main Function                        #
# ================================================== #
def get_street_types(osm_file, street_type_re):
    """Creates a dictionary of sets with the street types as keys and the 
       street names as values, and another dictionary with the total number
       of streets for each street type"""
    
    with codecs.open(osm_file, "r", encoding="utf-8") as osm:

        street_types = defaultdict(set)
        for event, elem in ET.iterparse(osm, events=("start",)):

            if (elem.tag == "node") or (elem.tag == "way"):
                for tag in elem.iter("tag"):
                    if tag.attrib["k"] == 'addr:street':
                        add_street_type(street_types, tag.attrib["v"], street_type_re)
    
    street_types_count = count_elems(street_types)
    
    return (street_types, street_types_count)


if __name__ == '__main__':
    """Defines the required variables if the code is launched in stand-alone mode"""
    
    OSM_FILE = sys.argv[1]
    st_type_re = re.compile(r'\S+\b', re.IGNORECASE)
    st_types, st_types_count = get_street_types(OSM_FILE, st_type_re)