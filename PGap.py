'''
Created on 30/mag/2015

@author: koala
'''

import sys
try:
    import gtk
    import gtk.glade
except:
    sys.exit(1)

class PGapMain:
    newPage = 2
    
    def __init__(self):
        
        #Set the Glade file
        self.gladefile = "pgapgui.glade"  
        self.builder = gtk.Builder()
        self.builder.add_from_file(self.gladefile)
        window = self.builder.get_object("pgapui")
        self.notebook = self.builder.get_object("notebook")
        window.show_all()
        
        handlers = { "onDeleteWindow": gtk.main_quit,
                     "onTestButton": self.onTestButtonPressed,
                     "onDeleteButton": self.onDeleteButtonPressed
                   }
        self.builder.connect_signals(handlers)
        
    def onTestButtonPressed(self,button):
        
        #Create new page
        text = gtk.TextView()
        buffer = text.get_buffer()
        buffer.set_text("new page" + str(self.newPage))
        text.show()
        scroll = gtk.ScrolledWindow()
        scroll.add(text)
        scroll.show()
        view = gtk.Viewport()
        view.add(scroll)
        view.show()
            
        label = gtk.Label("Page " + str(self.newPage))
        self.newPage += 1
        
        self.notebook.append_page(view, label)
        
    def onDeleteButtonPressed(self,button):
        notebook = self.notebook
        notebook.remove_page(notebook.get_current_page())

if __name__ == '__main__':
    main = PGapMain()
    gtk.main()