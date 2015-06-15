'''
Created on 01/giu/2015

@author: koala
'''

from xml.etree import ElementTree
from xml.etree.ElementTree import Element

defFilename = "test.xml"

class XML():
    
    XML_VERSION_TAG = "Version"
    
    def __init__(self, ver):
        
        self.root = Element('root')
        attr = { self.XML_VERSION_TAG : ver }
        self.root.attrib = attr
        
        self.ver = ver
        
    def addChild(self, tagName , text , parent = None, attr = None):
        if (parent == None):
            parent = self.root
        child = Element(tagName)
        if (attr != None):
            child.attrib = attr
        child.text = text
        parent.append(child)
        return child
        
    def save(self, filename = defFilename):
        tree = ElementTree.ElementTree(self.root)
        tree.write(filename, encoding='utf-8', xml_declaration=True)
        
    def load(self, filename = defFilename):
        tree = ElementTree.parse(filename)
        self.root = tree.getroot()
        self.ver = self.root.attrib[self.XML_VERSION_TAG] 
        
    def visualize(self, node, indent = ""):
        out = indent + node.tag
        if (node.attrib != None):
            out = out + " " + str(node.attrib)
        if (node.text != None):
            out = out + " " + node.text
        print (out)
        for child in node:
            self.visualize(child, indent+"--")
      
if __name__ == '__main__':
    xml = XML()
    xml.addChild("nota", "nota testo")
    print ("Test save")
    xml.visualize(xml.root)
    xml.save()
    print ("Test load")
    xml.load()
    xml.visualize(xml.root)