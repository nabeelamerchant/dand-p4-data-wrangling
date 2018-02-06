#!/usr/bin/env python2
# -*- coding: utf-8 -*-
'''
 Audit Addresses

 Code was modified from quiz submission in Lesson 13, Part 10
'''

import xml.etree.ElementTree as ET
import pprint
import re
from collections import defaultdict

osmFile = "toronto_map_updated5.osm"  #update filename based on xml file to be audited

''' Street Names '''
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
expected_streets = ["Way","Cottages","Downs","Outlook","Unionville","Wishbone","Woods",'Avenue','Boulevard','Brookstone','Circle','Close','Concession','Court','Crescent','Drive','East','Fernway','Gardens','Gate','Lane','Line','North','Place','Plaza','Road','South','Street','Terrace','Trail','West',"Ames","Avellino","Borghese","Briarway","Campanile","Chart","Chase","Circuit","Cove","Creekway","Crossing","End","Glenn","Green","Grove","Heights","Hill","Hills","Italia","Keep","Lanes","Esplanade","Crest","Islands","Lawn","Mall","Manor","Meadows","Mews","Oaks","Orchard","Park","Path","Point","Promenade","Quay","Ridge","Rise","Row","Run","Shores","Square","Teodoro","Toscana","Walk","Wood","Wynd","Woodlands","Warden","Vista","View","Valley","Vale","Thicket","Townline","Pleasant","Pines","Peachcrest","Palisades","Maple","Keanegate","Hollow","Glade","Elms","Croft","Bend","Acres"]#      
expected_cities = ["Ajax","Brampton","Concord","East York","Etobicoke","Fort Myers","Maple","Markham","Mississauga","North York","Pickering","Richmond Hill","Scarborough","Thornhill","Toronto","Vaughan","West Hill","Woodbridge","York","Agincourt","Dartmouth","Don Mills","Kleinburg","Port Union"]

# Compare the endings of the street names to a list of expected names
def audit_street_type(street_types, street_name):
    if ('way' not in street_name) and ('Via' not in street_name):
        m = street_type_re.search(street_name) #searches for a match to the street_type_re regular expression
        if m: #if a match is found
            street_type = m.group() #assign street_type to the group matched
            if street_type not in expected_streets:
                street_types[street_type].add(street_name) #add the street name to a special list (street_types) if its not in the expected list

# Check to see if the key relates to a street address
def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

# Combines previous two functions to audit street names and returns a list of invalid street names
def audit_streetnames(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)): #parse through the osmfile in pieces where the event that initiates each piece is the 'start' tag
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag): #if the tag in the node or way is a street name
                    audit_street_type(street_types, tag.attrib['v']) #check to see if its a valid street name
    osm_file.close()
    return street_types #return the list of invalid street names

''' Postal Codes '''
post_type_re = re.compile('\s')

# Checks if postal codes have spaces in them or not and return fixed postal code
def audit_postcode(postcode_types, postal_code):
    m = post_type_re.search(postal_code) #searches for a match to the post_type_re regular expression
    if m: #if a match is found (space)
        #postcode_types['Space'].add(postal_code) #add the postal code to the set of 'Space' postal codes
        new_pc = postal_code
    else: #if a match is not found (no space)
        new_pc = postal_code[0:3]+' '+postal_code[3:6] # update the postal code to create a space
        postcode_types['No Space'].add(postal_code) #add the postal code to the set of 'No Space' postal codes
        postcode_types['Fixed'].add(new_pc)
    return new_pc    

# Check to see if the key relates to a postal code
def is_postcode(elem):
    return (elem.attrib['k'] == "addr:postcode")

# Find postal codes in nodes or ways,check to see if they have spaces in them, and return a list the different types of postal codes
def audit_postcodes(osmfile):
    osm_file = open(osmfile, "r")
    postcode_types = defaultdict(set)
    postcode_fixed = []
    for event, elem in ET.iterparse(osm_file, events=("start",)): #parse through the osmfile in pieces where the event that initiates each piece is the 'start' tag
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_postcode(tag): #if the tag in the node or way is a postal code
                    new_pc = audit_postcode(postcode_types, tag.attrib['v']) #check to see if its a valid postal code
                    postcode_fixed.append(new_pc)
    osm_file.close()
    return postcode_types #return the list of the different postal codes

''' City Names '''
# Compare the endings of the city names to a list of expected names
def audit_city_type(city_list,city_name):
    if city_name not in expected_cities:
            city_list[''].add(city_name) #add the city name to a special list (city_list) if its not in the expected list

# Check to see if the key relates to a city name
def is_city_name(elem):
    return (elem.attrib['k'] == "addr:city")

# Combines previous two functions to audit city names and returns a list of invalid city names
def audit_citynames(osmfile):
    osm_file = open(osmfile, "r")
    city_list = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)): #parse through the osmfile in pieces where the event that initiates each piece is the 'start' tag
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_city_name(tag): #if the tag in the node or way is a city name
                    audit_city_type(city_list,tag.attrib['v']) #check to see if its a valid city name
    osm_file.close()
    return city_list #return the list of invalid city names


if __name__ == "__main__":
    
    #runs and prints the output of the functions to audit street names, postal codes, and city names
    
    street_names = audit_streetnames(osmFile)
    pprint.pprint(dict(street_names))
    
    postcode_list = audit_postcodes(osmFile)
    pprint.pprint(dict(postcode_list))
    
    city_list = audit_citynames(osmFile)
    pprint.pprint(dict(city_list))
    