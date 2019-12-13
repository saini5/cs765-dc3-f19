import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import pickle
from tree import getNodeList, alsoAncestors, buildNodeDict
from gtkcss import set_gtk_style
import json

file = open('tree-all.pickle', 'rb')
tree = pickle.load(file)

class TreeViewFilterWindow(Gtk.Window):

  def __init__(self):
    Gtk.Window.__init__(self, title="Treeview Filter Demo")
    self.set_border_width(10)
    self.maximize()

    self.paned = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)
    self.paned.set_position(400) # for some reason, only shows till the first column, we have to manually resize to show 2nd and 3rd cols 
    # Setting up the self.grid in which the elements are to be positionned
    self.grid = Gtk.Grid()
    self.grid.set_column_homogeneous(True)
    self.grid.set_row_homogeneous(True)
    # self.add(self.grid)
    self.add(self.paned)

    self.detail_grid = Gtk.Grid()

    # Creating the TreeStore model
    self.treestore = Gtk.TreeStore(int, str, int, int, str)

    nodeDict = buildNodeDict(tree)
    allNodes = getNodeList(tree)
    parents = {}
    self.treestoreiterNamewithBracketVsParentNode = {}
    self.treestoreiterNamewithBracketVsNode = {}
    parents[None] = None
    self.treestoreiterNamewithBracketVsParentNode[None] = None
    self.treestoreiterNamewithBracketVsNode[None] = None

    for node in allNodes:
      numChildren = ""
      if len(node.children) > 0:
        numChildren = " (" + str(len(node.children)) + ")"
      namePlusBranch = node.name + numChildren
      alsoAncestor = alsoAncestors(nodeDict, node)
      oneVal = list(nodeDict.values())[1]
      ancestorString = json.dumps({'x': str(oneVal)})
      attrs = [node.id, namePlusBranch, node.productCount, node.subtreeProductCount, ancestorString]
      parentId = node.parent.id if node.parent is not None else None
      parentObj = parents[parentId]
      treestoreiter = self.treestore.append(parentObj, attrs)
      parents[node.id] = treestoreiter
      treestoreiterNamewithBracket = self.treestore.get_value(treestoreiter, 0)
      self.treestoreiterNamewithBracketVsParentNode[treestoreiterNamewithBracket] = node.parent
      # TODO:: both of these reverse mappings from name(bracket) seem to be erroneous to this corner case
      # case in treeview: root>Sportsand Outdoors>Accessories shows Tires and Wheels as parent of Accessories(17),
      # possibly two got added against <Accessories(17), > and latest one was Tires and Wheels
      self.treestoreiterNamewithBracketVsNode[treestoreiterNamewithBracket] = node

    self.current_filter_language = None

    # Creating the filter, feeding it with the treestore model
    self.language_filter = self.treestore.filter_new()
    # # setting the filter function, note that we're not using the
    self.language_filter.set_visible_func(self.language_filter_func)
    self.treestore.set_sort_func(0, self.compare, None)

    # creating the treeview, making it use the filter as a model,
    # and adding the columns
    self.treeview = Gtk.TreeView.new_with_model(self.treestore)
    self.treeview.columns_autosize()
    self.treeview.set_enable_search(True)
    self.treeview.set_enable_tree_lines(True)
    self.treeview.set_show_expanders(True)
    self.treeview.connect("row_activated", self.on_node_clicked)

    # Create the columns for the TreeView
    cats = ["id", "Name (# subcategories)", "Product Count", "Subtree Product Count", "Alsos"]
    for i, column_title in enumerate(cats):
      renderer = Gtk.CellRendererText()
      column = Gtk.TreeViewColumn(column_title, renderer, text=i)
      column.set_sort_column_id(i)
      self.treeview.append_column(column)
      if i == 0:
        self.treeview.set_expander_column(column)

    # setting up the layout, putting the treeview in a scrollwindow,
    # and the buttons in a row
    self.scrollable_treelist = Gtk.ScrolledWindow()
    self.scrollable_treelist.set_vexpand(True)
    self.scrollable_treelist.set_hexpand(True)

    self.paned.add1(self.scrollable_treelist)
    self.scrollable_treelist.add(self.treeview)

    # TODO: Add the data rows & track the right-labels for editing
    # on selection
    detail_view_header = Gtk.Label.new()
    detail_view_header.set_markup("<big><b>Detailed View</b></big>")
    # self.detail_grid.add(detail_view_header)
    # self.row1 = self.build_row("hello", "my baby")
    self.detail_grid.attach (detail_view_header, 0, 0, 1, 1)

    label_annotation = Gtk.Label("Annotation")
    self.detail_grid.attach(label_annotation, 0, 1, 1, 1)

    value_annotation = Gtk.Label("Value")
    self.detail_grid.attach(value_annotation, 1, 1, 1, 1)

    # self.row2 = self.build_row("yo", "baby")

    self.paned.add2(self.detail_grid)

    # self.treeview.expand_all() # Uncomment to expand the tree initially
    self.show_all()

  def on_node_clicked(self, tree_view, path, column):
    """Called on any of the node clicks"""
    # we set the current language filter to the button's label
    # print("HELLO THERE")
    # print(path)
    # print("===")
    # print(column.get_title())
    # # self.current_filter_language = widget.get_label()
    # print("%s language selected!" % self.current_filter_language)
    # select = tree_view.get_selection()
    # selected_rows = select.get_selected_rows()
    # pathh = selected_rows[1]
    # roww = pathh[0]
    # index = roww.get_indices()
    # print(index)

    print(tree_view.get_model())
    tree_model = tree_view.get_model()
    tree_iter = tree_model.get_iter_from_string(path.to_string())
    # print(tree_iter)
    treeIterNameWithBracket = tree_model.get_value(tree_iter, 0)
    print(treeIterNameWithBracket)
    presentNodeParent = self.treestoreiterNamewithBracketVsParentNode[treeIterNameWithBracket]
    print(presentNodeParent)
    presentNode = self.treestoreiterNamewithBracketVsNode[treeIterNameWithBracket]
    print(presentNode)
    # node fetched
    # let's populate detailed view based on this node - getter methods for this node is in tree.py
    # TODO: start here


    # we update the filter, which updates in turn the view
    self.language_filter.refilter()
  
  def language_filter_func(self, model, iter, data):
    """Tests if the language in the row is the one in the filter"""
    if (self.current_filter_language is None
        or self.current_filter_language == "None"):
      return True
    else:
      return model[iter][2] == self.current_filter_language

  def on_selection_button_clicked(self, tree_view, path, column):
    """Called on any of the button clicks"""
    # we set the current language filter to the button's label
    print("HELLO THERE")
    # self.current_filter_language = widget.get_label()
    print("%s language selected!" % self.current_filter_language)
    # we update the filter, which updates in turn the view
    self.language_filter.refilter()

  def compare(self, model, row1, row2, user_data):
    sort_column, _ = model.get_sort_column_id()
    value1 = model.get_value(row1, sort_column)
    value2 = model.get_value(row2, sort_column)
    if isinstance(value1, int):
      value1 = -1 * int(value1)
      value2 = -1 * int(value2)

    if value1 < value2:
        return -1
    elif value1 == value2:
        return 0
    else:
        return 1

  def build_row(self, left_text, right_text):
    row = Gtk.Box(spacing=10)
    row.set_homogeneous(False)

    left = Gtk.Label.new(left_text)
    right = Gtk.Label.new(right_text)
    row.pack_start(left, True, True, 0)
    row.pack_start(right, True, True, 0)

    return row


set_gtk_style("treeview.css")  # Load the css file
win = TreeViewFilterWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
