'''
Created on 20/giu/2015

@author: koala
'''

import gtk

NBW_NOT_SELECTED = 0
NBW_SELECTED = 1

class noteBrowserWidget(object):
    '''
    classdocs
    '''
    
    def __init__(self, gladeFile, NoteStore):
        '''
        Constructor
        '''
        self.gladefile = gladeFile
        self.builder = gtk.Builder()
        self.builder.add_from_file(self.gladefile)
        
        self.NoteStore = NoteStore
        
        # Note selection widget
        self.tw = self.builder.get_object("noteTreeView")
        self.tw.set_model(self.NoteStore)
        self.tw.expand_all()
        self.tw.connect("row-activated", self.rowActivated)
        
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Title", renderer, text=0)
        column2 = gtk.TreeViewColumn("ID", renderer, text=1)
        self.tw.append_column(column)
        self.tw.append_column(column2)

        self.dl = self.builder.get_object("noteBrowse")
        
    def run(self):
        # It show the selection widget and wait for the user action.
        # Returns 0 if no selection or selection ID
        # self.piter stores the iter pointer to the selected items in NoteStore
        retVal = 0 # No selection
        self.tw.expand_all()
        if (self.dl.run() == 1):
            # Selected
            self.piter = self.tw.get_selection().get_selected()[1]
            retVal = self.NoteStore.get_value(self.piter,1)
        else:
            #Not Selected
            pass
        self.dl.hide()
        return retVal
    
    def rowActivated(self, treeview, path, view_column):
        self.dl.emit("response", 1)