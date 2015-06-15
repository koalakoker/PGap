'''
Created on 02/giu/2015

@author: koala
'''

import os
    
typeTag = {"Bold": 0, "Underline": 1, "Italic": 2}
statusTag = [False, False, False]
HTMLTagsOpen = ["<b>","<u>","<i>"]
HTMLTagsClose = ["</b>", "</u>" ,"</i>"]

XML_SEPARATOR = "##@@##"

def getTagNames(tags):
    currentTag = []
    for t in tags:
        currentTag.append(t.get_property("name"))
    return currentTag

def iterNext(textBuffer, start, end, istr):
#         print ("iter start = " + str(start.get_offset()) + " end = " + str(end.get_offset()))
    if (start.get_offset() >= end.get_offset()):
        return istr
    
    tags = getTagNames(start.get_tags())
    for tag in typeTag:
        if (statusTag[typeTag[tag]]):
            if not tag in tags:
                istr += HTMLTagsClose[typeTag[tag]]   #"</" + tag + ">"
                statusTag[typeTag[tag]] = False
    for name in tags:
        if not (statusTag[typeTag[name]]):
            istr += HTMLTagsOpen[typeTag[name]]  #   "<" + name + ">"    
            statusTag[typeTag[name]] = True
    pnext = start.copy()
    pnext.forward_to_tag_toggle(None)
    istr += start.get_text(pnext)
    
    return iterNext(textBuffer, pnext, end, istr)

def toHTML(textBuffer, start = None, end = None):
    if (start == None):
        start = textBuffer.get_start_iter()
    if (end == None):
        end = textBuffer.get_end_iter()
    
    outStr = """ <!DOCTYPE HTML>
<html>
<head>
<title>Generated HTM file</title>
</head>

<body>"""        
    outStr += iterNext(textBuffer, start, end, "").replace(os.linesep, '<br>')
    outStr += """</body>

</html> """
    
    return outStr
    
def serialize(textBuffer, start = None, end = None):
    if (start == None):
        start = textBuffer.get_start_iter()
    if (end == None):
        end = textBuffer.get_end_iter()
    myFormat = textBuffer.register_serialize_tagset('my-tagset')
    exported = textBuffer.serialize(textBuffer, myFormat, start, end)

    preambleTxt = exported[:26]
    #lenTxt = strToInt(exported[26:30])
    #skip exported[26:29] beacuse it is binay =  len of text
    text = exported[30:]
    
    exported = preambleTxt + XML_SEPARATOR + text        
    return exported

def deserialize(retTextBuffer, data, start = None):
    dataSplitted = data.split(XML_SEPARATOR,1)
    preambleTxt = dataSplitted[0]
    text = dataSplitted[1]
    data = preambleTxt + intToStr(len(text)) + text
    
    if (start == None):
        start = retTextBuffer.get_start_iter()
    myFormat = retTextBuffer.register_deserialize_tagset('my-tagset')
    retTextBuffer.deserialize(retTextBuffer, myFormat, start, data)
    return retTextBuffer

def formatting(textBuffer, start = None, end = None):
    if (start == None):
        start = textBuffer.get_start_iter()
    if (end == None):
        end = textBuffer.get_end_iter()
        
    exported = start.get_text(end)
    exported = exported.replace('<br>', os.linesep)
    exported = exported.replace('<i>', '"')
    exported = exported.replace('</i>', '"')
    exported = exported.replace('&#33;', '!')
    
    out_file = open("converted","w")
    out_file.write(exported)
    out_file.close()
    
def strToInt(istr):
    # return the value of istr that is a 4 char string with coded binary 32bit int.  ex. 0x00 00 00 1c => 28
    retVal = None
    if (len(istr) == 4):
        retVal = (ord(istr[0]) << 24) + (ord(istr[1]) << 16) + (ord(istr[2]) << 8) + ord(istr[3])
    return retVal

def intToStr(value):
    # return the coded binary 32bit int. Value is integer input. Returned value is a string. ex  28 => 0x00 00 00 1c
    return chr((value >> 24) & 0xFF) + chr((value >> 16) & 0xFF) + chr((value >> 8) & 0xFF) + chr(value & 0xFF)  

def prtHex(istr):
    i = 0
    for c in istr:
        h = format(ord(c), '02x')
        hi = format(i, '02x')
        print (i,hi, c, h)
        i = i + 1
