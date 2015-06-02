'''
Created on 02/giu/2015

@author: koala
'''

import os
    
typeTag = {"Bold": 0, "Underline": 1, "Italic": 2}
statusTag = [False, False, False]
HTMLTagsOpen = ["<b>","<u>","<i>"]
HTMLTagsClose = ["</b>", "</u>" ,"</i>"]

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
    next = start.copy()
    next.forward_to_tag_toggle(None)
    istr += start.get_text(next)
    
    return iterNext(textBuffer, next, end, istr)

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
    
    out_file = open("out.html","w")
    out_file.write(outStr)
    out_file.close()