'''
Created on 02/giu/2015

@author: koala
'''

import gobject
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
        self.savePosition = 0
        
        self.connect('changed', self.verifyNoModification)
        self.connect('apply-tag', self.emitChanged)
        self.connect('remove-tag', self.emitChanged)
    
    def setSavePosition(self):
        print ("Change in setSavePosition")
        self.savePosition = len(self.undo_stack)    
    
    def verifyNoModification(self, dummy):
        if (self.savePosition == len(self.undo_stack)):
            self.stop_emission("changed")
            self.emit("reset_modify")
        
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

gobject.type_register(undobufferrich)
gobject.signal_new("reset_modify", undobufferrich, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ())