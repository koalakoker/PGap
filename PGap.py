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
    
    def __init__(self):
        
        #Set the Glade file
        self.gladefile = "pgapgui.glade"  
        self.builder = gtk.Builder()
        self.builder.add_from_file(self.gladefile)
        window = self.builder.get_object("pgapui")
        window.show_all()
        
        handlers = { "onDeleteWindow": gtk.main_quit, "onTestButton": self.onTestButtonPressed }
        self.builder.connect_signals(handlers)
        
    def onTestButtonPressed(self,button):
        notebook = self.builder.get_object("notebook")
#         print (type(notebook))
        checkbutton = gtk.CheckButton("Check me please!")
        checkbutton.set_size_request(100, 75)
        checkbutton.show ()    
        label = gtk.Label("Add page")
        notebook.insert_page(checkbutton, label, 2)

if __name__ == '__main__':
    main = PGapMain()
    gtk.main()