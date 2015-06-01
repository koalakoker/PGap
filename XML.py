'''
Created on 01/giu/2015

@author: koala
'''

from xml.etree import ElementTree
# from xml.dom import minidom
# import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element

# def prettify(elem):
#     """Return a pretty-printed XML string for the Element.
#     """
#     rough_string = ElementTree.tostring(elem, 'utf-8')
#     reparsed = minidom.parseString(rough_string)
#     return reparsed.toprettyxml(indent="  ")

if __name__ == '__main__':

#     tree = ET.parse('country_data.xml')
#     root = tree.getroot()
#      
#     print root.tag, root.attrib
#      
#     for child in root:
#         print child.tag, child.attrib
#         for value in child:
#             print value.tag, value.attrib, value.text
    
    root = Element('root')
    attr = { "name" : "Gigi" }
    root.attrib = attr
    
    child = Element('child')
    child.text = "Pippino"
    
    root.append(child)
    
#     prettify(root)
    
    tree = ElementTree(root)
    
    tree.write("test.xml", encoding='utf-8', xml_declaration=True)