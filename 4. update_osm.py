#!/usr/bin/env python2
# -*- coding: utf-8 -*-

'''
    Create new XML file with corrections from audit results
    
    References:
    https://discussions.udacity.com/t/changing-attribute-value-in-xml/44575/6    
    http://stackoverflow.com/questions/3095434/inserting-newlines-in-xml-file-generated-via-xml-etree-elementtree-in-python
    Udacity Project 4; Lesson 13 Part 10
'''

import xml.etree.ElementTree as ET
import re
from collections import defaultdict
import pprint

OSM_FILE = "toronto_map_updated4.osm"  # Original XML file
SAMPLE_FILE = "toronto_map_updated5.osm" # New XML file
city_mapping = {"City of Brampton":"Brampton","City of Pickering":"Pickering","City of Toronto":"Toronto","City of Vaughan":"Vaughan","North York, Toronto":"North York","York, Toronto":"York","toronto":"Toronto","Town of Ajax":"Ajax","Town of Markham":"Markham","City of Markham":"Markham","City of Vaughan (Maple)":"Vaughan","Etoicoke":"Etobicoke","Toronto, ON":"Toronto","Toronto;City of Toronto":"Toronto","Torontoitalian":"Toronto","Vaughan (Concord)":"Vaughan", "Vaughan (Woodbridge)":"Vaughan","Willowdale":"North York","markham":"Markham","vaughan":"Vaughan"}
province_mapping = {'Ontario':'ON'}
street_mapping = {"Lan":"Lane","Ave":"Avenue","Ave.":"Avenue",'avenue':'Avenue',"Blvd":"Boulevard","Blvd.":"Boulevard",'Ct':'Court','Dr':'Drive','dr':'Drive',"E":"East","E.":"East",'N':'North','Rd':'Road','rd':'Road',"road":"Road",'S':'South','St':'Street','St.':'Street','street':'Street','st':'Street','st.':'Street','Trl':'Trail','Terace':'Terrace','W':'West','W.':'West','west':'West','Pkwy':'Parkway','Pl':'Place'}
post_type_re = re.compile('\s')

''' Postal Code '''
# Checks if postal codes have spaces in them or not and return fixed postal code
def audit_postcode(postal_code):
    m = post_type_re.search(postal_code) #searches for a match to the post_type_re regular expression
    if m: #if a match is found (space)
        #postcode_types['Space'].add(postal_code) #add the postal code to the set of 'Space' postal codes
        new_pc = postal_code
    elif len(postal_code)==5: #if a match is not found (no space)
        new_pc = postal_code[0:3]+' '+postal_code[3:6] # update the postal code to create a space
        #postcode_types['No Space'].add(postal_code) #add the postal code to the set of 'No Space' postal codes
    else:
        new_pc = 'Wrong Postal Code'
    return new_pc 

''' Street Names '''
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
expected_streets = ["Way","Cottages","Downs","Outlook","Unionville","Wishbone","Woods",'Avenue','Boulevard','Brookstone','Circle','Close','Concession','Court','Crescent','Drive','East','Fernway','Gardens','Gate','Lane','Line','North','Place','Plaza','Road','South','Street','Terrace','Trail','West',"Ames","Avellino","Borghese","Briarway","Campanile","Chart","Chase","Circuit","Cove","Creekway","Crossing","End","Glenn","Green","Grove","Heights","Hill","Hills","Italia","Keep","Lanes","Esplanade","Crest","Islands","Lawn","Mall","Manor","Meadows","Mews","Oaks","Orchard","Park","Path","Point","Promenade","Quay","Ridge","Rise","Row","Run","Shores","Square","Teodoro","Toscana","Walk","Wood","Wynd","Woodlands","Warden","Vista","View","Valley","Vale","Thicket","Townline","Pleasant","Pines","Peachcrest","Palisades","Maple","Keanegate","Hollow","Glade","Elms","Croft","Bend","Acres"]#      
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

def update_name(street_name, mapping):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        try:
            street_name = street_name.replace(street_type,mapping[street_type])
        except:
            pass
        #print street_name
    return street_name
  
