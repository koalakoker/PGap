'''
Created on 30/mag/2015

@author: koala
'''

import pygtk
pygtk.require('2.0')
import gtk
from gtk import gdk
import pango
from NoteModel import NoteModel
import noteBrowserWidget
import os

PROGRAM_NAME = "PGap"

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
        if (self.NoteStore.modified):
            message = gtk.MessageDialog(type=gtk.MESSAGE_WARNING, buttons=gtk.BUTTONS_NONE)
            message.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
            message.add_button(gtk.STOCK_NO, gtk.RESPONSE_NO)
            message.add_button(gtk.STOCK_YES, gtk.RESPONSE_YES)
            message.set_default_response(gtk.RESPONSE_YES)
            message.set_title("Save Notes")
            message.set_markup("Notes have been modified. Save changes?")
            res = message.run()
            message.destroy()
            if (res == gtk.RESPONSE_YES):
                self.onSave(None)
            elif ((res == gtk.RESPONSE_CANCEL) or (res == gtk.RESPONSE_DELETE_EVENT)):
                return    
        gtk.main_quit()
        return False
        
    def __init__(self):
        self.gladefile = "pgapgui.glade"  
        self.builder = gtk.Builder()
        self.builder.add_from_file(self.gladefile)
        self.window = self.builder.get_object("pgapui")
        self.window.resize(1024,600)
        self.window.show_all()
        self.window.connect("delete_event", self.delete_event)
                    
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
        self.tag_link = gtk.TextTag("Link")
        self.tag_link.set_property("underline", pango.UNDERLINE_SINGLE)
        self.tag_link.set_property("style", pango.STYLE_ITALIC)
        color = gdk.Color(0,0,65535) #Link color
        self.tag_link.set_property("foreground-gdk", color)
        self.tag_link.connect("event", self.tagLinkEvent)
        self.tagTable.add(self.tag_link)
        self.tag_hidden = gtk.TextTag("Hidden")
        self.tag_hidden.set_property("underline", pango.UNDERLINE_SINGLE)
        self.tag_hidden.set_property("style", pango.STYLE_ITALIC)
        color = gdk.Color(65535,0,0) #Link color
        self.tag_hidden.set_property("foreground-gdk", color)
        self.tag_hidden.set_property("invisible", True)
        self.tagTable.add(self.tag_hidden)
        
        # create a TreeStore with one string showColumn to use as the model
        self.NoteStore = NoteModel(self.tagTable)
        self.NoteStore.connect('modified_title', self.onTitleChanged)
        self.NoteStore.connect('modified_text', self.onTextChanged)
        #Populate
#         self.NoteStore.populate()

        # create the TreeView using NoteStore
        self.treeview =  self.builder.get_object("treeview")
        self.treeview.set_model(self.NoteStore)
        self.treeviewSelection = self.treeview.get_selection()
        
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
        self.noteSelect(0)
                
        self.keyCtrlPressed = False
        
        self.fileSelected = None
        self.updateTitle()
        
        # Clipboard
        self.clipboard = gtk.Clipboard()
        
        # Note Browser Widget
        self.noteBrowser = noteBrowserWidget.noteBrowserWidget(self.gladefile, self.NoteStore)
        
        handlers = { "onDeleteWindow": gtk.main_quit,
                     "onNewButton": self.onTestClk,
                     "onDeleteButton": self.onTestClk,
                    "onTestClk": self.onTestClk,
                     "on_ID_toggled": self.updateColumnView,
                     "on_Last modify_toggled": self.updateColumnView,
                     "on_Creation Time_toggled": self.updateColumnView,
                     "keypress": self.onKeyPress,
                     "keyrelease": self.onKeyRelease,
                     "mousemove": self.onMouseMove,
                     "onCursorChanged": self.onNoteSelectionChange,
                     "onNewNote": self.onNewNote,
                     "on_BIU_button_clicked": self.on_BIU_button_clicked,
                     "onSave" : self.onSave,
                     "onSaveAs" : self.onSaveAs,
                     "onOpen" : self.onOpen,
                     "onQuit" : self.delete_event
                   }
        
        self.builder.connect_signals(handlers)
        
    def onTitleChanged(self, NoteModel):
        self.updateTitle()
        
    def onTextChanged(self, NoteModel):
        piter = self.getNoteSelected()
        path = NoteModel.get_path(piter)
        self.NoteStore.emit("row-changed", path, piter)
        
    def updateTitle(self):
        fileSelected = self.fileSelected
        modIndincator = ""
        if (self.NoteStore.modified):
            modIndincator = "*"
        newTitle = PROGRAM_NAME
        if (fileSelected != None):
            newTitle += " - " + fileSelected + modIndincator
        else:
            newTitle += " - new notebook" + modIndincator
        self.window.set_title(newTitle)
                                        
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
                
                #Verify if tag is link (in this case the user have to select the link Eg. Note ID)
                if (tag == self.tag_link):
                    if (self.textbuffer.isTagSelected(start, self.tag_link)):
                        self.textbuffer.removeLink(self.tag_link, self.tag_hidden, start)
                    else:
                        noteID = self.noteBrowser.run()
                        if (noteID != 0):
                            self.textbuffer.addLink(self.tag_link, self.tag_hidden, start, end, "#" + str(noteID))
                else:
                    self.textbuffer.toggleTag(tag, start, end)
                
                
        except AttributeError:
            pass
    
    def onKeyEsc(self):
        try:
            bounds = self.textbuffer.get_selection_bounds()
            if len(bounds) != 0:
                tb = self.textbuffer
                tb.select_range(tb.get_end_iter(),tb.get_end_iter())
                return
        except:
            pass
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
            if (keyPressName == "l"):
                self.on_BIU_button_clicked(None, self.tag_link)
            if (keyPressName == "z"):
                self.textbuffer.undo()
            if ((keyPressName == "y") or (keyPressName == "Z")):
                self.textbuffer.redo()
            if (keyPressName == "s"):
                self.onSave()
        
        if ((keyPressName == "Control_L") or (keyPressName == "Control_R")):
            self.keyCtrlPressed = True
            
        if (keyPressName == "Escape"):
            self.onKeyEsc()
