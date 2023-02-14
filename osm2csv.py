# -*- coding: utf-8 -*-
"""
The objective of this program is to read an OSM datafile given in XML format,
obtain the information stored in nodes and ways, store the defined fields,
apply the corrections given in the shape_element function and store the data
in the corresponding CSV files.

The code is essentially the one develop for the SQL Case Study in Udacity, with
the addition of the following corrections:
    - Search for street names in "name" tags and change their type to 
      "name:street" if no "addr:street" tag is given for the associated node
      (unless the node is a bus stop).
    - Correct abbreviated street types, e.g. *Avenida* for *Av.*
    - Correct street names given in Spanish to Galician.
    - Add the street type to street names which do not contain it.
    - Discard the postal code if it does not contain a 5-digit code.

Python version: 3.6.0
"""

import sys
import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET
import cerberus

import schema

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


def shape_element(element, mapping, expected_street_types, 
                  node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS):
    """Clean and shape node or way XML element to Python dict"""
    
    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []

    if element.tag == 'node':
        for attrib in node_attr_fields:
            try:
                node_attribs[attrib] = element.attrib[attrib]
            except KeyError:
                node_attribs[attrib] = ''
        
        tags = get_tags(element, tags, mapping, expected_street_types)
        
        return {'node': node_attribs, 'node_tags': tags}
    elif element.tag == 'way':
        for attrib in way_attr_fields:
            try:
                way_attribs[attrib] = element.attrib[attrib]
            except KeyError:
                way_attribs[attrib] = ''
        
        way_id = element.attrib['id']
        for idx, child in enumerate(element.findall('nd')):
            way_nodes.append({'id': way_id,
                              'node_id': child.attrib['ref'],
                              'position': idx})
        
        tags = get_tags(element, tags, mapping, expected_street_types)
        
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


def get_tags(element, tags, mapping, expected_street_types):
    """Get information from secondary tags and correct data if needed"""
    
    node_id = element.attrib['id']
    
    # Set a boolean to True if there is no "addr:street" and if the node is not a bus stop
    change_name_tag = True
    if (len(element.findall(".//tag[@k='addr:street']")) != 0 or 
        len(element.findall(".//tag[@v='bus_stop']")) != 0):
        change_name_tag = False
    
    for child in element.findall('tag'):
        tag_key = child.attrib['k']
        if PROBLEMCHARS.search(tag_key):
            continue
        
        if tag_key == 'name':
            tag_value = child.attrib['v']
            first_word = tag_value.split()[0]
            # Change tag to "name:street" if the first word matches the expected street types and if the boolean is True
            if (first_word in expected_street_types) and (change_name_tag):
                tag_type = tag_key
                key = 'street'
            else: # Keep name value as "name"
                tag_type = tag_key
                key = 'name'
        elif LOWER_COLON.search(tag_key):
            tag_type = tag_key.split(':', 1)[0]
            key = tag_key.split(':', 1)[-1]
            if tag_key == 'addr:street':
                tag_value = update_street_name(child.attrib['v'], mapping)
            elif tag_key == 'addr:city':
                tag_value = correct_city_name(child.attrib['v'])
            elif tag_key == 'addr:postcode':
                tag_value = child.attrib['v']
                if len(tag_value) != 5:
                    continue
            else:
                tag_value = child.attrib['v']
        else:
            tag_value = child.attrib['v']
            key = tag_key
            if 'name' in tag_key:
                tag_type = 'name'
            else:
                tag_type = 'regular'
        
        tags.append({'id': node_id, 
                     'key': key, 
                     'value': tag_value, 
                     'type': tag_type})
    
    return tags


# ================================================== #
#             Correcting Functions                   #
# ================================================== #
def update_street_name(st_name, mapping):
    """Update street name if present in the mapping dictionary provided """
    
    if st_name in mapping.keys():
        st_name = mapping[st_name]

    return st_name


def correct_city_name(city_name):
    """Correct city name if it contains either Coruña or O Temple"""
    
    if re.search("O Temple", city_name):
        city_name = 'O Temple, Cambre'
    elif (re.search("Coruña", city_name)) and not (re.search("A Coruña", city_name)):
        city_name = 'A Coruña'
    
    return city_name


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, mapping, expected_street_types, nodes_path, 
                node_tags_path, ways_path, way_nodes_path, way_tags_path, 
                validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(nodes_path, "w", encoding="utf-8") as nodes_file, \
         codecs.open(node_tags_path, "w", encoding="utf-8") as nodes_tags_file, \
         codecs.open(ways_path, "w", encoding="utf-8") as ways_file, \
         codecs.open(way_nodes_path, "w", encoding="utf-8") as way_nodes_file, \
         codecs.open(way_tags_path, "w", encoding="utf-8") as way_tags_file:

        nodes_writer = csv.DictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = csv.DictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = csv.DictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = csv.DictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = csv.DictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element, mapping, expected_street_types)
            if el:
                if validate is True:
                    validate_element(el, validator)
                
                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    """Defines the required variables if the code is launched in stand-alone mode"""
    
    OSM_FILE = sys.argv[1]
    
    NODES_PATH = 'nodes.csv'
    NODE_TAGS_PATH = 'nodes_tags.csv'
    WAYS_PATH = 'ways.csv'
    WAY_NODES_PATH = 'ways_nodes.csv'
    WAY_TAGS_PATH = 'ways_tags.csv'
    
    expected_street_types = ['Rúa', 'Praza', 'Avenida', 'Rolda', 'Glorieta', 
                             'Travesía', 'Praciña', 'Estrada', 'Paseo', 'Lugar', 
                             'Camiño', 'Cantón', 'Escaleira', 'Costa', 'Escalinata', 
                             'Pasadizo', 'Estreita', 'Vía', 'Vereda', 'Calexón',
                             'Ruela', 'Peirao', 'Rampla', 'Autoestrada',
                             'Autovía']
    
    street_mapping = {'CARRETERA NACIONAL VI KM. 589': 'Estrada Nacional VI Km. 589',
                      'Plaza do Santuario': 'Praza do Santuario',
                      'Calle Cuba': 'Rúa Cuba',
                      'Carretera de A Zapateira': 'Estrada da Zapateira',
                      'Roi Xordo': 'Rúa Roi Xordo',
                      'Rosalía de Castro': 'Rúa Rosalía de Castro',
                      'Anxo senra Fernandez': 'Rúa Anxo Senra Fernández',
                      'Capitán Juan Varela': 'Rúa Capitán Juan Varela',
                      'María Corredoira': 'Rúa María Corredoira',
                      'Av.Mallos': 'Avenida dos Mallos',
                      'Avda Alfonso Molina': 'Avenida Alfonso Molina',
                      'Avd. Ernesto Che Guevara': 'Avenida Ernesto Che Guevara'}
    
    process_map(OSM_FILE, street_mapping, expected_street_types, NODES_PATH, 
                NODE_TAGS_PATH, WAYS_PATH, WAY_NODES_PATH, WAY_TAGS_PATH, 
                validate=False)