import re
import os
from math import floor
import logging as logging
import webbrowser
import tkinter as tk
import warnings as wn
from tkinter import ttk, filedialog, messagebox


class OT_Argument:
    def __init__(
        self,
        control=None,
    ):
        self.Control = control

    # def __setitem__(self,key):

    def __getitem__(self, key):
        # Allow dictionary-like access
        return getattr(self, key, None)

    def __setitem__(self, key, value):
        setattr(self, key, value)  # Allow setting attributes using bracket notation

    def get(self, key, default=None):
        return getattr(self, key, default)

    def __contains__(self, key):
        # Check for attribute existence without triggering __getattr__
        return key in self.__dict__

    def __getattr__(self, key):
        # Return None if the attribute does not exist
        return None


class OT:
    # __New(Format:="",ConfigFile:="",DDL_ParamDelimiter:="-<>-",SkipGUI:=FALSE,StepsizedGuiShow:=FALSE) {
    def __init__(
        self,
        config_file="",
        format="",
        DDL_ParamDelimiter="-<>-",
        skip_gui=False,
        stepsized_gui_show=False,
        loglevel="Info",
    ):
        self.loglevel = loglevel
        self.logger = logging.getLogger(
            self.__class__.__module__ + "." + self.__class__.__qualname__
        )
        self.logger.setLevel(loglevel)
        self.config_file = config_file
        self.type = format
        self.DDL_ParamDelimiter = DDL_ParamDelimiter
        self.skip_gui = skip_gui
        self.stepsized_gui_show = stepsized_gui_show

        self.classname = "ot (" + format + ")"
        # this.GUITitle="Define output format - "
        self.version = "0.1.a"
        self.gui_instance = None
        # this.bClosedNoSubmit=false
        self.arguments = {}
        self.error = None
        self.errors = (
            (
                -1,
                "Provided Configfile does not exist:\n\n",
                "\n\n---\nExiting Script",
                -100,
            ),
            (0, "Gui got cancelled", "\n\n---\nReturning to General Selection", 0),
            (
                +2,
                "Format not defined.\nCheck your configfile.\n\nReturning default 'outputformat()'",
                "",
                20,
            ),
        )

        self.load_config()
        self.assume_defaults()
        self.adjust()

    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    text = f.read()
            else:
                text = self.config_file

            # Split into sections based on format
            if str(self.type + "\n") not in text:
                raise ValueError(
                    f"The string '{self.type}' was not found in the format-definitions."
                )
            lines = (
                text.split(self.type + "\n")[1].split("\n\n")[0].strip().splitlines()
            )

            if not lines:
                self.result = self.type + "()"
                self.error = self.errors[2]
                print(f"{self.__class__.__name__} > Initialization Error: {self.error}")
                return

            current_param = None

            for line in lines:
                line = line.strip()
                if not line or line.startswith(";"):  # Skip comments and empty lines
                    continue

                # Check if the line defines a rendering package - this is metadata
                if "renderingpackage" in line:
                    key = line.split(":")[0]
                    key_value_pairs = line.split("|")
                    current_param = None
                    for kv in key_value_pairs:
                        if not kv.count("Value:"):
                            continue
                        k__ = kv.split("Value:")[1]
                        if current_param is None:
                            # self.key = k__
                            setattr(self, key, k__)
                    continue

                # Split the line by the pipe character to extract key-value pairs
                key_value_pairs = line.split("|")
                ind = 0
                current_param = None
                for kv in key_value_pairs:
                    ind = ind + 1
                    key, value = self.parse_key_value(kv)
                    if key and value:
                        if current_param is None:
                            current_param = key
                            # Initialize a new Argument instance with Control set
                            self.arguments[current_param] = OT_Argument(control=value)
                        else:
                            # Populate the argument properties based on subsequent key-value pairs
                            setattr(self.arguments[current_param], key, value)
            self.arguments = {
                key: self.arguments[key] for key in sorted(self.arguments)
            }
            # print(self.get_error(0))
        except FileNotFoundError:
            print(f"Configuration file '{self.config_file}' not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def assemble_format_string(self):
        if hasattr(self, "renderingpackage_start"):
            if not hasattr(self, "renderingpackage_end"):
                raise ValueError(
                    f"output_type: {self.type} - faulty meta parameter\n"
                    "The meta parameter\n'renderingpackage_end'\ndoes not exist. Exiting. "
                    "Please refer to documentation and fix the file 'DynamicArguments.ini'."
                )
            fmt_str = self.renderingpackage_start
        else:
            if "::" in self.type:  # Check for start string
                fmt_str = (
                    self.type + "(\n"
                )  # Check if format is from a specific package
            else:
                fmt_str = (
                    "rmarkdown::" + self.type + "(\n"
                )  # Assume rmarkdown-package if not the case
        # self.arguments["number-depth"]["Value"] = -2
        self.adjust()

        for parameter, value in self.arguments.items():
            if value.get("Control") in ["meta", "Meta"]:
                continue

            if value.get("Value") == "" and value.get("Default") == "":
                continue

            if "___" in parameter:
                parameter = "'" + parameter.replace("___", "-") + "'"
            elif "-" in parameter:
                parameter = "'" + parameter + "'"

            if parameter == "toc_depth" and not self.arguments["toc"]["Value"]:
                continue

            if (
                value.get("Type") == "String"
                and value.get("Value") != ""
                and value.get("Default") != "NULL"
            ):
                value["Value"] = self.da_quote(value["Value"])

            if "reference_docx" in parameter or "reference-doc" in parameter:
                param_backup = value["Value"]
                if self.DDL_ParamDelimiter in value["Value"]:
                    param_string = value["Value"].split(self.DDL_ParamDelimiter)[1]
                else:
                    param_string = value["Value"]

                if "(" in param_string:
                    param_string = param_string.split("(")[1].strip('"')
                    if param_string.endswith(")"):
                        param_string = param_string[:-1]

                param_string = param_string.replace("\\", "/")
                value["Value"] = self.da_quote(param_string)

                if param_string == "":
                    value["Value"] = self.da_quote(
                        param_backup.strip('"').replace("\\", "/")
                    )

                if self.DDL_ParamDelimiter in param_backup:
                    param_backup = param_backup.split(self.DDL_ParamDelimiter)[
                        1
                    ].strip()

                if not os.path.exists(value["Value"]) and not os.path.exists(
                    param_backup.replace("\\", "/")
                ):
                    value["Value"] = self.da_quote(
                        param_backup.strip('"').replace("\\", "/")
                    )

                if not os.path.exists(value["Value"].strip('"')) and not os.path.exists(
                    param_backup.replace("\\", "/")
                ):
                    raise ValueError(
                        f"output_type: {self.type} - faulty reference_docx\n"
                        f"The given path to the reference docx-file\n'{value['Value']}'\ndoes not exist. Returning."
                    )

            fmt_str += f"{parameter} = {value['Value']},\n"

        # Handle removal of meta keys
        meta_keys_are_present = True
        while meta_keys_are_present:
            present_meta_keys = 0
            for parameter, value in list(self.arguments.items()):
                if value.get("Control") in ["meta", "Meta"]:
                    del self.arguments[parameter]

            for value in self.arguments.values():
                if value.get("Control") in ["meta", "Meta"]:
                    present_meta_keys += 1

            meta_keys_are_present = present_meta_keys > 0

        fmt_str = fmt_str[:-2]  # Remove the last comma and newline
        fmt_str += "\n)" if "\n" in fmt_str else ""

        if self.renderingpackage_start in fmt_str:
            if hasattr(self, "renderingpackage_end"):
                fmt_str = fmt_str.replace("\n)", self.renderingpackage_end)

        self.assembled_format_string = fmt_str
        return

    def assume_defaults(self):
        for parameter, value in self.arguments.items():
            if value["Control"] == "meta" or value["Control"] == "Meta":
                setattr(self, parameter, value["Value"])
                continue
            # Remove quotation marks from paths and strings
            if "SearchPath" in value:
                value["SearchPath"] = value["SearchPath"].replace('"', "")
            if "String" in value:
                value["String"] = value["String"].replace('"', "")

            # Remove quotation marks from default values if type is string
            if value.get("Type") == "String":
                value["Default"] = value["Default"].replace('"', "")

            # Set Value to Default if Value is empty
            if value.Value == None:
                if value.get("Control") == "file":
                    # Check if the file exists in the SearchPath with Default as filename
                    file_path = os.path.join(value["SearchPath"], value["Default"])
                    if not os.path.exists(file_path) and (file_path != ""):
                        raise FileExistsError(
                            f"output_type: {self.type}\nThe default file\n'{file_path}'\ndoes not exist. No default set."
                        )
                    else:
                        value["Value"] = file_path
                else:
                    value["Value"] = value.get("Default", "")

    def adjust(self):
        self.adjust_min_max()
        self.adjust_ddls()
        self.adjust_bools()
        self.adjust_integers()
        self.adjust_nulls()
        return self

    def adjust_min_max(self):
        """Ensures that numerical values fulfil 'Min <= Value <= Max'. Sets Value to 'Max' if 'Value>Max', and to 'Min' if 'Value<Min'. Sets to 'Default' if not'Min<=Value<=Max'."""
        for parameter, value in self.arguments.items():
            value_type = value.get("Type")
            if value_type is not None:
                value_type = value_type.lower()
            convert_func = None

            # Determine the conversion function based on the type
            if value_type == "integer":
                convert_func = int
            elif value_type == "number":
                convert_func = float
            else:
                continue  # Skip if the type is not recognized

            # # Try to convert the current value
            # try:
            #     current_value = convert_func(value["Value"])
            # except (ValueError, TypeError):
            #     # Handle cases where the conversion fails, e.g., set to Default
            #     if "Default" in value:
            #         value["Value"] = convert_func(
            #             value["Default"]
            #         )  # Convert Default value if necessary
            #     continue  # Skip further checks if conversion fails

            if "Max" in value and convert_func(value["Value"]) > convert_func(
                value["Max"]
            ):
                value["Value"] = convert_func(value["Max"])

            if "Min" in value and convert_func(value["Min"]) > convert_func(
                value["Value"]
            ):
                value["Value"] = convert_func(value["Min"])

            if "Max" in value and "Min" in value:
                if not (
                    convert_func(value["Min"])
                    <= convert_func(value["Value"])
                    <= convert_func(value["Max"])
                ):
                    value["Value"] = convert_func(value["Default"])

    def adjust_ddls(self):
        pass

    def adjust_bools(self):
        def is_boolean(value):
            # Convert value to string and make it lowercase for case-insensitive matching
            str_value = str(value).strip().lower()

            # Check if the string representation matches any boolean representation
            if str_value in {"1", "0", "true", "false"}:
                return True
            return False

        for parameter, value in self.arguments.items():
            value_type = value.get("Type")
            if value_type is not None:
                value_type = value_type.lower()
            if value_type in ["boolean"]:
                # Ensure the Value can be converted to an int
                if isinstance(value["Value"], (int, float)):
                    value[
                        "Value"
                    ] += 0  # No change, just ensures it's treated as a number
                elif isinstance(value["Value"], str) and value["Value"].isdigit():
                    value["Value"] = int(value["Value"])  # Convert string to int
                else:
                    # Handle case where value cannot be converted to a number
                    if value["Value"].upper() not in ["TRUE", "FALSE"]:
                        raise TypeError(
                            f"[Pre-Boolean-check]: failed to cast parameter {parameter} with value [{value['Value']}] of type [{type(value['Value'])}] into boolean."
                        )

            # Convert boolean to "TRUE" or "FALSE"
            if value_type == "boolean":
                val_ = value["Value"]
                try:
                    if is_boolean(value["Value"]):
                        value["Value"] = "TRUE"
                    else:
                        value["Value"] = "FALSE"
                except:
                    raise TypeError(
                        f"[Pre-Boolean-check]: Parameter {parameter}: Value {value['Value']} with type [{type(value['Value'])}] is not a member of valid boolean-castable inputs ('1', '0', 'true', 'false')"
                    )

    def adjust_integers(self):
        for parameter, value in self.arguments.items():
            value_type = value.get("Type")
            if value_type is not None:
                value_type = value_type.lower()
            if value_type in ["integer"]:
                value["Value"] = floor(int(value["Value"]))

    def adjust_nulls(self):
        """Removes quotation marks from NULL-values"""
        for _, value in self.arguments.items():
            if value["Value"] == "NULL":
                value["Value"] = value["Value"].replace('"', "")

    def parse_key_value(self, kv):
        """Parse a key-value pair from the string."""
        match = re.match(r"(?P<Key>[-\w]+):(?P<Val>.*)", kv.strip())
        if match:
            return match.group("Key"), match.group("Val").strip()
        return None, None

    def get_error(self, id):
        """Retrieve an error message by ID."""
        for error in self.errors:
            if error[0] == id:
                return {
                    "ID": error[0],
                    "String": error[1],
                    "EndString": error[2],
                    "Criticality": error[3],
                }
        return None  # Return None if ID is not found

    def da_quote(self, string):
        """Returns the input string enclosed in double quotes."""
        return f'"{string}"'

    # GUI-related stuff

    def generate_gui(
        self,
        x,
        y,
        AttachBottom=True,
        GUI_ID="ParamsGUI:",
        destroyGUI=True,
        xpos_control=False,
        Tab3Width=674,
        ShowGui=False,
    ):
        """Generates the GUI: static and dynamic parts, and populates it."""
        print("Generates the GUI and populates it")
        self.gui_instance = OT_GUI(
            self.arguments, self.config_file, self.type, self.loglevel
        )

    def submit_gui():
        """After the GUI is submitted, this function must be called to modify the arguments in self.arguments if the user changed values in the GUI"""
        pass

    def destroy_gui():
        """submits and destroys the GUI, assigns error 0 to the error-state and returns self"""
        pass

    def ChooseFile():
        """Callback-function for 'File'-selection entries"""
        pass

    def EditConfig():
        """Opens the current configuration file for editing, and asks to reload after it gets saved"""
        # TODO: instead of always asking to reload, fileread the file before and after opening it, and do a comparison
        # such that user is only asked if the file has changed.
        pass

    def open_file_selection_folder():
        """opens the directory of a file-path on the file-system"""
        pass


import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime


class OT_GUI:
    def __init__(self, arguments, config_file, type, loglevel=None):
        self.root = tk.Tk()  # Initialize the Tkinter root window here
        self.classname = f"ot_gui ({type})"
        self.root.title(f"Params GUI ({type})")
        self.arguments = arguments  # Pass arguments for GUI elements
        self.config_file = config_file
        self.type = type
        self.tabs = ttk.Notebook(self.root)
        self.logger = logging.getLogger(
            self.__class__.__module__ + "." + self.__class__.__qualname__
        )
        self.logger.setLevel(level=loglevel)

        self.create_gui()
        self.bind_method_hotkey("<Alt-s>", "submit")
        self.bind_method_hotkey("<Alt-e>", "open_configuration_file")
        self.bind_method_hotkey("<Prior>", "switch_tab_up")
        self.bind_method_hotkey("<Next>", "switch_tab_down")
        self.bind_method_hotkey("<Escape>", "close")
        self.root.focus_force()  # makes window take keyboard focus immediately.
        # self.root.grab_set()  # makes window modal
        self.root.mainloop()  # Start the GUI event loop here

    def switch_tab_down(self, event=None):
        current_tab = self.tabs.index(self.tabs.select())
        total_tabs = len(self.tabs.tabs())
        next_tab = (current_tab + 1) % total_tabs  # Wrap around to the beginning
        self.tabs.select(next_tab)

    def switch_tab_up(self, event=None):
        current_tab = self.tabs.index(self.tabs.select())
        total_tabs = len(self.tabs.tabs())
        previous_tab = (current_tab - 1) % total_tabs  # Wrap around to the end
        self.tabs.select(previous_tab)

    def da_dateparse(self, date_string):
        """Convert date from YYYYMMDDHH24MISS format to datetime.date."""
        if len(date_string) >= 8:  # Ensure the string is long enough for YYYYMMDD
            return datetime.strptime(date_string[:8], "%Y%m%d").date()
        return None  # Return None if date_string is invalid

    def add_text(self, value, tab_frame, row_index):
        # Add the text label to the right of the link
        text_label = tk.Label(tab_frame, text=value["String"])
        text_label.grid(row=row_index, column=0, padx=(10, 0), sticky="w")

    def add_link(self, value, tab_frame, row_index):
        if "Link" in value:
            link = value["Link"]
            link_label = tk.Label(
                tab_frame,
                text=f"{value['Linktext']}",
                fg="blue",
                cursor="hand2",
            )
            link_label.bind("<Button-1>", lambda e, link=link: webbrowser.open(link))
            link_label.grid(row=row_index, column=0, sticky="w")

    def add_edit(self, value, tab_frame, row_index, control_options):
        if control_options == "Number" or value["Type"] in ["Integer"]:
            if "Max" in value and "Min" in value:
                # Add Spinbox for number range
                spinbox = ttk.Spinbox(
                    tab_frame,
                    from_=value["Min"],
                    to=value["Max"],
                    width=8,
                    validate="key",
                    validatecommand=(
                        self.root.register(self.validate_spinbox_input),
                        "%P",
                    ),
                )
                spinbox.grid(
                    row=row_index + 1,
                    column=0,
                    pady=(5, 0),
                    padx=(5, 0),
                    sticky="ew",
                )
                spinbox.delete(0, "end")  # Clear any existing text
                spinbox.insert(0, value["Value"])  # Insert default value
                value["Entry"] = spinbox  # Save a reference
            else:
                # Add Entry for number input
                number_entry = ttk.Entry(
                    tab_frame,
                    validate="key",
                    validatecommand=(
                        self.root.register(self.validate_entry),
                        "%S",
                    ),
                )
                number_entry.delete(0, "end")  # Clear any existing text
                number_entry.insert(0, value["Value"])  # Insert default value
                number_entry.grid(row=row_index + 1, column=0, pady=(5, 0), sticky="ew")
                value["Entry"] = number_entry  # Save a reference
        else:
            # Add the main Edit control
            edit_control = tk.Entry(tab_frame, width=20)
            edit_control.delete(0, "end")  # Clear any existing text
            edit_control.insert(0, value["Value"])  # Insert default value
            edit_control.grid(
                row=row_index + 1,
                column=0,
                columnspan=2,
                pady=(5, 0),
                sticky="ew",
            )
            value["Entry"] = edit_control  # Save a reference
        row_index += 1
        return value, row_index

    def add_ddlcombo(self, value, tab_frame, row_index, control_options):
        # Check for control options

        # If options are comma-separated, convert to a pipe-separated format
        if "," in control_options and "|" not in control_options:
            control_options = control_options.replace(",", "|")

        # Add the default value if not already present
        if value["Default"] not in control_options:
            if control_options.endswith("|"):
                control_options += value["Default"]
            else:
                control_options += "|" + value["Default"]

        # Ensure no duplicate options and handle default formatting
        control_options = control_options.replace(
            value["Default"], value["Default"] + "|"
        )
        control_options = control_options.replace("||", "|")
        control_options = control_options.rstrip("|")  # Remove trailing pipe

        # Split options into a list
        options_list = control_options.split("|")
        # Create the combobox
        if (
            value.Control == "combobox"
        ):  # for combobox, remove readonly to allow editing
            # combobox: allow editing. Strip readonly if present, then warn the use to use ddl if readonly is desired
            if "readonly" in options_list:  # except if it is explicitly noted
                options_list.remove("readonly")
                self.logger.debug(  # use debugging because this code results in the expected behaviour for this control-type. Debugging will yield the reason
                    f"{self.name}: Option 'readonly' present in {value.Control}'s parameter got ignored. To use a DDL without write-access, use control-type 'ddl'."
                )
            combobox = ttk.Combobox(
                tab_frame,
                values=options_list,
            )
        elif value.Control == "ddl":  # for ddl, force readonly
            if "readonly" not in options_list:
                self.logger.debug(  # use debugging because this code results in the expected behaviour for this control-type. Debugging will yield the reason
                    f"{self.classname}: Option 'readonly' not present in {value.Control}'s parameter. 'readonly' was forcefully applied. To use a DDL with write-access, use control-type 'combobox'."
                )
            combobox = ttk.Combobox(tab_frame, values=options_list, state="readonly")
        # Set the default value in the combobox
        combobox.set(value["Default"])
        combobox.grid(row=row_index + 1, column=0, pady=(5, 0), sticky="ew")

        # Store the reference for later use
        value["Entry"] = combobox  # Save a reference

        row_index += 1  # Increment the row index for the next control
        return value, row_index

    def add_checkbox(self, value, tab_frame, row_index, control_options):
        # Add the text label to the right of the link
        # text_label = tk.Label(tab_frame, text="")
        # text_label.grid(row=row_index, column=0, padx=(10, 0), sticky="w")
        # Logic for creating a checkbox
        if value["Value"].lower() == "true":
            checkbox_var = tk.BooleanVar(value=True)
        elif value["Value"].lower() == "false":
            checkbox_var = tk.BooleanVar(value=False)
        else:
            raise ValueError(f"Invalid value for boolean conversion: {value["Value"]}")
        checkbox = tk.Checkbutton(
            tab_frame, text=value["String"], variable=checkbox_var
        )
        checkbox.grid(row=row_index, column=0, padx=(10, 0), sticky="w")
        value["Entry"] = checkbox_var  # Save reference for retrieving value
        row_index += 1
        return value, row_index

    def add_file(self, value, tab_frame, row_index, modified_parameter):
        # Entry for the file path
        file_entry = ttk.Entry(tab_frame, width=50)
        file_entry.insert(0, value.get("Value", ""))
        file_entry.grid(
            row=row_index + 1,
            column=0,
            columnspan=4,
            # padx=5,
            pady=5,
            sticky="ew",
        )

        # "Select File" button
        select_file_btn = ttk.Button(
            tab_frame,
            text="Select File",
            command=lambda param=modified_parameter: self.choose_file(
                param, file_entry
            ),
        )
        select_file_btn.grid(row=row_index, column=2, padx=5, pady=5, sticky="w")

        # "Open Folder" button
        open_folder_btn = ttk.Button(
            tab_frame,
            text="Open Folder",
            command=lambda param=modified_parameter: self.open_file_folder(
                param, file_entry
            ),
        )
        open_folder_btn.grid(row=row_index, column=3, padx=5, pady=5, sticky="w")

        row_index += 1
        value["Entry"] = file_entry  # Save reference for retrieving value
        return value, row_index

    def add_datepicker(self, value, tab_frame, row_index):
        # Initialize DateEntry control with parsed date if available
        date_entry = DateEntry(
            tab_frame,
            width=12,
            background="darkblue",
            foreground="white",
            borderwidth=2,
            date_pattern="dd.MM.yyyy",
        )
        date_entry.grid(row=row_index + 1, column=0, pady=(5, 0), sticky="w")

        if "Value" in value:
            parsed_date = self.da_dateparse(value["Value"])
            if parsed_date:
                date_entry.set_date(parsed_date)

        # Store the reference to retrieve the selected date later
        value["Entry"] = date_entry
        row_index += 2  # Move down by two rows for next control
        return value, row_index

    def create_gui(self):
        self.tabs.grid(row=0, column=0, sticky="nsew")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Create tabs and controls based on provided arguments
        tab_headers = {}
        for parameter, value in self.arguments.items():
            if value["Control"] in ["meta", "Meta"]:
                continue
            if "Tab3Parent" in value:
                tab_headers[value["Tab3Parent"]] = {"Height": 0}
            else:
                self.arguments[parameter]["Tab3Parent"] = "Other"
                tab_headers[value["Tab3Parent"]] = {"Height": 0}
        tab_headers = {key: tab_headers[key] for key in sorted(tab_headers)}
        HiddenHeaders = {}
        added_headers = {}
        sanitized_header_map = (
            {}
        )  # Dictionary to hold original to sanitized header mappings

        for Header, _ in tab_headers.items():
            HeaderFound = False
            for Parameter, value in self.arguments.items():
                if value["Tab3Parent"] == Header:
                    if value["Control"] not in ["meta", "Meta"]:
                        if Header not in added_headers:
                            # Sanitize the header
                            sanitized_header = Header.replace(
                                "&&", "and"
                            )  # Example of replacing special characters
                            sanitized_header = "".join(
                                e if e.isalnum() else "_" for e in sanitized_header
                            )
                            sanitized_header = sanitized_header.lower()
                            # Store the mapping
                            sanitized_header_map[Header] = sanitized_header

                            # Add the tab with the original name for display
                            self.tabs.add(
                                ttk.Frame(self.tabs, name=sanitized_header.lower()),
                                text=Header,
                            )
                            added_headers[Header] = True
                            HiddenHeaders[Header] = False
                            HeaderFound = True
                        break
                    else:
                        added_headers[Header] = False
                        HiddenHeaders[Header] = True

        a = self.tabs.tabs()
        for Header, _ in tab_headers.items():
            if HiddenHeaders[Header]:
                continue
            row_index = 0
            self.logger.debug(f"Adding to tab {Header}")
            for parameter, value in self.arguments.items():
                if value["Control"] in ["meta", "Meta"]:
                    continue
                if "-" in parameter:
                    parameter = parameter.replace(
                        "-", "___"
                    )  # Replace dashes with three underscores
                modified_parameter = parameter.replace("___", "-")
                if (
                    "String" not in value
                ):  # do not load controls which do not have a descriptor-string
                    continue

                # Check if modified_parameter is not in Value['String']
                if modified_parameter not in value["String"]:
                    value["String"] = f"{modified_parameter}: {value['String']}"

                # Ensure only controls of this tab are added
                if Header == value["Tab3Parent"]:
                    Control = value["Control"]
                else:
                    continue  # this parameter does not belong into this tab

                row_index += 1
                # Add edit and related controls
                b = self.tabs.index(
                    ".!notebook." + sanitized_header_map[Header]
                )  # Use the sanitized header
                c = a[b]
                tab_frame = self.tabs.nametowidget(c)
                control_options = value.get("ctrlOptions", "")
                if Control == "edit":
                    self.add_text(value, tab_frame, row_index)
                    self.add_link(value, tab_frame, row_index)
                    value, row_index = self.add_edit(
                        value, tab_frame, row_index, control_options
                    )
                elif Control == "file":
                    self.add_text(value, tab_frame, row_index)
                    self.add_link(value, tab_frame, row_index)
                    value, row_index = self.add_file(
                        value, tab_frame, row_index, modified_parameter
                    )
                elif (Control == "ddl") or (Control == "combobox"):
                    self.add_text(value, tab_frame, row_index)
                    self.add_link(value, tab_frame, row_index)
                    value, row_index = self.add_ddlcombo(
                        value, tab_frame, row_index, control_options
                    )
                elif Control == "datetime":
                    print("datetime selection control and related controls")
                    self.add_text(value, tab_frame, row_index)
                    self.add_link(value, tab_frame, row_index)
                    value, row_index = self.add_datepicker(value, tab_frame, row_index)
                elif Control == "checkbox":
                    self.add_link(value, tab_frame, row_index)
                    value, row_index = self.add_checkbox(
                        value, tab_frame, row_index, control_options
                    )
                else:
                    raise NotImplementedError(
                        f"Control-type {Control} is not implemented. Control-type found for parameter '{parameter}' of format {self.type} in configuration-file '{self.config_file}'"
                    )
        self.add_footer()

    def add_footer(self):
        # Create a frame for the footer
        footer_frame = tk.Frame(self.root)
        footer_frame.grid(row=1, column=0, sticky="ew", pady=10)

        submit_button = tk.Button(
            footer_frame,
            text="Submit",
            command=self.submit,  # Link to the submit method
            width=15,
        )
        submit_button.pack(side=tk.LEFT, padx=5)

        edit_button = tk.Button(
            footer_frame,
            text="Edit Configuration",
            command=self.open_configuration_file,  # Link to the function that opens the config
            width=20,
        )
        edit_button.pack(side=tk.LEFT, padx=5)

        footer_frame.grid_columnconfigure(0, weight=1)
        footer_frame.grid_columnconfigure(1, weight=1)

    def bind_method_hotkey(self, hotkey, method):
        self.root.bind(hotkey, lambda event: getattr(self, method)())

    def open_configuration_file(self):
        # This function opens the configuration file
        # Replace 'config.ini' with the actual path to your configuration file
        if os.path.exists(self.config_file):
            os.startfile(self.config_file)  # For Windows; adjust if using another OS
        else:
            messagebox.showerror("Error", "Configuration file not found!")

    def choose_file(self, parameter, file_entry):
        # Open a file dialog to select a file
        file_path = filedialog.askopenfilename(
            title="Select a File",
            initialdir=self.arguments[parameter].get("SearchPath", ""),
        )
        if file_path:
            self.arguments[parameter]["Value"] = file_path
            file_entry.delete(0, tk.END)
            file_entry.insert(0, file_path)

    def open_file_folder(self, parameter, file_entry):
        # Open the folder containing the selected file
        file_path = file_entry.get()
        if os.path.isfile(file_path):
            folder_path = os.path.dirname(file_path)
            webbrowser.open(folder_path)
        else:
            self.logger.warning("No valid file selected, or the file does not exist.")
            messagebox.showwarning(
                "Warning", "No valid file selected or file does not exist."
            )

    def submit(self):
        results = {}
        for parameter, value in self.arguments.items():
            if "Entry" in value:
                results[parameter] = self.arguments[parameter].Value = value[
                    "Entry"
                ].get()
            elif "Var" in value:
                results[parameter] = self.arguments[parameter].Value = value[
                    "Var"
                ].get()
            elif "Combo" in value:
                results[parameter] = self.arguments[parameter].Value = value[
                    "Combo"
                ].get()
        # self.results = results
        self.root.destroy()

    def close(self):
        self.root.destroy()

    def validate_entry(self, text):
        return text.isdecimal()

    def validate_spinbox_input(self, input_value):
        # Simple validation to allow only numbers
        return input_value.isdigit() or input_value == ""
