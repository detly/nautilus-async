import gtk
import pygtk

def debug_shell(namespace):
    """
    
    Open up an IPython shell which shares the context of the extension.
    
    See: http://ipython.scipy.org/moin/Cookbook/EmbeddingInGTK
    
    """
    import gtk
    from rabbitvcs.debug.ipython_view import IPythonView
    
    window = gtk.Window()
    window.set_size_request(750,550)
    window.set_resizable(True)
    window.set_position(gtk.WIN_POS_CENTER)
    scrolled_window = gtk.ScrolledWindow()
    scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    ipython_view = IPythonView()
    ipython_view.updateNamespace(namespace)
    ipython_view.set_wrap_mode(gtk.WRAP_CHAR)
    ipython_view.show()
    scrolled_window.add(ipython_view)
    scrolled_window.show()
    window.add(scrolled_window)
    window.show()
