import re
import os
from math import floor


class OT:
    # __New(Format:="",ConfigFile:="",DDL_ParamDelimiter:="-<>-",SkipGUI:=FALSE,StepsizedGuiShow:=FALSE) {
    def __init__(
        self,
        config_file="",
        format="",
        DDL_ParamDelimiter="-<>-",
        skip_gui=False,
        stepsized_gui_show=False,
    ):
        self.config_file = config_file
        self.type = format
        self.DDL_ParamDelimiter = DDL_ParamDelimiter
        self.skip_gui = skip_gui
        self.stepsized_gui_show = stepsized_gui_show

        self.classname = "ot (" + format + ")"
        # this.GUITitle="Define output format - "
        self.version = "0.1.a"
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
            with open(self.config_file, "r") as f:
                text = f.read()

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
                        if (
                            current_param is None
                        ):  # Initiate parameter-Object if current_param is not set
                            current_param = key
                            self.arguments[key] = {}
                            self.arguments[key]["Control"] = value
                        else:
                            self.arguments[current_param][key] = value
            # print(self.get_error(0))
        except FileNotFoundError:
            print(f"Configuration file '{self.config_file}' not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def assume_defaults(self):
        for parameter, value in self.arguments.items():
            if value["Control"] == "meta" or value["Control"] == "Meta":
                setattr(self, parameter, value["Value"])
                continue
            # Remove quotation marks from paths and strings
            if "SearchPath" in value:
                value["SearchPath"] = value["SearchPath"].replace('"', "")
            if not (value.get("String", "") == ""):
                value["String"] = value["String"].replace('"', "")

            # Remove quotation marks from default values if type is string
            if value.get("Type") == "String":
                value["Default"] = value["Default"].replace('"', "")

            # Set Value to Default if Value is empty
            if value.get("Value", "") == "":
                if value.get("Control") == "File":
                    # Check if the file exists in the SearchPath with Default as filename
                    file_path = os.path.join(value["SearchPath"], value["Default"])
                    if not os.path.exists(file_path):
                        print(
                            f"output_type: {self.type}\nThe default File\n'{file_path}'\ndoes not exist. No default set."
                        )
                    else:
                        value["Value"] = file_path
                else:
                    value["Value"] = value["Default"]

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
                    if value["Value"] not in ["TRUE", "FALSE"]:
                        print(f"Warning: Cannot convert {value['Value']} to a number.")

            # Convert boolean to "TRUE" or "FALSE"
            if value_type == "boolean":
                value["Value"] = "TRUE" if value["Value"] else "FALSE"

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
