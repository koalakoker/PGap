'''
Created on 30/mag/2015

@author: koala
'''

import sys
try:
    import gtk
except:
    sys.exit(1)

class PGapMain:
    newPage = 2 #default value 1 is the welcome screen
    textMargins = 5
    
    def __init__(self):
        
        #Set the Glade file
        self.gladefile = "pgapgui.glade"  
        self.builder = gtk.Builder()
        self.builder.add_from_file(self.gladefile)
        window = self.builder.get_object("pgapui")
        self.notebook = self.builder.get_object("notebook")
        window.show_all()
        
        handlers = { "onDeleteWindow": gtk.main_quit,
                     "onNewButton": self.onTestButtonPressed,
                     "onDeleteButton": self.onDeleteButtonPressed
                   }
        self.builder.connect_signals(handlers)
        
    def onTestButtonPressed(self,button):
        notebook = self.notebook
        
        #Create new page
        text = gtk.TextView()
        txBuffer = text.get_buffer()
        txBuffer.set_text("new page" + str(self.newPage))
        text.show()
        text.set_wrap_mode(gtk.WRAP_WORD)
        text.set_left_margin(self.textMargins)
        text.set_right_margin(self.textMargins)
        scroll = gtk.ScrolledWindow()
        scroll.add(text)
        scroll.show()
        scroll.set_policy(gtk.POLICY_NEVER,gtk.POLICY_AUTOMATIC)
        view = gtk.Viewport()
        view.add(scroll)
        view.show()
            
        label = gtk.Label("Page " + str(self.newPage))
        self.newPage += 1
        
        newPageIndex = notebook.append_page(view, label)
        notebook.set_current_page(newPageIndex)
        
    def onDeleteButtonPressed(self,button):
        notebook = self.notebook
        notebook.remove_page(notebook.get_current_page())

if __name__ == '__main__':
    main = PGapMain()
    gtk.main()