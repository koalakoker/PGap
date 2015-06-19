'''
Created on 30/mag/2015

@author: koala
'''

import pygtk
pygtk.require('2.0')
import gtk
from gtk import gdk
# import TextBuffer2HTMLConvert
import pango
from NoteModel import NoteModel
import os

class PGapMain:
    
    columnInfo = ('Note title', 'ID', 'Creation Time', 'Last Modify')
    
    def getColumnInfo(self, istr):
        #returns the first showColumn that match istr inside columnInfo
        i = 0
        pos = -1
        for s in self.columnInfo:
            if (s == istr):
                if (pos == -1):
                    pos = i
            i += 1
        return pos

    # close the window and quit
    def delete_event(self, widget=None, event=None, data=None):
        gtk.main_quit()
        return False
    
    def report_signal(self, sender):
        print "Receiver reacts to z_signal"
    
    def __init__(self):
        self.gladefile = "pgapgui.glade"  
        self.builder = gtk.Builder()
        self.builder.add_from_file(self.gladefile)
        self.window = self.builder.get_object("pgapui")
        self.window.resize(1024,600)
        self.window.show_all()
        self.window.connect("delete_event", self.delete_event)
        
        handlers = { "onDeleteWindow": gtk.main_quit,
                     "onNewButton": self.onTestClk,
                     "onDeleteButton": self.onTestClk,
                     "onTestClk": self.onTestClk,
                     "on_ID_toggled": self.updateColumnView,
                     "on_Last modify_toggled": self.updateColumnView,
                     "on_Creation Time_toggled": self.updateColumnView,
                     "keypress": self.onKeyPress,
                     "keyrelease": self.onKeyRelease,
                     "onCursorChanged": self.onNoteSelectionChange,
                     "onNewNote": self.onNewNote,
                     "on_BIU_button_clicked": self.on_BIU_button_clicked,
                     "onSave" : self.onSave,
                     "onSaveAs" : self.onSaveAs,
                     "onOpen" : self.onOpen
                   }
        self.builder.connect_signals(handlers)
            
        #create tagTable
        self.tagTable = gtk.TextTagTable()
        self.tag_bold = gtk.TextTag("Bold")
        self.tag_bold.set_property("weight", pango.WEIGHT_BOLD)
        self.tagTable.add(self.tag_bold)
        self.tag_underline = gtk.TextTag("Underline")
        self.tag_underline.set_property("underline", pango.UNDERLINE_SINGLE)
        self.tagTable.add(self.tag_underline)
        self.tag_italic = gtk.TextTag("Italic")
        self.tag_italic.set_property("style", pango.STYLE_ITALIC)
        self.tagTable.add(self.tag_italic)
        
        # create a TreeStore with one string showColumn to use as the model
        self.NoteStore = NoteModel(self.tagTable)
        self.NoteStore.connect('z_signal', self.report_signal)
        #Populate
#         self.NoteStore.populate()

        # create the TreeView using NoteStore
        self.treeview =  self.builder.get_object("treeview")
        self.treeview.set_model(self.NoteStore)
        
        self.tvcolumn = []
        self.cell = []
        
        for i in range(len(self.columnInfo)):
            # create the TreeViewColumn to display the data
            self.tvcolumn.append(gtk.TreeViewColumn(self.columnInfo[i]))
            # add tvcolumn to treeview
            self.treeview.append_column(self.tvcolumn[i])
            # create a CellRendererText to render the data
            self.cell.append(gtk.CellRendererText())
            # add the cell to the tvcolumn and allow it to expand
            self.tvcolumn[i].pack_start(self.cell[i], True)
            # set the cell "text" attribute to showColumn 0 - retrieve text
            # from that showColumn in NoteStore
            self.tvcolumn[i].add_attribute(self.cell[i], 'text', i)
            # Allow sorting on the showColumn
            self.tvcolumn[i].set_sort_column_id(i)
            # Allow resize of showColumn
            self.tvcolumn[i].set_resizable(True)
        
        # make it searchable
        self.treeview.set_search_column(0)
        
        # Allow drag and drop reordering of rows
        self.treeview.set_reorderable(True)
        
        #update column view accordind glade file
        self.updateColumnView(None)
        
        #Make first column of TreeView editable (Note name)
        col = self.treeview.get_column(0)
        renderer = col.get_cell_renderers()[0]
        renderer.set_property('editable', True)
        renderer.connect('edited', self.cell_edited_callback)
        
        self.textview = self.builder.get_object("textview")
        self.onNoteSelectionChange(self.treeview)
                
        self.keyCtrlPressed = False
        
        self.fileSelected = None
        self.updateTitle(self.fileSelected)
        
        # Clipboard
        self.clipboard = gtk.Clipboard()
        
    def updateTitle(self, fileSelected = None):
        modIndincator = ""
        if (self.NoteStore.modified):
            modIndincator = "*"
        if (fileSelected != None):
            self.window.set_title("PGap - " + fileSelected + modIndincator)
                                        
    def updateColumnView(self, CheckMenuItem):
        for i in range(len(self.columnInfo)):
            itm = self.builder.get_object(self.columnInfo[i])
            if (itm != None):
                self.tvcolumn[i].set_visible(itm.get_active())
                
    def on_BIU_button_clicked(self, button, tag = None):
        if (tag == None):
            # Select Tag from button clicked
            # Note: Tag name must be set in the button label
            tag = self.tagTable.lookup(button.get_label())
            
            try:
                bounds = self.textbuffer.get_selection_bounds()
                
                if len(bounds) != 0:
                    start, end = bounds
                    self.textbuffer.toggleTag(tag, start, end)
                    
            except AttributeError:
                pass
        
            
    
    def onKeyEsc(self):
        bounds = self.textbuffer.get_selection_bounds()
        if len(bounds) != 0:
            tb = self.textbuffer
            tb.select_range(tb.get_end_iter(),tb.get_end_iter())
        else:
            self.delete_event()
    
    def onKeyRelease(self, widget, event):
        keyPressName = gdk.keyval_name(event.keyval)
        
        if ((keyPressName == "Control_L") or (keyPressName == "Control_R")):
            self.keyCtrlPressed = False
    
    def onKeyPress(self, widget, event):
        keyPressName = gdk.keyval_name(event.keyval)
        
        if (self.keyCtrlPressed):
            if (keyPressName == "b"):
                self.on_BIU_button_clicked(None, self.tag_bold)
            if (keyPressName == "i"):
                self.on_BIU_button_clicked(None, self.tag_italic)
            if (keyPressName == "u"):
                self.on_BIU_button_clicked(None, self.tag_underline)
            if (keyPressName == "z"):
                self.textbuffer.undo()
            if ((keyPressName == "y") or (keyPressName == "Z")):
                self.textbuffer.redo()
        
        if ((keyPressName == "Control_L") or (keyPressName == "Control_R")):
            self.keyCtrlPressed = True
            
        if (keyPressName == "Escape"):
            self.onKeyEsc()
