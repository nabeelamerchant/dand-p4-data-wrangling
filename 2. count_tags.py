#!/usr/bin/env python2
# -*- coding: utf-8 -*-
'''
 Find the number and types of tags in the open street maps file
 
 Code was modified from quiz submission in Lesson 13, Part 3
'''

import xml.etree.ElementTree as ET
import pprint

osmFile = "toronto_map"


def get_root(fname):
    tree = ET.parse(fname)
    return tree.getroot() 

# Main function in section 1
def count_tags(filename):
        root = get_root(filename)
        data = {} # dictionary to count the total number of each type of tag
        data[root.tag] = 1
        for child in root: # iterates through the different child tags in the file
            if child.tag not in data: # if a tag name doesn't exist in the dictionary:
                data[child.tag] = 1
            else:
                data[child.tag] = data[child.tag] + 1 # add a count to the tag name
            for grandchild in child: # repeat process for embedded tags
                if grandchild.tag not in data:
                    data[grandchild.tag] = 1
                else:
                    data[grandchild.tag] = data[grandchild.tag] + 1
        return data 
    
if __name__ == "__main__":
    tags = count_tags(osmFile) # runs function count_tags
    pprint.pprint(tags) # prints results