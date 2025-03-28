from functools import partial
from collections import deque
from tkinter import ttk
import tkinter as tk
import os as os
import logging


# class TtkCheckList is sourced from https://stackoverflow.com/a/67348336, and slightly adopted to suit my own needs.
class TtkCheckList(ttk.Treeview):

    def __init__(
        self,
        master=None,
        width=200,
        clicked=None,
        separator=".",
        unchecked="\u2610",
        checked="\u2612",
        **kwargs,
    ):
        """
        :param width: the width of the check list
        :param clicked: the optional function if a checkbox is clicked. Takes a
                        `iid` parameter.
        :param separator: the item separator (default is `'.'`)
        :param unchecked: the character for an unchecked box (default is
                          "\u2610")
        :param unchecked: the character for a checked box (default is "\u2612")

        Other parameters are passed to the `TreeView`.
        """
        if "selectmode" not in kwargs:
            kwargs["selectmode"] = "none"
        if "show" not in kwargs:
            kwargs["show"] = "tree"
        ttk.Treeview.__init__(self, master, **kwargs)
        self._separator = separator
        self._unchecked = unchecked
        self._checked = checked
        self._clicked = self.selection_toggle if clicked is None else clicked

        self.column("#0", width=width, stretch=tk.YES)
        self.bind("<Button-1>", self._item_click, True)

    def _item_click(self, event):
        assert event.widget == self
        x, y = event.x, event.y
        element = self.identify("element", x, y)
        if element == "text":
            iid = self.identify_row(y)
            self._clicked(iid)

    def add_item(self, item):
        """
        Add an item to the checklist. The item is the list of nodes separated
        by dots: `Item.SubItem.SubSubItem`. **This item is used as `iid`  at
        the underlying `Treeview` level.**
        """
        try:
            parent_iid, text = item.rsplit(self._separator, maxsplit=1)
        except ValueError:
            parent_iid, text = "", item
        logging.debug(f"parent:{parent_iid}")
        self.insert(
            parent_iid,
            index="end",
            iid=item,
            text=text + " " + self._unchecked,
            open=True,
        )

    def toggle(self, iid):
        """
        Toggle the checkbox `iid`
        """
        text = self.item(iid, "text")
        checked = text[-1] == self._checked
        status = self._unchecked if checked else self._checked
        self.item(iid, text=text[:-1] + status)

    def checked(self, iid):
        """
        Return True if checkbox `iid` is checked
        """
        text = self.item(iid, "text")
        return text[-1] == self._checked

    def check(self, iid):
        """
        Check the checkbox `iid`
        """
        text = self.item(iid, "text")
        if text[-1] == self._unchecked:
            self.item(iid, text=text[:-1] + self._checked)

    def uncheck(self, iid):
        """
        Uncheck the checkbox `iid`
        """
        text = self.item(iid, "text")
        if text[-1] == self._checked:
            self.item(iid, text=text[:-1] + self._unchecked)


