'''
Created on 02/giu/2015

@author: koala
'''

import undobuffer

class undobufferrich(undobuffer.UndoableBuffer):
    '''
    Extends Undoable buffer with formatting
    '''

    def __init__(self, text):
        '''
        Constructor
        '''
        undobuffer.UndoableBuffer.__init__(self)
        self.begin_not_undoable_action()
        self.set_text(text)
        self.end_not_undoable_action()
        
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