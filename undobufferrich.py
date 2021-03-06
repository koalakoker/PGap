'''
Created on 02/giu/2015

@author: koala
'''

import undobuffer

class undobufferrich(undobuffer.UndoableBuffer):
    '''
    Extends Undoable buffer with formatting
    '''

    def __init__(self, text, tagTable = None):
        '''
        Constructor
        '''
        undobuffer.UndoableBuffer.__init__(self, tagTable)
        self.begin_not_undoable_action()
        self.set_text(text)
        self.end_not_undoable_action()
        
        self.connect('apply-tag', self.emitChanged)
        self.connect('remove-tag', self.emitChanged)
                
    def emitChanged(self, dummy1 = None, dummy2 = None, dummy3 = None, dummy4 = None):
        self.emit("changed")
                
    def isBlockTagged(self, tag, start, end):
        # return True if all char in the buffer from start to end is tagged with tag, else False
        retVal = True
#         print tag
        l = end.get_offset()-start.get_offset()
        # Try catch
        for i in range(l):
            appliedTag =  start.get_tags()
            found = False
            for t in appliedTag:
                if (t == tag):
                    found = True
            if not (found):
                retVal = False
            start.forward_char()
        return retVal
    
    def toggleTag(self, tag, start, end):
        if not (self.isBlockTagged(tag, start.copy(), end)):
            self.apply_tag(tag, start, end)
        else:
            self.remove_tag(tag, start, end)
                
    def addLink(self, tag_link, tag_link_hidden, start, end, link):
        self.apply_tag(tag_link, start, end)
        self.insert_with_tags(end, link, tag_link_hidden)
        
    def removeLink(self, tag_link, tag_link_hidden, start):
        # Check if link tag is selected
        if not (self.isTagSelected(start, tag_link)):
            return
        
        # find tag bounds
        localStart = start.copy()
        localEnd = start.copy()
        
        localStart.backward_to_tag_toggle(tag_link)
        localEnd.forward_to_tag_toggle(tag_link)
        self.remove_tag(tag_link, localStart, localEnd)
        localStart.forward_to_tag_toggle(tag_link_hidden)
        localEnd.forward_to_tag_toggle(tag_link_hidden)
        self.delete(localStart,localEnd)
        
    def getLink(self, tag_link, tag_link_hidden, start):
        # Check if link tag is selected
        if not (self.isTagSelected(start, tag_link)):
            return
        
        if (self.isTagSelected(start, tag_link_hidden)):
            return
        
        localStart = start.copy() 
        
        localStart.forward_to_tag_toggle(tag_link_hidden)
        localEnd = localStart.copy()
        localEnd.forward_to_tag_toggle(tag_link_hidden)
        return self.get_text(localStart, localEnd)
        
    def isTagSelected(self, start, tag):
        tags = start.get_tags()
        retVal = False
        if (tag in tags):
            retVal = True
        return retVal
    
    def isInternalLink(self, link):
        if (link[0] == '#'):
            return True
        else:
            return False
        
    def getNoteIDFromLink(self, link):
        NoteID = link[1:]
        return int(NoteID)