#         print (gtk.gdk.keyval_name(event.keyval))
                
    def onMouseMove(self, widget, event):
        start = widget.get_iter_at_location(int(event.x), int(event.y))
        if (self.textbuffer.isTagSelected(start, self.tag_link)):
            cur = gtk.gdk.Cursor(gtk.gdk.HAND1)
            event.window.set_cursor(cur)
            widget.set_tooltip_text("ctrl + mouse left click to open the link")
            self.textview.grab_focus()
        else:
            event.window.set_cursor(None)
            widget.set_tooltip_text(None)
            
    def tagLinkEvent(self, tag, widget, event, piter):
        if (event.type == gtk.gdk.BUTTON_PRESS):
            if (event.button == 1):
                start = widget.get_iter_at_location(int(event.x), int(event.y))
                tb = self.textbuffer
                if (tb.isTagSelected(start, self.tag_link)):
                    if (self.keyCtrlPressed):
                        link = tb.getLink(self.tag_link, self.tag_hidden, start)
                        if (tb.isInternalLink(link)):
                            noteID = tb.getNoteIDFromLink(link)
                            noteIDPath = self.NoteStore.findNoteID(noteID) 
                            self.noteSelect(noteIDPath)
        
    def getNoteSelected(self):
        # Returns the node of self.TreeView that is selected or None
        itersel = None
        treeView = self.treeview
        if (treeView != None):
            itersel = treeView.get_selection().get_selected()[1]
        return itersel

    def onNoteSelectionChange(self, treeView):
        itersel = self.getNoteSelected()
        if (itersel == None):
            itersel = self.NoteStore.get_iter_root()
        if (itersel != None):
            self.textbuffer = self.NoteStore.get_value(itersel, 4)
            self.textview.set_buffer(self.textbuffer)
            self.textview.set_sensitive(True)
            self.textview.grab_focus()
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
##             self.appoTxt = gtk.TextBuffer()
##             self.clipboard.request_rich_text(self.appoTxt, self.callbackrich)
#         diag = gtk.MessageDialog()
#         diag.run()
        
#         menu = gtk.Menu()
#         menu_item = gtk.MenuItem("A menu item")
#         menu.append(menu_item)
#         menu_item.run()
#         menu.popup(None, None, None, 0, 0)
        pass

    def callbackrich(self, clipboard, clformat, text, length, data = None):
        print ("Hey")
#         print (self, clipboard, clformat, text, length, data)

    def rowChangedCallback(self, clipboard, text, data = None):
        print (text)
        
    def cell_edited_callback(self, cellrenderertext, path, new_text):
        piter = self.NoteStore.get_iter(path)
        self.NoteStore.set_value(piter, 0, new_text)
    
    def getNoteValue(self, col):
        #Get the value from the selected note in the Tree View
        piter = self.treeview.get_selection().get_selected()[1]
        return self.NoteStore.get_value(piter,col)    
    
    def setNoteValue(self, col, value):
        #Set the vaule to the selected note in the Tree View
        piter = self.treeview.get_selection().get_selected()[1]
        self.NoteStore.set_value(piter, col, value)
        
    def getNoteIter(self):
        #Get the selected noter iter for the Note Model
        return self.treeview.get_selection().get_selected()[1]
    
    def noteSelect(self, path):
        self.treeviewSelection.select_path(path)
        self.treeview.emit("cursor-changed")
        
    def onSave(self, menuItm = None):
        if (self.fileSelected == None):
            self.onSaveAs(None)
        else:
            if (self.NoteStore.save(self.fileSelected) == True):
                pass
    
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
                self.updateTitle()
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
                self.updateTitle()
                self.noteSelect(0)
                
        chooser.destroy()
        
if __name__ == '__main__':
    main = PGapMain()
    gtk.main()
