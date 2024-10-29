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

                # Check if the line defines a rendering package
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
                        ):  # Initiate Parameter-Object if current_param is not set
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
        print("TODO: implement AssumeDefaults")

    def adjust(self):
        print("TODO: implement adjust")

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
