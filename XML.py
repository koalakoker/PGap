'''
Created on 01/giu/2015

@author: koala
'''

from xml.etree import ElementTree
from xml.etree.ElementTree import Element

ver = "1.0"
defFilename = "test.xml"

class XML():
    
    def __init__(self):
        
        self.root = Element('root')
        attr = { "Version" : ver }
        self.root.attrib = attr
        
    def addChild(self, name , text , node = None, attr = None):
        child = Element(name)
        if (attr != None):
            child.attrib = attr
        child.text = text
        if (node == None):
            self.root.append(child)
        else:
            self.node.append(child)
        
    def save(self, filename = defFilename):
        tree = ElementTree.ElementTree(self.root)
        tree.write(filename, encoding='utf-8', xml_declaration=True)
        
    def load(self, filename = defFilename):
        tree = ElementTree.parse('country_data.xml')
        self.root = tree.getroot()
        
    def visualize(self, node, indent = ""):
        #print (indent + node.tag + node.attrib + node.text)
        print (node.tag)
        for child in node:
            self.visualize(child, indent+"  ")
      
if __name__ == '__main__':
    xml = XML()
    xml.addChild("nota", "nota testo")
    xml.visualize(xml.root)
    