import tkinter as tk
from tkinter import ttk


class ObsidianKnittrGUI:
    def __init__(self):
        self.output_types = [
            "quarto::pdf",
            "quarto::html",
            "quarto::docx",
            "quarto::pdf",
            "quarto::html",
            "quarto::docx",
            "quarto::pdf",
            "quarto::html",
            "quarto::docx",
            "quarto::pdf",
            "quarto::html",
            "quarto::docx",
            "quarto::pdf",
            "quarto::html",
            "quarto::docx",
            "quarto::pdf",
            "quarto::html",
            "quarto::docx",
        ]  # Example types
        self.output_selections = {}
        self.root = tk.Tk()
        self.title = "Obsidian Knittr - automate Obsidian.md conversion"
        self.root.title(self.title)
        self.root.geometry("800x700")  # set geometry
        self.root.minsize(800, 700)  # set minimum size
        self.root.resizable(False, False)  # disable resizing of GUI

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
        self.root.mainloop()

    def bind_method_hotkey(self, hotkey, method):
        self.root.bind(hotkey, lambda event: getattr(self, method)())

    def disable_event(self):
        pass

    def setup_gui(self):
        # Title Label (Top full-width)
        # title_label = tk.Label(self.root, text=self.title, font=("Helvetica", 16))
        # title_label.pack(fill=tk.X, padx=5, pady=5)
        bg_col = "lightgrey"

        # Main frames for layout sections
        left_frame = tk.Frame(self.root)
        right_frame = tk.Frame(self.root)
        # bottom_frame = tk.Frame(self.root)

        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5, pady=5)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=5, pady=5)
        # bottom_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5, pady=5)

        # Left top section: "Choose Output Type" with static height and scrollable checkboxes
        output_frame = tk.LabelFrame(
            left_frame, text="Choose Output Type", padx=5, pady=5, height=8, bg=bg_col
        )
        output_frame.pack(fill=tk.X)

        # Set a static height for the output frame
        output_frame.configure(height=2)

        # Create a scrollable frame for checkboxes
        canvas = tk.Canvas(output_frame)
        scrollbar = tk.Scrollbar(output_frame, orient="vertical", command=canvas.yview)
        checkbox_frame = tk.Frame(canvas)

        checkbox_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=checkbox_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Add checkboxes for each output type in the scrollable frame
        for output_type in self.output_types:
            var = tk.IntVar()
            checkbox = tk.Checkbutton(checkbox_frame, text=output_type, variable=var)
            checkbox.pack(anchor=tk.W, padx=5, pady=2)
            self.output_selections[output_type] = var

        # Right top section: "Choose manuscript" and file history dropdown
        right_top_frame = tk.Frame(right_frame)
        right_top_frame.pack(fill=tk.X, padx=5, pady=5)

        manuscript_button = tk.Button(
            right_top_frame, text="Choose Manuscript", command=self.choose_file
        )
        manuscript_button.pack(side=tk.LEFT, padx=5)

        file_history_label = tk.Label(right_top_frame, text="File History:")
        file_history_label.pack(side=tk.LEFT, padx=5)

        file_history_dropdown = ttk.Combobox(right_top_frame)
        file_history_dropdown.pack(side=tk.LEFT, fill=tk.X, expand=False, padx=5)

        # Right middle section: Obsidian HTML options with checkboxes
        obsidian_frame = tk.LabelFrame(
            right_frame, text="Obsidian HTML", padx=5, pady=5
        )
        obsidian_frame.pack(fill=tk.BOTH, expand=False)

        # for _ in range(5):
        tk.Checkbutton(obsidian_frame, text="!!Use verb 'Convert' for OHTML").pack(
            anchor=tk.W, padx=5, pady=2
        )
        tk.Checkbutton(obsidian_frame, text="!!Use the personal fork").pack(
            anchor=tk.W, padx=5, pady=2
        )
        tk.Checkbutton(obsidian_frame, text="Purge OHTML-Error-strings").pack(
            anchor=tk.W, padx=5, pady=2
        )
        tk.Checkbutton(obsidian_frame, text="Set OHTML's Verbose-Flag?").pack(
            anchor=tk.W, padx=5, pady=2
        )
        tk.Checkbutton(obsidian_frame, text="Limit scope of OHTML?").pack(
            anchor=tk.W, padx=5, pady=2
        )

        # Left middle section: Execution Directories (as a text label)
        exec_dir_frame = tk.LabelFrame(
            left_frame, text="Execution Directories", padx=5, pady=5
        )
        exec_dir_frame.pack(fill=tk.BOTH, expand=False)

        exec_dir_label = tk.Label(
            exec_dir_frame, text="Choose execution directory for Quarto/R"
        )
        exec_dir_label.pack(anchor=tk.W, padx=5, pady=5)
        self.v = tk.IntVar()
        self.v.set(1)

        exec_dir_options = [
            ("&1. OHTML-Output-Dir", 1),
            ("&2. subfolder of note-location in vault", 2),
        ]

        def select_radio(event):
            if event.state & 0x0008:
                if event.keysym == "1":
                    self.v.set(1)
                    show_radio()
                elif event.keysym == "2":
                    self.v.set(2)
                    show_radio()

        def show_radio():
            pass
            print(self.v.get())

        for txt, val in exec_dir_options:
            tk.Radiobutton(
                exec_dir_frame,
                text=txt,
                padx=20,
                variable=self.v,
                command=show_radio,
                value=val,
            ).pack(anchor="w")

        self.root.bind("1", select_radio)
        self.root.bind("2", select_radio)

        # tk.Radiobutton(
        #     exec_dir_frame, text="OHTML-Output-Dir", variable=v, value=1
        # ).pack(anchor="w")
        # tk.Radiobutton(
        #     exec_dir_frame, text="OHTML-Output-Dir", variable=v, value=2
        # ).pack(anchor="w")

        # Bottom-aligned Last Execution and Engine-Specific Stuff frames
        last_exec_frame = tk.LabelFrame(
            left_frame, text="Last Execution", padx=5, pady=5
        )
        last_exec_frame.pack(fill=tk.BOTH, expand=False)

        last_exec_label1 = tk.Label(last_exec_frame, text="Last execution info 1")
        last_exec_label2 = tk.Label(last_exec_frame, text="Last execution info 2")
        last_exec_label1.pack(fill=tk.X, padx=5, pady=2)
        last_exec_label2.pack(fill=tk.X, padx=5, pady=2)

        # Button frame with named buttons for actions, placed below the height of the group boxes
        version_frame = tk.LabelFrame(left_frame, text="Versions", padx=5, pady=5)
        version_frame.pack(fill=tk.BOTH, expand=False)

        version_label_1 = tk.Label(
            version_frame, text="ObsidianKnittr_py vX.Y.Z | Obsidian-HTML vX.Y.Z.hash"
        )
        version_label_2 = tk.Label(
            version_frame, text="Quarto-cli vX.Y.Z | Using quarto-cli"
        )
        version_label_1.pack(fill=tk.X, padx=5, pady=2)
        version_label_2.pack(fill=tk.X, padx=5, pady=2)

        # Right top section: General Configuration
        general_config_frame = tk.LabelFrame(
            right_frame, text="General Configuration", padx=5, pady=5
        )
        general_config_frame.pack(fill=tk.BOTH, expand=False)

        tk.Checkbutton(general_config_frame, text="Remove '#' from tags").pack(
            anchor=tk.W, padx=5, pady=2
        )
        tk.Checkbutton(general_config_frame, text="Strip local markdown links").pack(
            anchor=tk.W, padx=5, pady=2
        )
        tk.Checkbutton(general_config_frame, text="Keep filename").pack(
            anchor=tk.W, padx=5, pady=2
        )
        tk.Checkbutton(
            general_config_frame, text="Render manuscripts to chosen outputs"
        ).pack(anchor=tk.W, padx=5, pady=2)
        tk.Checkbutton(
            general_config_frame, text="Backup Output files before rendering"
        ).pack(anchor=tk.W, padx=5, pady=2)

        # Right bottom section: Engine-specific settings
        engine_frame = tk.LabelFrame(
            right_frame, text="Engine-specific Stuff", padx=5, pady=5
        )
        engine_frame.pack(fill=tk.BOTH, expand=True)

        tk.Checkbutton(
            engine_frame,
            text="Remove 'figure'/'table'/'equation' from inline\nreferences in quarto-documents",
        ).pack(anchor=tk.W, padx=5, pady=2)

        exec_dir_label.pack(anchor=tk.W, padx=5, pady=5)

        button_frame = tk.Frame(right_frame, padx=5, pady=5)
        button_frame.pack(pady=5)

        tk.Button(button_frame, text="Submit", command=self.submit).pack(
            side=tk.LEFT, padx=5
        )
        tk.Button(button_frame, text="Full Submit", command=self.full_submit).pack(
            side=tk.LEFT, padx=5
        )
        tk.Button(
            button_frame, text="Edit General Config", command=self.edit_general_config
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="About", command=self.show_about).pack(
            side=tk.LEFT, padx=5
        )

    def choose_file(self):
        # Functionality for "Choose Manuscript" - placeholder
        print("Choose Manuscript clicked")

    def submit(self):
        # Placeholder for Submit logic
        print("Submit clicked")

    def full_submit(self):
        # Placeholder for Full Submit logic
        print("Full Submit clicked")

    def edit_general_config(self):
        # Placeholder for Edit General Config logic
        print("Edit General Config clicked")

    def show_about(self):
        # Placeholder for About dialog
        print("About clicked")

    def close(self):
        self.root.destroy()
