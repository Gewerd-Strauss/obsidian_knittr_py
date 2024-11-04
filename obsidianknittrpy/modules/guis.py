import tkinter as tk
from tkinter import ttk
import pyperclip as pc
import os as os
import warnings as wn


class ObsidianKnittrGUI:
    def __init__(self):
        self.output_types = [
            "quarto::pdf",
            "quarto::html",
            "quarto::docx",
        ]  # Example types
        self.file_history = [
            "A1",
            "B1",
            "C1",
            "A2",
            "B2",
            "C2",
            "A3",
            "B3",
            "C3",
            "A4",
            "B4",
            "C4",
            "A5",
            "B5",
            "C5",
            "A6",
            "B6",
            "C6",
            "A7",
            "B7",
            "C7",
        ]
        self.output_selections = {}
        self.root = tk.Tk()
        self.title = "Obsidian Knittr - automate Obsidian.md conversion"
        self.root.title(self.title)
        self.width = 750
        self.height = 550
        self.root.geometry(f"{self.width}x{self.height}")  # set geometry
        self.root.minsize(self.width, self.height)  # set minimum size
        self.root.resizable(False, False)  # disable resizing of GUI
        self.root.wm_attributes("-topmost", 1)
        self.obsidian_options_selections = {
            "verb": tk.IntVar(),
            "use_custom_fork": tk.IntVar(),
            "purge_errors": tk.IntVar(),
            "verbose_flag": tk.IntVar(),
            "limit_scope": tk.IntVar(),
        }
        self.gen_config_selections = {
            "remove_hashtags": tk.IntVar(),
            "strip_local_md_links": tk.IntVar(),
            "keep_filename": tk.IntVar(),
            "render_to_outputs": tk.IntVar(),
            "backup_output_before_rendering": tk.IntVar(),
        }
        self.engine_config_selections = {
            "quarto_strip_reference_prefixes": tk.IntVar(),
        }

        self.classname = "ObsidianKnittrGUI"

        # Disable the close button
        def disable_event():
            pass

        self.root.protocol("WM_DELETE_WINDOW", disable_event)
        self.root.configure(bg="#1d1f21")
        self.bind_method_hotkey("<Alt-s>", "submit")
        self.bind_method_hotkey("<Alt-f>", "full_submit")
        self.bind_method_hotkey("<Alt-a>", "show_about")
        self.bind_method_hotkey("<Alt-c>", "choose_file")
        self.bind_method_hotkey("<Escape>", "close")
        self.setup_gui()
        self.update_filehistory()
        self.load_configuration()
        self.root.mainloop()

    def bind_method_hotkey(self, hotkey, method):
        self.root.bind(hotkey, lambda event: getattr(self, method)())

    def disable_event(self):
        pass

    def setup_gui(self):
        bg_col = "lightgrey"
        bg_col = None
        frame_margin_x = 5
        frame_margin_y = 5
        show_top_frame = False
        render_debug = False
        # Main frames for layout sections
        left_frame = tk.Frame(self.root, bg="green" if render_debug else None)
        right_frame = tk.Frame(self.root, bg="red" if render_debug else None)
        top_frame = tk.Frame(self.root, bg="purple" if render_debug else None)
        title_bar_factor = 0.04 if show_top_frame else 0.00

        top_frame.place(
            x=0, y=0, width=self.width, height=self.height * title_bar_factor
        )
        left_frame.place(
            x=0,
            y=self.height * title_bar_factor,
            width=self.width / 2,
            height=(self.height * (1 - title_bar_factor)),
        )
        right_frame.place(
            x=self.width / 2,
            y=self.height * title_bar_factor,
            width=self.width / 2,
            height=(self.height * (1 - title_bar_factor)),
        )
        output_frame_height = 275
        output_frame_width = self.width / 2 - 10
        output_frame_y = (
            frame_margin_y / 2 + 0
        )  # TODO: add title-string ObsidianKnittr to the top
        output_frame_x = frame_margin_x / 2
        # Left Top Section - "Choose Output Type"
        output_frame = tk.LabelFrame(left_frame, text="Choose Output Type", bg=bg_col)
        output_frame.place(
            x=output_frame_x,
            y=output_frame_y,
            width=output_frame_width,
            height=output_frame_height,
        )

        # # Left Middle Section - "Execution Directories"
        exec_dir_frame = tk.LabelFrame(
            left_frame, text="Execution Directories", bg=bg_col
        )
        exec_dir_frame_x = frame_margin_x / 2
        exec_dir_frame_y = output_frame_y + output_frame_height + frame_margin_y
        exec_dir_frame_height = 150
        exec_dir_frame_width = self.width / 2 - 10

        exec_dir_frame.place(
            x=exec_dir_frame_x,
            y=exec_dir_frame_y,
            width=exec_dir_frame_width,
            height=exec_dir_frame_height,
        )

        # # Left Bottom Section - "Last Execution"
        last_exec_frame = tk.LabelFrame(left_frame, text="Last Execution", bg=bg_col)

        last_exec_frame_x = frame_margin_x / 2
        last_exec_frame_y = exec_dir_frame_y + exec_dir_frame_height + frame_margin_y
        last_exec_frame_height = 70
        last_exec_frame_width = self.width / 2 - 10
        last_exec_frame.place(
            x=last_exec_frame_x,
            y=last_exec_frame_y,
            width=last_exec_frame_width,
            height=last_exec_frame_height,
        )
        version_frame_x = frame_margin_x / 2
        version_frame_y = last_exec_frame_y + last_exec_frame_height + frame_margin_y
        version_frame_height = 40
        version_frame_width = self.width / 2 - 10
        version_frame = tk.Frame(left_frame, bg=bg_col)
        version_frame.place(
            x=version_frame_x,
            y=version_frame_y,
            width=version_frame_width,
            height=version_frame_height,
        )

        manuscript_button_and_history_frame = tk.LabelFrame(
            right_frame, text="Manuscript", bg=bg_col
        )
        manuscript_button_and_history_frame_x = frame_margin_x / 2
        manuscript_button_and_history_frame_y = output_frame_y
        manuscript_button_and_history_frame_height = 120
        manuscript_button_and_history_frame_width = self.width / 2 - 10

        manuscript_button_and_history_frame.place(
            x=manuscript_button_and_history_frame_x,
            y=manuscript_button_and_history_frame_y,
            width=manuscript_button_and_history_frame_width,
            height=manuscript_button_and_history_frame_height,
        )
        obsidian_frame = tk.LabelFrame(right_frame, text="Obsidian HTML", bg=bg_col)
        obsidian_frame_x = frame_margin_x / 2
        obsidian_frame_y = (
            manuscript_button_and_history_frame_y
            + manuscript_button_and_history_frame_height
        ) + frame_margin_y
        obsidian_frame_height = 150
        obsidian_frame_width = self.width / 2 - 10

        obsidian_frame.place(
            x=obsidian_frame_x,
            y=obsidian_frame_y,
            width=obsidian_frame_width,
            height=obsidian_frame_height,
        )
        general_config_frame = tk.LabelFrame(
            right_frame, text="General Configuration", bg=bg_col
        )
        general_config_frame_x = frame_margin_x / 2
        general_config_frame_y = (
            obsidian_frame_y + obsidian_frame_height + frame_margin_y
        )
        general_config_frame_width = self.width / 2 - 10
        general_config_frame_height = 150
        general_config_frame.place(
            x=general_config_frame_x,
            y=general_config_frame_y,
            width=general_config_frame_width,
            height=general_config_frame_height,
        )

        engine_frame = tk.LabelFrame(
            right_frame, text="Engine-specific stuff", bg=bg_col
        )
        engine_frame_x = frame_margin_x / 2
        engine_frame_y = (
            general_config_frame_y + general_config_frame_height + frame_margin_y
        )
        engine_frame_width = self.width / 2 - 10
        engine_frame_height = last_exec_frame_height
        engine_frame.place(
            x=engine_frame_x,
            y=engine_frame_y,
            width=engine_frame_width,
            height=engine_frame_height,
        )
        button_frame = tk.Frame(right_frame, bg=bg_col)
        buttom_frame_x = frame_margin_x / 2
        buttom_frame_y = engine_frame_y + engine_frame_height + frame_margin_y
        buttom_frame_width = self.width / 2 - 10
        buttom_frame_height = version_frame_height
        button_frame.place(
            x=buttom_frame_x,
            y=buttom_frame_y,
            width=buttom_frame_width,
            height=buttom_frame_height,
        )
        ########## OUTPUT TYPES ##########
        canvas = tk.Canvas(output_frame)
        scrollbar = tk.Scrollbar(output_frame, orient="vertical", command=canvas.yview)
        checkbox_frame = tk.Frame(canvas)
        checkbox_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=checkbox_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.place(relwidth=0.9, relheight=1)
        scrollbar.place(relx=0.9, rely=0, relheight=1)

        for output_type in self.output_types:
            var = tk.IntVar()
            checkbox = tk.Checkbutton(checkbox_frame, text=output_type, variable=var)
            checkbox.pack(anchor=tk.W, padx=5, pady=2)
            self.output_selections[output_type] = var

        ########## CHOOSE MANUSCRIPT ##########
        # Right Top Section - "Choose Manuscript"
        manuscript_button = tk.Button(
            manuscript_button_and_history_frame,
            text="Choose Manuscript",
            command=self.choose_file,
        )
        manuscript_button.pack(side=tk.TOP, anchor=tk.W, padx=5)
        file_history_label = tk.Label(
            manuscript_button_and_history_frame, text="File History:"
        )
        file_history_label.pack(side=tk.TOP, anchor=tk.W)  # , padx=5)
        self.file_history_dropdown = ttk.Combobox(
            manuscript_button_and_history_frame, state="readonly"
        )
        self.file_history_dropdown.pack(
            fill=tk.X,
        )

        ########## OBSIDIAN HTML ##########
        # Right Top Section - "Obsidian HTML"
        # obsidian_frame.place(x=10, y=80, width=350, height=200)
        options = {
            "verb": "!!Use verb 'Convert' for OHTML",
            "use_custom_fork": "!!Use the personal fork",
            "purge_errors": "Purge OHTML-Error-strings",
            "verbose_flag": "Set OHTML's Verbose-Flag?",
            "limit_scope": "Limit scope of OHTML?",
        }

        for key, text in options.items():
            tk.Checkbutton(
                obsidian_frame,
                text=text,
                variable=self.obsidian_options_selections[key],
            ).pack(anchor=tk.W)

        ########## EXECUTION DIRECTORIES ##########
        tk.Label(exec_dir_frame, text="Choose execution directory for Quarto/R").pack(
            anchor=tk.W, padx=5, pady=5
        )
        self.exec_dir_selection = tk.IntVar(value=1)
        exec_dir_options = [
            ("1. OHTML-Output-Dir", 1),
            ("2. Subfolder of note-location in vault", 2),
        ]
        for txt, val in exec_dir_options:
            tk.Radiobutton(
                exec_dir_frame,
                text=txt,
                padx=20,
                variable=self.exec_dir_selection,
                value=val,
            ).pack(anchor=tk.W)

        def select_radio(event):
            if event.state & 0x0008:
                if event.keysym == "1":
                    self.exec_dir_selection.set(1)
                    show_radio()
                elif event.keysym == "2":
                    self.exec_dir_selection.set(2)
                    show_radio()

        def show_radio():
            pass
            print(self.exec_dir_selection.get())

        self.root.bind("1", select_radio)
        self.root.bind("2", select_radio)
        ########## GENERAL CONFIGURATION ##########

        gen_config_opts = {
            "remove_hashtags": "Remove '#' from tags",
            "strip_local_md_links": "Strip local markdown links",
            "keep_filename": "Keep filename",
            "render_to_outputs": "Render manuscripts to chosen outputs",
            "backup_output_before_rendering": "Backup Output files before rendering",
        }
        for key, text in gen_config_opts.items():
            tk.Checkbutton(
                general_config_frame,
                text=text,
                variable=self.gen_config_selections[key],
            ).pack(anchor=tk.W)
        ########## LAST EXECUTION ##########
        # # Left Bottom Section - "Last Execution"
        self.last_exec_label1 = tk.Label(last_exec_frame, text="Last execution info 1")
        self.last_exec_label2 = tk.Label(last_exec_frame, text="Last execution info 2")
        self.last_exec_label1.pack(anchor=tk.W, padx=5, pady=2)
        self.last_exec_label2.pack(anchor=tk.W, padx=5, pady=2)
        ########## ENGINE-SPECIFIC STUFF ##########
        # # Right Bottom Section - "Engine-specific stuff"
        engine_opts = {
            "quarto_strip_reference_prefixes": "Remove 'figure'/'table'/'equation' from inline references\nin quarto-documents"
        }
        for key, text in engine_opts.items():
            tk.Checkbutton(
                engine_frame,
                text=text,
                variable=self.engine_config_selections[key],
            ).pack(anchor=tk.W)
        ########## VERSIONS ##########
        # Bottom - Versions and Buttons
        version_label_1 = tk.Label(
            version_frame, text="ObsidianKnittr_py vX.Y.Z | Obsidian-HTML vX.Y.Z.hash"
        )
        version_label_2 = tk.Label(
            version_frame, text="Quarto-cli vX.Y.Z | Using quarto-cli"
        )
        version_label_1.pack(anchor=tk.W)  # place(relx=0.5, rely=0.9, anchor="center")
        version_label_2.pack(anchor=tk.W)  # place(relx=0.5, rely=0.92, anchor="center")

        ########## BOTTOM BUTTONS ##########
        tk.Button(button_frame, text="Submit", command=self.submit).pack(
            side=tk.LEFT, padx=1
        )
        tk.Button(button_frame, text="Full Submit", command=self.full_submit).pack(
            side=tk.LEFT, padx=1
        )
        tk.Button(
            button_frame, text="Edit General Config", command=self.edit_general_config
        ).pack(side=tk.LEFT, padx=1)
        tk.Button(button_frame, text="About", command=self.show_about).pack(
            side=tk.LEFT, padx=1
        )

    def choose_file(self):
        # Functionality for "Choose Manuscript" - placeholder
        # --
        filetypes = [("Markdown files", "*.md")]
        title = "Choose manuscript file"
        # --
        print("Choose Manuscript clicked")

        clipboard = pc.paste()
        path = clipboard.replace("/", "\\")

        if os.path.exists(path) and not os.path.isdir(path):
            ext = os.path.splitext(path)[1].lower()
            print(f"Path {path} from clipboard exists.")
            if ext == ".md":
                # self.root.withdraw()
                manuscript_path = path
        else:
            print("Clipboard does not hold a valid path, so open a file-dialog instead")
            # TODO: do we even port the setsearchroototolastmrunmanuscriptfolder stuff?
            # if (self.config.SetSearchRootToLastRunManuscriptFolder):
            allow_last_run = False
            if allow_last_run:
                last_run_dir = os.path.dirname(self.config.Lastrun.manuscriptpath)
                fp = tk.filedialog.askopenfilename(
                    initialdir=last_run_dir, title=title, filetypes=filetypes
                )
            else:
                allow_searchroot = False
                if allow_searchroot:
                    searchroot = self.config.config.searchroot
                else:
                    searchroot = os.path.expanduser("~")
                fp = tk.filedialog.askopenfilename(
                    initialdir=searchroot, title=title, filetypes=filetypes
                )
            if not os.path.exists(fp):
                wn.warn(
                    f"{self.classname}: File '{fp}' does not exist. Please select a different file."
                )
            ext = os.path.splitext(fp)[1].lower()
            if not ext == ".md":
                wn.warn(
                    f"{self.classname}: File '{fp}' is not a markdown-file. Please select a markdown-file (file-suffix: '.md')"
                )
            if fp == "":
                return  # no file selected
        print(fp)
        self.update_filehistory(fp)
        # self.root.deiconify()

    def update_filehistory(self, added_path=None):
        if added_path:
            # Move to beginning if already in the history
            if added_path in self.file_history:
                self.file_history.remove(added_path)
            # Add to the beginning
            self.file_history.insert(0, added_path)

        # Populate the Combobox with current file history
        self.file_history_dropdown["values"] = self.file_history

        # Select the most recent entry if the list is not empty
        if self.file_history:
            self.file_history_dropdown.current(0)

    def load_configuration(self):
        print(
            "load configuration to populate checkbxoes, output-types, execution-directories/last-execution/..."
        )
        pass

    def update_last_execution_labels(self, last_manuscript_path, last_level):
        """Update the text for last execution labels."""
        DL = -300
        wn.warn(
            f"pass through default config and implement  default level 'DL' {DL} here"
        )
        self.last_exec_label1.config(text=f"LM: {last_manuscript_path}")
        self.last_exec_label2.config(text=f"LL: {last_level} DL:{DL}")

    def submit(self):
        # output_type, execution_directories
        results = {}
        results["output_type"] = []
        for output_type, var in self.output_selections.items():
            if var.get():
                results["output_type"].append(output_type)

        if len(results["output_type"]) == 0:
            print(
                "no format selected, please select a format"
            )  # TODO: replace this with a notifyUser-call - since its a GUI, we must notify in it?
            return
        results["execution_directory"] = (
            self.exec_dir_selection.get()
        )  # Assuming v holds the selected radio button value

        # obsidian_html, general_configuration, engine_configurations
        results["obsidian_html"] = {}
        results["general_configuration"] = {}
        results["engine_configurations"] = {}
        for key, var in self.obsidian_options_selections.items():
            results["obsidian_html"][key] = bool(var.get())
        for key, var in self.gen_config_selections.items():
            results["general_configuration"][key] = bool(var.get())
        for key, var in self.engine_config_selections.items():
            results["engine_configurations"][key] = bool(var.get())
        # manuscript
        results["manuscript"] = {}
        results["manuscript"]["manuscript_path"] = self.file_history_dropdown.get()
        results["manuscript"]["manuscript_name"] = os.path.basename(
            results["manuscript"]["manuscript_path"]
        )
        results["manuscript"]["manuscript_dir"] = os.path.dirname(
            results["manuscript"]["manuscript_path"]
        )
        results["general_configuration"]["full_submit"] = False

        if results["obsidian_html"]["verb"]:
            results["obsidian_html"]["verb"] = "convert"
        else:
            results["obsidian_html"]["verb"] = "run"

        print("Submit clicked")
        print("Results:", results)  # Print the gathered results for verification
        self.results = results
        self.close()
        pass

    def full_submit(self):
        # output_type, execution_directories
        results = {}
        results["output_type"] = []
        for output_type, var in self.output_selections.items():
            if var.get():
                results["output_type"].append(output_type)
        results["execution_directory"] = (
            self.exec_dir_selection.get()
        )  # Assuming v holds the selected radio button value

        # obsidian_html, general_configuration, engine_configurations
        results["obsidian_html"] = {}
        results["general_configuration"] = {}
        results["engine_configurations"] = {}
        for key, var in self.obsidian_options_selections.items():
            results["obsidian_html"][key] = bool(var.get())
        for key, var in self.gen_config_selections.items():
            results["general_configuration"][key] = bool(var.get())
        for key, var in self.engine_config_selections.items():
            results["engine_configurations"][key] = bool(var.get())
        # manuscript
        results["manuscript"] = {}
        results["manuscript"]["manuscript_path"] = self.file_history_dropdown.get()
        results["manuscript"]["manuscript_name"] = os.path.basename(
            results["manuscript"]["manuscript_path"]
        )
        results["manuscript"]["manuscript_dir"] = os.path.dirname(
            results["manuscript"]["manuscript_path"]
        )
        results["general_configuration"]["full_submit"] = True
        if results["obsidian_html"]["verb"]:
            results["obsidian_html"]["verb"] = "convert"
        else:
            results["obsidian_html"]["verb"] = "run"

        print("Full Submit clicked")
        print("Results:", results)  # Print the gathered results for verification
        self.results = results
        self.close()
        pass

    def edit_general_config(self):
        # Placeholder for Edit General Config logic
        print("Edit General Config clicked")

    def show_about(self):
        # Placeholder for About dialog
        print("About clicked")
        self.update_last_execution_labels("A", "B")

    def close(self):
        self.root.destroy()


