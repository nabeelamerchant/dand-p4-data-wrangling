#!/usr/bin/env python2
# -*- coding: utf-8 -*-
'''
 Create csv files for each database table based on schema.py
 
 Code from quiz submission in Lesson 13, Part 11
'''
import xml.etree.ElementTree as ET
import pprint
import re
import csv
import codecs
import cerberus
import schema

osmFile = "toronto_map_updated5.osm" #XML file to be converted

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

#Clean and shape node or way XML element to Python dict
def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements
    

    # creates a dictionary for all node and node tag attributes following the schema
    if element.tag == 'node':
        # sets the type and value for each node attribute
        node_attribs['id'] = int(element.attrib['id'])
        node_attribs['lat'] = float(element.attrib['lat'])
        node_attribs['lon'] = float(element.attrib['lon'])
        node_attribs['user'] = element.attrib['user']
        node_attribs['uid'] = int(element.attrib['uid'])
        node_attribs['version'] = element.attrib['version']
        node_attribs['changeset'] = int(element.attrib['changeset'])
        node_attribs['timestamp'] = element.attrib['timestamp']
        
        #creates a list of node tags pertaining to the current node
        for subel in element:
            subel_tag = {}
            fullkey = subel.attrib['k']
            # fixes key values in the node tags that have colons in them
            key_split = fullkey.split(':') #splits the key along ':' values
            if len(key_split) > 1: #if the key splits more than once
                tag_type = key_split[0] #the tag type is the first part
                key = ':'.join(key_split[1:]) #the key is the remaining parts (combined)
            else: #if the key doesn't split
                tag_type = 'regular' #the tag type is 'regular'
                key = key_split[0] #the key is the first part
            # sets the type and value for each node tag attribute
            subel_tag['id'] = int(element.attrib['id'])
            subel_tag['key'] = key
            subel_tag['value'] = subel.attrib['v']
            subel_tag['type'] = tag_type
            tags.append(subel_tag)
        return {'node': node_attribs, 'node_tags': tags}
    # creates a dictionary for all way, way tag, and way node attributes following the schema
    elif element.tag == 'way':
        # sets the type and value for each way attribute
        way_attribs['id'] = int(element.attrib['id'])
        way_attribs['user'] = element.attrib['user']
        way_attribs['uid'] = int(element.attrib['uid'])
        way_attribs['version'] = element.attrib['version']
        way_attribs['timestamp'] = element.attrib['timestamp']
        way_attribs['changeset'] = int(element.attrib['changeset'])
        n = 0
        for subel in element:
            # creates a list of way tags pertaining to the current way
            if subel.tag == 'tag':
                subel_tag = {}
                fullkey = subel.attrib['k']
                key_split = fullkey.split(':')
                if len(key_split) > 1:
                    tag_type = key_split[0]
                    key = ':'.join(key_split[1:])
                else:
                    tag_type = 'regular'
                    key = key_split[0]
                # sets the type and value for each way tag    
                subel_tag['id'] = int(element.attrib['id'])
                subel_tag['key'] = key
                subel_tag['value'] = subel.attrib['v']
                subel_tag['type'] = tag_type
                tags.append(subel_tag)
            # creates a list of way nodes pertaining to the current way
            elif subel.tag == 'nd':
                subel_node = {}
                # sets the type andv alue for each way nodes
                subel_node['id'] = int(element.attrib['id'])
                subel_node['node_id'] = int(subel.attrib['ref'])
                subel_node['position'] = n
                n = n + 1
                way_nodes.append(subel_node)
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


# Helper functions 

# Edit element before saving it
def audit_element():
    pass

# Yield element if it is the right type of tag
def get_element(osm_file, tags=('node', 'way', 'relation')):
    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()

# Raise ValidationError if element does not match schema
def validate_element(element, validator, schema=SCHEMA):
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))

# Extend csv.DictWriter to handle Unicode input
class UnicodeDictWriter(csv.DictWriter, object):
    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# Main function in section 3
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            
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
            

if __name__ == "__main__":
    process_map(osmFile, validate=True)