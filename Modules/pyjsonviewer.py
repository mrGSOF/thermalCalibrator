"""

A JSON viewer using pure python

author: Atsushi Sakai (@Atsushi_twi)

"""

import argparse
import json
import os
import uuid
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, Tk
#from tkinter import font
#from tkinter import messagebox

# === Config ===
MAX_N_SHOW_ITEM = 300
MAX_HISTORY = 10
FILETYPES = [("JSON files", "*.json"), ("All Files", "*.*")]
HISTORY_FILE_PATH = os.path.join(os.path.expanduser('~'),
                                 ".pyjsonviewer_history")
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

class JSONTreeFrame(ttk.Frame):

    def __init__(self, master, json_path=None, json_data=None, initial_dir="~/"):
        super().__init__(master, padding="3")
        self.master = master
        self.grid(row=0, column=0, sticky=tk.NSEW)
        self.tree = ttk.Treeview(self, columns="Values")
        self.tree.column("Values", width=100, anchor="center")
        self.tree.heading("Values", text="Values")
        self.create_widgets()
        self.initial_dir = initial_dir

        if json_path:
            self.set_table_data_from_json_path(json_path)  #< Generate tree from JSON file
        elif json_data:
            self.set_table_data_from_json(json_data)       #< Generate tree from dictionary

    def create_widgets(self) -> None:
        self.tree.bind('<Double-1>', self.click_item)

        ysb = ttk.Scrollbar(
            self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=ysb.set)

        self.tree.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W))
        ysb.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def click_item(self, event=None) -> None:
        """
        Callback function when an item is clicked

        :param event: event arg (not used)
        """
        item_id = self.tree.selection()
        item_text = self.tree.item(item_id, 'text') #< Get the 'text' fielf the selected item
        print( item_id, item_text)

    def select_json_file(self, event=None) -> None:
        """
        :param event: event arg (not used)
        """
        file_path = filedialog.askopenfilename(
            initialdir=self.initial_dir,
            filetypes=FILETYPES)
        self.set_table_data_from_json_path(file_path)

    def expand_all(self, event=None) -> None:
        """
        :param event: event arg (not used)
        """
        for item in self.get_all_children(self.tree):
            self.tree.item(item, open=True)

    def collapse_all(self, event=None) -> None:
        """
        :param event: event arg (not used)
        """
        for item in self.get_all_children(self.tree):
            self.tree.item(item, open=False)

    def get_all_children(self, tree, item="") -> tuple:
        children = tree.get_children(item)
        for child in children:
            children += self.get_all_children(tree, child) #< Recursive
        return children

    def set_table_data_from_json_path(self, file_path) -> None:
        """ Read JSON file and call set_table_data_from_json() method """
        data = self.load_json_data(file_path)
        self.set_table_data_from_json(data=data, rootName=file_path )

    def set_table_data_from_json(self, data, rootName="ROOT") -> None:
        """ Clear previous tree structure and generate new one by calling insert_nodes(json_data) method """
        assert type(data) in (list, dict)
        self.delete_all_nodes()
        root = "root" #< Root
        self.tree.insert("", '0', root, text=rootName)
        self.tree.item(root, open=True)
        self.insert_nodes(data=data, root=root)
        #self.json_tree(root, data)
        
    def delete_all_nodes(self) -> None:
        """ Clear previous tree structure """
        for i in self.tree.get_children():
            self.tree.delete(i)

    def json_tree(self, parent, dictionary):
        """  Minimal function to generate tree (replace insert_nodes()) """
        tree = self.tree
        for key in dictionary:
            uid = uuid.uuid4()
            if isinstance(dictionary[key], dict):
                tree.insert(parent, 'end', uid, text=key)               #< 
                self.json_tree(uid, dictionary[key])
            elif isinstance(dictionary[key], (tuple, list)):
                tree.insert(parent, 'end', uid, text=key + '[]')        #<
                self.json_tree(uid, dict([(i, x) for i, x in enumerate(dictionary[key])]))
            else:
                value = dictionary[key]
                if value is None:
                    value = 'None'
                tree.insert(parent, 'end', uid, text=key, value=value)  #< 

    def insert_nodes(self, data, root="") -> None:
        """ Main funcrion to generate the tree structure from data """
        if isinstance(data, (list,tuple)):
            for index, value in enumerate(data):        #< Add every element in the list
                self.insert_node(root, index, value)    #< Use the INDEX# as field lable
        elif isinstance(data, dict):
            for (key, value) in data.items():           #< Add every element in the dictionary
                self.insert_node(root, key, value)      #< Use the KEY name as field lable

    def insert_node(self, parent, key, value) -> None:
        """ Recursive function """
        node = self.tree.insert(parent, 'end', text=key, open=False)

        if value:
            if isinstance(value, (list, tuple)):
                for index, item in enumerate(value[:MAX_N_SHOW_ITEM]):
                    self.insert_node(node, index, item)                  #< Recursive function add a list
            elif isinstance(value, dict):
                for key, item in value.items():
                    self.insert_node(node, key, item)                    #< Recursive function add a dictionary
            else:
                self.tree.insert(node, 'end', text=value, open=False)    #< Add the value to the tree (GUI)


    @staticmethod
    def load_json_data(file_path):
        with open(file_path, encoding='utf-8') as f:
            return json.load(f)

def view_data(json_file=None, json_data=None, initial_dir=None) -> None:
    root: Tk = tk.Tk()
    root.title('PyJSONViewer')
    root.geometry("500x500")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    menubar = tk.Menu(root)

    if json_file:
        app = JSONTreeFrame(root, json_path=json_file, initial_dir=initial_dir)
    elif json_data:
        app = JSONTreeFrame(root, json_data=json_data)
    else:
        app = JSONTreeFrame(root)

    file_menu = tk.Menu(menubar, tearoff=0)
    file_menu.add_command(label="Open", accelerator='Ctrl+O',
                          command=app.select_json_file)
    menubar.add_cascade(label="File", menu=file_menu)

    tool_menu = tk.Menu(menubar, tearoff=0)
    tool_menu.add_command(label="Expand all",
                          accelerator='Ctrl+E', command=app.expand_all)
    tool_menu.add_command(label="Collapse all",
                          accelerator='Ctrl+L', command=app.collapse_all)
    menubar.add_cascade(label="Tools", menu=tool_menu)

    root.config(menu=menubar)
    root.bind_all("<Control-o>", lambda e: app.select_json_file(event=e))
    root.bind_all("<Control-e>", lambda e: app.expand_all(event=e))
    root.bind_all("<Control-l>", lambda e: app.collapse_all(event=e))

    #root.mainloop()
    return app


def main():
    print(__file__ + " start!!")

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', type=str, help='JSON file path')
    parser.add_argument('-d', '--dir', type=str,
                        help='JSON file directory')
    parser.add_argument('-o', '--open', action='store_true',
                        default=False, help='Open with finder')
    args = parser.parse_args()

    if args.open:
        args.file = filedialog.askopenfilename(
            initialdir=args.dir,
            filetypes=FILETYPES)
    return view_data(json_file=args.file, initial_dir=args.dir)


if __name__ == '__main__':
    app = main()