#########

from obsidianknittrpy.modules.DynamicArguments import OT
from obsidianknittrpy import __config__


def handle_ot_guis(args, pb):
    # Implement GUI launch logic here
    x = 1645
    y = 475
    ShowGui = 1
    for format in pb["objects"]["sel"]:
        ot = OT(
            config_file=__config__,
            format=format,
            DDL_ParamDelimiter="-<>-",
            skip_gui=pb["settings"]["general_configuration"]["full_submit"],
            stepsized_gui_show=False,
        )  # Create instance of OT

        # Check if args is not empty and is iterable
        if not not args:
            for param, value in args.items():
                if format not in param:  # Check if format is in param
                    continue
                param_ = param.replace(format + ".", "")  # Replace the format prefix
                if param_ in ot.arguments:  # Check if the parameter exists in Arguments
                    # Set the default such that the GUI also reflects it
                    # Note: If we decide to set skip_gui=True when running CLI, we only have
                    # to set the 'Value'-field to `value`.
                    # However, this loop then must be taken _after_ the GUI was skipped.
                    # The disadvantage is that if a GUI _is_ rendered, any argument passed
                    # through the commandline will not be displayed with its updated value.
                    # Additionally, that value will not actually be submitted because the
                    # commandline-ported argument would then be inserted over the user's
                    # potential choice afterwards.
                    #
                    #
                    # there are 2 options to solve this:
                    # 1. either make the GUI always overwrite commandline-selections
                    #   - in this case the GUI should render the changes from the commandline
                    #     first, such that the user has the educated knowledge of the right state
                    # 2. disable commandline-fed arguments when running gui-mode, and force the
                    #    user to do all changes themselves. Essentially disabling the CL-support
                    #    in GUI-mode; but I am not sure.
                    # .

                    ot.arguments[param_]["Value"] = value  # Set the Value
                    ot.arguments[param_]["Default"] = value

        if ShowGui:
            setattr(
                ot, "SkipGUI", pb["settings"]["general_configuration"]["full_submit"]
            )  # Set the attribute SkipGUI
            ot.generate_gui(
                x, y, True, "ParamsGUI:", 1, 1, 674, ShowGui
            )  # Call GenerateGUI method
        ot.assemble_format_string()  # Call AssembleFormatString method
        pb["objects"]["output_formats"][format] = ot
    for format, ot in pb["objects"]["output_formats"].items():
        # Here, format is the key (e.g., "quarto::docx")
        # and ot is the instance of the OT class
        print(f"Format: {format}, Output Type: {ot.type}, Arguments: {ot.arguments}")

    return pb