''' 
    Update OSM File 

    Fix city names, postal codes, province values, and street names
'''

match_hashtag_re = re.compile(r'#\w*$',re.IGNORECASE)

def get_element(osm_file, street_names,tags=('node', 'way', 'relation')):
    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            if elem.tag == 'way' or elem.tag == 'node':
                for tag in elem.iter('tag'):
                    
                    # Finds and fixes city names
                    if tag.attrib['v'] in city_mapping:
                        tag.set('v', city_mapping[tag.attrib['v']])
                
                    # Fixes postal codes
                    if tag.attrib['k'] == "addr:postcode":
                        tag.set('v', audit_postcode(tag.attrib['v']))
                    
                    # Changes state key to province
                    if tag.attrib['k'] == "addr:state":
                        tag.set('k', 'addr:province')
                       
                    if tag.attrib['k'] == "addr:province" and tag.attrib['v'] in province_mapping:
                        tag.set('v',province_mapping[tag.attrib['v']])
                    
                    # Finds and fixes street names
                    if tag.attrib['k'] == "addr:street":
                        street_name = tag.attrib['v']
                        m = street_type_re.search(street_name)
                        if m:
                            street_type = m.group()
                            if street_name in street_names[street_type]:
                                try:
                                    if len(street_name.split(',')) > 1: # should deal with all , Suite or , Ste or , Floor numbers
                                        street_name = street_name.split(',')[0]
                                    elif "Hwy" in street_name:
                                        street_name = street_name.replace("Hwy","Highway")
                                    elif re.search(r'#\w*$',street_name): # removes anything with ' #...'
                                        m = re.search(r'#\w*$',street_name)
                                        part_to_remove = ' '+m.group()
                                        street_name = street_name.replace(part_to_remove,'')
                                    #elif (', Suite' in street_name) or (', Ste' in street_name): # removes Suite or Ste numbers
                                    #    street_name = street_name.split(',')[0]
                                    elif re.search('\s\b*[Uu]nit',street_name): #removes Unit or unit numbers
                                        street_name = re.split('\s*[Uu]nit',street_name)[0]
                                    elif 'Floor' in street_name: #removes , Floor and Floor numbers
                                        #if len(street_name.split(',')) > 1:
                                        #    street_name = street_name.split(',')[0]
                                        #else:
                                        street_split = street_name.split(' ')
                                        street_split.remove(street_split[-1])
                                        street_split.remove(street_split[-1])
                                        street_name = ' '.join(street_split)
                                    elif ' St. ' in street_name:
                                        street_name = street_name.replace('St.','Street')
                                        if street_type == "W" or street_type == "E.":
                                            street_name = street_name.replace(street_type,street_mapping[street_type])
                                    elif (' St ' in street_name) or (' St. ' in street_name) or (' st ' in street_name) or (' st. ' in street_name) or (' ST ' in street_name): #replaces mid string abreviations
                                        street_name = street_name.replace(' St ' or ' St. ' or ' st ' or ' st. ' or ' ST ',' Street ')
                                    elif ' Dr ' in street_name: #replaces mid string abreviations
                                        street_name = street_name.replace(' Dr ',' Drive ')
                                    elif ' Ave ' in street_name: #replaces mid string abreviations
                                        street_name = street_name.replace(' Ave ',' Avenue ')
                                    else:
                                        #if none of the above, then replace based on mapping
                                        street_name = street_name.replace(street_type,street_mapping[street_type]) #Lesson 13, Part 10
                                    print street_name
                                except:
                                    pass
                                    #print 'pass ==>'+street_name
                                tag.set('v',street_name)
            yield elem
            root.clear()

if __name__ == "__main__":  
    street_names = audit_streetnames(OSM_FILE) # audit street names to create a dictionary of unexpected names
    #pprint.pprint(dict(street_names))

    # create a new file and write the updated tag values to this file
    with open(SAMPLE_FILE, 'w') as output:
        output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        output.write('<osm>\n  ')
        # run the function get_element on each element in the xml file
        for i, element in enumerate(get_element(OSM_FILE,street_names)):
            output.write(ET.tostring(element, encoding='utf-8'))
        output.write('</osm>')
       