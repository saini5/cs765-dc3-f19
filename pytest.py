import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import pickle
from tree import getNodeList

file = open('tree-all.pickle', 'rb')
tree = pickle.load(file)

software_list = [("Firefox", 2002, "C++"),
                 ("Eclipse", 2004, "Java"),
                 ("Pitivi", 2004, "Python"),
                 ("Netbeans", 1996, "Java"),
                 ("Chrome", 2008, "C++"),
                 ("Filezilla", 2001, "C++"),
                 ("Bazaar", 2005, "Python"),
                 ("Git", 2005, "C"),
                 ("Linux Kernel", 1991, "C"),
                 ("GCC", 1987, "C"),
                 ("Frostwire", 2004, "Java")]


class TreeViewFilterWindow(Gtk.Window):

  def __init__(self):
    Gtk.Window.__init__(self, title="Treeview Filter Demo")
    self.set_border_width(10)

    self.paned = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)
    # Setting up the self.grid in which the elements are to be positionned
    self.grid = Gtk.Grid()
    self.grid.set_column_homogeneous(True)
    self.grid.set_row_homogeneous(True)
    # self.add(self.grid)
    self.add(self.paned)

    self.detail_grid = Gtk.Grid()
    self.detail_grid.set_column_homogeneous(True)
    self.detail_grid.set_row_homogeneous(True)
    self.paned.add2(self.detail_grid)

    # Creating the TreeStore model
    self.software_treestore = Gtk.TreeStore(str, int, int)

    allNodes = getNodeList(tree)
    parents = {}
    parents[None] = None
    for node in allNodes:
      parentName = None
      if node.parent is not None:
        parentName = node.parent.name
      attrs = [node.name, node.productCount, node.subtreeProductCount]
      parentObj = parents[parentName]
      # print(node.path)
      # print(node.name)
      # print(node.productCount)
      parents[node.name] = self.software_treestore.append(parentObj, attrs)

    self.current_filter_language = None

    # Creating the filter, feeding it with the treestore model
    self.language_filter = self.software_treestore.filter_new()
    # # setting the filter function, note that we're not using the
    self.language_filter.set_visible_func(self.language_filter_func)

    # creating the treeview, making it use the filter as a model,
    # and adding the columns
    self.treeview = Gtk.TreeView.new_with_model(self.software_treestore)
    self.treeview.columns_autosize()
    self.treeview.set_enable_search(True)
    self.treeview.set_enable_tree_lines(True)

    # Create the columns for the TreeView
    cats = ["Name", "Product Count", "Subtree Product Count"]
    for i, column_title in enumerate(cats):
      renderer = Gtk.CellRendererText()
      column = Gtk.TreeViewColumn(column_title, renderer, text=i)
      self.treeview.append_column(column)
      if i == 0:
        self.treeview.set_expander_column(column)

    # creating buttons to filter by programming language,
    # and setting up their events
    self.buttons = list()
    for prog_language in ["Java", "C", "C++", "Python", "None"]:
      button = Gtk.Button(prog_language)
    self.buttons.append(button)
    button.connect("clicked", self.on_selection_button_clicked)

    # setting up the layout, putting the treeview in a scrollwindow,
    # and the buttons in a row
    self.scrollable_treelist = Gtk.ScrolledWindow()
    self.scrollable_treelist.set_vexpand(True)
    self.scrollable_treelist.set_hexpand(False)

    self.paned.add1(self.scrollable_treelist)
    self.scrollable_treelist.add(self.treeview)

    self.detail_grid.attach(self.buttons[0],
                            0, 0, 20, 20)
    # for i, button in enumerate(self.buttons[1:]):
    #   self.grid.attach_next_to(button, self.buttons[i],
    #                            Gtk.PositionType.RIGHT, 1, 1)

    self.show_all()

  def language_filter_func(self, model, iter, data):
    """Tests if the language in the row is the one in the filter"""
    if (self.current_filter_language is None
        or self.current_filter_language == "None"):
      return True
    else:
      return model[iter][2] == self.current_filter_language

  def on_selection_button_clicked(self, widget):
    """Called on any of the button clicks"""
    # we set the current language filter to the button's label
    self.current_filter_language = widget.get_label()
    print("%s language selected!" % self.current_filter_language)
    # we update the filter, which updates in turn the view
    self.language_filter.refilter()


win = TreeViewFilterWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