class ObsidianHTML_Limiter:
    def __init__(
        self, manuscript_path, auto_submit=False, level=-1, cli_args=None, loglevel=None
    ):
        self.logger = logging.getLogger(
            self.__class__.__module__ + "." + self.__class__.__qualname__
        )
        self.logger.setLevel(level=loglevel)
        self.width = 750
        self.height = 550
        if os.path.exists(manuscript_path):
            self.manuscript_path = manuscript_path
            self.auto_submit = auto_submit
            self.default_level = level
            self.cli_args = cli_args if cli_args else {}
            self.directory_structure = self.find_obsidian_vault_root()
            self.removed_selected_limiter_directory_success = False
            self.adjust_default_Level()
            if auto_submit:
                self.auto_select_directory()
                return  # we submit, so we can just use the level passed through.
            self.root = tk.Tk()
            self.root.focus_force()
            self.root.wm_attributes("-topmost", 1)
            self.setup_gui()
            self.select_kth_level(self.level, None)
            self.setup_key_bindings()
            self.root.mainloop()

    def auto_select_directory(self):
        """Simulates the selection of a directory as if done via GUI, based on the level."""
        # Simulate the logic that happens when a directory is selected in the GUI

        idx = 0
        selected_directory = ""
        while idx < self.level:
            selected_directory = os.path.join(
                selected_directory, self.directory_structure[1][idx]
            )
            idx = idx + 1
        # Replace dots and construct the limiter directory
        limiter_directory = selected_directory.replace("/.", "\\")
        limiter_directory = os.path.join(limiter_directory, ".obsidian\\")
        limiter_directory = os.path.normpath(limiter_directory)

        # Assign the selected directory to the class instance attribute
        self.selected_limiter_directory = limiter_directory

        # Check if the selected directory is the vault root
        vault_root = self.directory_structure[0]
        self.selected_limiter_is_vaultroot = limiter_directory == vault_root

    def adjust_default_Level(self):
        """translate default level into correct integer for treeview-handling"""

        """
        Level = 0 > manuscript_dir
        Level = -1 > true vault-root
        Level > 0 = manuscript_dir - level

        """

        if self.default_level == -1:  # vault-root
            lvl = 1
        elif self.default_level == 0:  # manuscript-dir
            lvl = len(self.directory_structure[1])
        else:
            lvl = len(self.directory_structure[1]) - self.default_level
        if lvl < 0:
            self.level = 1
        elif lvl == 0:
            self.level = 1
        else:
            self.level = lvl

    def adjust_directory_structure(self):
        idx = 0
        self.adjusted_directory_structure = self.directory_structure
        for each in self.adjusted_directory_structure[1]:
            idx = idx + 1
            if idx == 1:
                head = each
                rep = head + "/"
                rep = rep.replace("//", "/")
                self.adjusted_directory_structure[1][idx - 1] = rep
                continue
            # self.directory_structure[1][idx - 1] = os.path.normpath(
            #     os.path.join(head, each)
            # )
            rep = head + "/." + each + "/"
            rep = rep.replace("//", "/")
            self.adjusted_directory_structure[1][idx - 1] = rep
            # + "/"
            head = self.adjusted_directory_structure[1][idx - 1]
        rep = self.adjusted_directory_structure[1][idx - 1] + "/"
        rep = rep.replace("//", "/")
        self.adjusted_directory_structure[1][idx - 1] = rep

    def setup_gui(self):
        self.root.title("Obsidian Vault Selector")
        self.root.geometry(f"{self.width}x{self.height}")  # set geometry
        title_bar_factor = 0.04 if True else 0.00
        main_frame = tk.Frame(self.root, bg="green" if True else None)
        main_frame.place(
            x=0,
            y=self.height * title_bar_factor,
            width=self.width,
            height=(self.height * (1 - title_bar_factor)),
        )
        vault_root_label = tk.Label(
            main_frame, text=f"Vault root: {self.directory_structure[0]}"
        )
        vault_root_label.pack(side=tk.TOP, anchor=tk.W)
        self.adjust_directory_structure()
        a = len(self.adjusted_directory_structure[1])
        self.tree = TtkCheckList(
            main_frame,
            height=len(self.adjusted_directory_structure[1]),
            clicked=partial(check_new, self),
        )  # TODO: replace this with the tkchecklist in 'treeview_checkboxes.py'. Then implement the callbacks for selecting the correct indeces.
        for item in self.adjusted_directory_structure[1]:
            logging.debug(item)
            self.tree.add_item(item)
        self.tree.pack(expand=True, fill=tk.BOTH, anchor=tk.W)
        self.tree.heading("#0", text="Vault Structure", anchor="w")
        # self.build_tree()
        self.tree.pack()
        submit_button = tk.Button(self.root, text="Submit Folder", command=self.submit)
        submit_button.pack()
        pass

    def close(self):
        self.root.destroy()

    def submit(self, event=None):
        self.close()
        pass

    def setup_key_bindings(self):
        self.root.bind("<Alt-q>", self.select_first_level)
        self.root.bind("<Alt-e>", self.select_last_level)
        lD = len(self.directory_structure[1]) + 1
        for i in range(1, lD):  # Bind Alt+1 to Alt+9
            self.root.bind(
                f"{i}", lambda event, idx=i: self.select_kth_level(idx, event)
            )
            logging.debug(f"binding '<Alt-{i}>'")

        self.root.bind("<Alt-s>", self.submit)

    def select_first_level(self, event):
        if event is not None:
            if not (event.state & 0x0008):
                return
        children = self.tree.get_children()
        if children:  # Check if there are any items
            iid = children[0]  # Get the iid of the first item
            check_new(self, iid)

    def select_last_level(self, event):
        if event is not None:
            if not (event.state & 0x0008):
                return
        children = self.tree.get_children()
        if children:  # Check if there are any items
            not_last = True
            while not len(children) == 0:
                iid = children[-1]  # Get the iid of the last item
                children = self.tree.get_children(iid)

            check_new(self, iid)

    def select_kth_level(self, k, event):
        if event is not None:
            if not (event.state & 0x0008):
                return
        index = 0
        children = self.tree.get_children()
        if children:
            while True:
                index = index + 1
                iid = children[-1]
                if index == k:
                    break
                else:
                    children = self.tree.get_children(iid)
            check_new(self, iid)

    def add_limiter(self):
        if self.selected_limiter_is_vaultroot:
            self.logger.debug("Selected limiter is the vault root. No action taken.")
            self.selected_limiter_preexisted = True
            return

        # Check if the directory exists
        if os.path.exists(self.selected_limiter_directory):
            self.selected_limiter_preexisted = True
            self.logger.info(
                f"Directory '{self.selected_limiter_directory}' already exists. No action taken."
            )
        else:
            # Create the directory
            os.makedirs(self.selected_limiter_directory)
            self.selected_limiter_preexisted = False
            self.logger.info(f"Created directory '{self.selected_limiter_directory}'.")
            # self.close()

    def remove_limiter(self):
        if self.selected_limiter_is_vaultroot:
            self.logger.warning("Cannot remove limiter; it is the vault root.")
            return

        if self.selected_limiter_preexisted:
            self.logger.warning("Cannot remove limiter; it was pre-existing.")
            return

        # Remove the limiter directory
        try:
            os.rmdir(self.selected_limiter_directory)  # Only remove if empty
            self.logger.info(f"Removed directory '{self.selected_limiter_directory}'.")
            self.removed_selected_limiter_directory_success = True
        except Exception as e:
            self.logger.error(
                f"Failed to remove directory '{self.selected_limiter_directory}': {e}"
            )

    def build_tree(self):
        a = self.directory_structure[1]
        level = 1
        Levels = []
        for path in a:
            if level == 1:
                id = self.tree.insert("", "end", text=os.path.basename(path), open=True)
            else:
                id = self.tree.insert(id, "end", text=path, open=True)
            Levels.append(id)

            level = level + 1

    def assemble_tv_string(array):
        tv_string = ""
        for idx, val in enumerate(reversed(array), start=1):
            indent = "\t" * idx
            tv_string += f"{indent}{val}\tIcon4 expand\n"
        return tv_string

    def find_obsidian_vault_root(self, reset=False):
        found_location = ""
        stack = deque() if reset else deque()  # Initialize or reset the directory stack
        path = self.manuscript_path
        original_path = path.rstrip("\\")  # Remove trailing backslash if present

        # If path is a file, use its directory
        if not os.path.isdir(original_path):
            path = os.path.dirname(original_path)
        else:
            stack.append(os.path.basename(original_path))  # Add to stack if directory

        while True:
            # Construct the Obsidian folder path to check

            obsidian_check_path = os.path.join(path, ".obsidian")

            # Check if the directory contains the .obsidian folder
            if os.path.isdir(obsidian_check_path):
                obsidian_vault_path = obsidian_check_path
                stack.appendleft(path)
                return obsidian_vault_path, list(stack)

            # If we have reached the root directory, stop the search
            parent_dir = path

            # Move up one directory level
            if parent_dir not in stack:  # Avoid circular appending
                stack.appendleft(
                    os.path.basename(parent_dir)
                )  # Add parent directory to the front of the stack
            path = os.path.dirname(parent_dir)  # Update path to parent directory


def check_new(instance, iid):
    """
    If the status of an item is toggled, the status of all its descendants
    is also set to the new status.
    """
    check_list = instance.tree

    def uncheck_recursively(item):
        check_list.uncheck(item)
        for subitem in check_list.get_children(item):
            uncheck_recursively(subitem)

    # Uncheck all items
    for item in check_list.get_children():
        uncheck_recursively(item)

    # Now check the selected item
    check_list.check(iid)
    limiter_directory = iid
    limiter_directory = limiter_directory.replace("/.", "\\")
    limiter_directory = os.path.join(limiter_directory, ".obsidian\\")
    limiter_directory = os.path.normpath(limiter_directory)
    instance.selected_limiter_directory = limiter_directory
    # 'iid' here  basically makes it free for me to assemble the path-string, as long
    # as I can determine if I can clean out the dots properly. If that is the case, I could just self-assign
    # `self.tv_selection_string = iid`
    # and then parse out the dots to get my selected path during submission.
    instance.selected_limiter_is_vaultroot = (
        limiter_directory == instance.directory_structure[0]
    )