#         print (gtk.gdk.keyval_name(event.keyval))

    def getNoteSelected(self):
        # Returns the node of self.TreeView that is selected or None
        itersel = None
        treeView = self.treeview
        if (treeView != None):
            itersel = treeView.get_selection().get_selected()[1]
        return itersel

    def onNoteSelectionChange(self, treeView = None):
        itersel = self.getNoteSelected()
        if (itersel == None):
            itersel = self.NoteStore.get_iter_root()
        if (itersel != None):
            self.textbuffer = self.NoteStore.get_value(itersel, 4)
            self.textview.set_buffer(self.textbuffer)
            self.textview.set_sensitive(True)
        else:
            self.textview.set_sensitive(False)
            
    def onNewNote(self, button = None):
        # Create new node        
        piter = self.NoteStore.CreateNewNote(self.getNoteSelected())
        path = None
        if (piter != None):
            path = self.NoteStore.get_path(piter) 
        if (path != None):
            self.treeview.expand_to_path(path)
            self.treeview.set_cursor(path)

    def onTestClk(self, button):
#         TextBuffer2HTMLConvert.toHTML(self.textbuffer)
#         TextBuffer2HTMLConvert.serialize(self.textbuffer)
#         self.NoteStore.populate()
#             self.clipboard.request_text(self.rowChangedCallback)
            self.appoTxt = gtk.TextBuffer()
            self.clipboard.request_rich_text(self.appoTxt, self.callbackrich)
#         diag = gtk.MessageDialog()
#         diag.show()

    def callbackrich(self, clipboard, clformat, text, length, data = None):
        print ("Hey")
#         print (self, clipboard, clformat, text, length, data)

    def rowChangedCallback(self, clipboard, text, data = None):
        print (text)
        
    def cell_edited_callback(self, cellrenderertext, path, new_text):
        piter = self.NoteStore.get_iter(path)
        self.NoteStore.set_value(piter, 0, new_text)
        
    def onSave(self, menuItm):
        if (self.fileSelected == None):
            self.onSaveAs(None)
        else:
            self.NoteStore.save(self.fileSelected)
    
    def onSaveAs(self, menuItm):
        chooser = gtk.FileChooserDialog(title="Save notes file",action=gtk.FILE_CHOOSER_ACTION_SAVE,
                                  buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK))
        chooser.set_current_folder(os.getcwd())
        filefilter = gtk.FileFilter()
        filefilter.set_name("PGap note file")
        filefilter.add_pattern("*.xml")
        chooser.add_filter(filefilter)
        filefilter = gtk.FileFilter()
        filefilter.set_name("All files")
        filefilter.add_pattern("*")
        chooser.add_filter(filefilter)
        chooser.set_do_overwrite_confirmation(True)
        if (chooser.run() == gtk.RESPONSE_OK):
            fileSelected = chooser.get_filename()
            if (self.NoteStore.save(fileSelected) == True):
                self.fileSelected = fileSelected
                self.updateTitle(self.fileSelected)
            else:
                pass
        chooser.destroy()
            
    def onOpen(self, menuItm):
        chooser = gtk.FileChooserDialog(title="Open notes file",action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                  buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        chooser.set_current_folder(os.getcwd())
        filefilter = gtk.FileFilter()
        filefilter.set_name("PGap note file")
        filefilter.add_pattern("*.xml")
        chooser.add_filter(filefilter)
        filefilter = gtk.FileFilter()
        filefilter.set_name("All files")
        filefilter.add_pattern("*")
        chooser.add_filter(filefilter)
        if (chooser.run() == gtk.RESPONSE_OK):
            fileSelected = chooser.get_filename()
            if (self.NoteStore.load(fileSelected) == False):
                md = gtk.MessageDialog(self.window, 
                gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO, 
                gtk.BUTTONS_CLOSE, "File type not supported")
                md.run()
                md.destroy()
            else:
                self.fileSelected = fileSelected
                self.updateTitle(self.fileSelected)
        chooser.destroy()
        
if __name__ == '__main__':
    main = PGapMain()
    gtk.main()
