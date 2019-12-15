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
    self.paned.set_position(400)  # for some reason, only shows till
    # the first column, we have to manually resize to show 2nd and 3rd cols
    # Setting up the self.grid in which the elements are to be positionned
    self.add(self.paned)

    self.detail_grid = Gtk.Grid()
    self.detail_grid.set_row_spacing(0)
    self.detail_grid.set_column_spacing(0)
    self.detail_grid.set_border_width(10)

    # Creating the TreeStore model
    self.treestore = Gtk.TreeStore(int, str, int, int, str)

    self.nodeDict = buildNodeDict(tree)
    allNodes = getNodeList(tree)
    parents = {}
    parents[None] = None

    for node in allNodes:
      numChildren = ""
      if len(node.children) > 0:
        numChildren = " (" + str(len(node.children)) + ")"
      namePlusBranch = node.name + numChildren
      alsoAncestor = alsoAncestors(self.nodeDict, node)
      alsoList = list(alsoAncestor.values())
      oneVal = alsoList[0] if len(alsoList) > 0 else "NONE"
      ancestorString = json.dumps({'x': str(oneVal)})
      attrs = [node.id, namePlusBranch, node.productCount,
               node.subtreeProductCount, ancestorString]
      parentId = node.parent.id if node.parent is not None else None
      parentObj = parents[parentId]
      treestoreiter = self.treestore.append(parentObj, attrs)
      parents[node.id] = treestoreiter

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
    cats = ["Name (# subcategories)", "Product Count",
            "Subtree Product Count", "Alsos"]
    for i, column_title in enumerate(cats):
      renderer = Gtk.CellRendererText()
      column = Gtk.TreeViewColumn(column_title, renderer, text=i + 1)
      column.set_sort_column_id(i + 1)
      self.treeview.append_column(column)
      if i == 0:
        self.treeview.set_expander_column(column)
        self.treeview.set_search_column(i)

    # setting up the layout, putting the treeview in a scrollwindow,
    # and the buttons in a row
    self.scrollable_treelist = Gtk.ScrolledWindow()
    self.scrollable_treelist.set_vexpand(True)
    self.scrollable_treelist.set_hexpand(True)

    self.paned.add1(self.scrollable_treelist)
    self.scrollable_treelist.add(self.treeview)

    # TODO: Add the data rows & track the right-labels for editing
    # on selection
    empty_placeholder = Gtk.Label.new("")
    self.detail_grid.attach(empty_placeholder, 0, 0, 1, 1)
    detail_view_header = Gtk.Label.new()
    detail_view_header.set_markup("<big><b>Detailed View</b></big>")
    detail_view_header.set_justify(Gtk.Justification.LEFT)
    detail_view_header = self.frame_wrap(detail_view_header)
    # self.detail_grid.add(detail_view_header)
    self.detail_grid.attach(detail_view_header, 1, 1, 2, 1)

    label_annotation = self.frame("Annotation")
    self.detail_grid.attach(label_annotation, 1, 2, 1, 1)

    value_annotation = self.frame("Value")
    self.detail_grid.attach(value_annotation, 2, 2, 1, 1)

    # initializing the rows
    name_annotation = Gtk.Label.new("Name")
    name_annotation.set_justify(Gtk.Justification.LEFT)
    name_annotation = self.frame_wrap(name_annotation)
    self.detail_grid.attach(name_annotation, 1, 3, 1, 1)
    self.name_value = self.frame("")
    self.detail_grid.attach(self.name_value, 2, 3, 1, 1)

    path_annotation = Gtk.Label.new("Path")
    path_annotation.set_justify(Gtk.Justification.LEFT)
    path_annotation = self.frame_wrap(path_annotation)
    self.detail_grid.attach_next_to(path_annotation, name_annotation,
                                    Gtk.PositionType.BOTTOM, 1, 1)
    self.path_value = self.frame("")
    self.detail_grid.attach(self.path_value, 2, 4, 1, 1)
    self.detail_grid.attach_next_to(self.path_value, path_annotation,
                                    Gtk.PositionType.RIGHT, 1, 1)

    product_count_annotation = Gtk.Label.new("Product Count")
    product_count_annotation.set_justify(Gtk.Justification.LEFT)
    product_count_annotation = self.frame_wrap(product_count_annotation)
    self.detail_grid.attach_next_to(product_count_annotation,
                                    path_annotation,
                                    Gtk.PositionType.BOTTOM, 1, 1)
    self.product_count_value = self.frame("")
    self.detail_grid.attach_next_to(self.product_count_value,
                                    product_count_annotation,
                                    Gtk.PositionType.RIGHT, 1, 1)

    subtree_product_count_annotation = Gtk.Label.new("Subtree Product Count")
    subtree_product_count_annotation.set_justify(Gtk.Justification.LEFT)
    subtree_product_count_annotation = self.frame_wrap(
        subtree_product_count_annotation)
    self.detail_grid.attach_next_to(subtree_product_count_annotation,
                                    product_count_annotation,
                                    Gtk.PositionType.BOTTOM, 1, 1)
    self.subtree_product_count_value = self.frame("")
    self.detail_grid.attach_next_to(self.subtree_product_count_value,
                                    subtree_product_count_annotation,
                                    Gtk.PositionType.RIGHT, 1, 1)

    self.paned.add2(self.detail_grid)

    # self.treeview.expand_all() # Uncomment to expand the tree initially
    self.show_all()

  def frame(self, text):
    return self.frame_wrap(Gtk.Label.new(text))

  def frame_wrap(self, elem):
    frame = Gtk.Frame.new()
    frame.add(elem)
    return frame

  def on_node_clicked(self, tree_view, path, column):
    """Called on any of the node clicks"""

    print(tree_view.get_model())
    tree_model = tree_view.get_model()
    tree_iter = tree_model.get_iter_from_string(path.to_string())
    id = tree_model.get_value(tree_iter, 0)  # Hidden column 0

    presentNode = self.nodeDict[id]
    # node fetched
    # let's populate detailed view based on this node -
    # getter methods for this node is in tree.py
    self.name_value.get_child().set_text(presentNode.name)
    self.path_value.get_child().set_text(str(presentNode.path))

    self.product_count_value.get_child().set_text(
        str(presentNode.productCount))
    self.subtree_product_count_value.get_child().set_text(
        str(presentNode.subtreeProductCount))
    # self.show_all()

    # we update the filter, which updates in turn the view
    self.language_filter.refilter()

  def language_filter_func(self, model, iter, data):
    """Tests if the language in the row is the one in the filter"""
    if (self.current_filter_language is None
        or self.current_filter_language == "None"):
      return True
    else:
      return model[iter][2] == self.current_filter_language

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


set_gtk_style("treeview.css")  # Load the css file
win = TreeViewFilterWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
