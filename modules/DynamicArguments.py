import tkinter as tk
from tkinter import messagebox
import re
import os


class OT:
    def __init__(
        self,
        format="",
        config_file="",
        ddl_param_delimiter="-<>-",
        skip_gui=False,
        stepsized_gui_show=False,
    ):
        self.type = format
        self.class_name = f"{format} )"
        self.ddl_param_delimiter = ddl_param_delimiter
        self.skip_gui = skip_gui
        self.stepsized_gui_show = stepsized_gui_show

        if os.path.exists(config_file):
            self.config_file = config_file
        else:
            self.error = self.get_error(-1)
            messagebox.showerror(f"{self.class_name} > Initialization", self.error)
            raise FileNotFoundError(f"Configuration file '{config_file}' not found.")

        self.load_config()

    def load_config(self):
        with open(self.config_file, "r") as f:
            text = f.read()

        # Process the configuration file content
        lines = text.split(self.type + "\n")[1].split("\n\n")[0].strip().split("\n")

        if not lines:
            self.error = self.get_error(2)
            messagebox.showerror(f"{self.class_name} > Load Config", self.error)
            return

        self.arguments = {}

        for line in lines:
            line = line.strip()
            if line.startswith(";") or not line:
                continue

            match = re.match(r"(?P<Key>[-\w]+:)(?P<Val>[^|]+)", line)
            if match:
                match_key = match.group("Key")[:-1]  # Remove the colon
                match_val = match.group("Val").strip()
                self.arguments[match_key] = match_val

        self.assume_defaults()
        self.adjust()

    def get_error(self, error_id):
        errors = {
            -1: "Provided Configfile does not exist:\n\nExiting Script",
            0: "GUI got cancelled\n\nReturning to General Selection",
            +2: "Format not defined.\nCheck your configfile.\n\nReturning default 'outputformat()'",
        }
        return errors.get(error_id, "Undefined error")

    def assume_defaults(self):
        # Placeholder for default values; implement as needed
        pass

    def adjust(self):
        # Placeholder for adjustments; implement as needed
        pass


class App:
    def __init__(self, master, auto_submit=False):
        self.master = master
        self.auto_submit = auto_submit
        self.result = None

        self.create_widgets()

        if self.auto_submit:
            master.after(
                100, self.submit
            )  # Delay to allow GUI to render before submission

    def create_widgets(self):
        self.label = tk.Label(self.master, text="Enter format:")
        self.label.pack()

        self.entry = tk.Entry(self.master)
        self.entry.pack()

        self.submit_button = tk.Button(self.master, text="Submit", command=self.submit)
        self.submit_button.pack()

    def submit(self):
        format_value = self.entry.get()
        self.result = OT(
            format=format_value, config_file="path/to/config.ini"
        )  # Provide your config file path

        # Process the result as needed
        print(f"Submitted format: {self.result.type}")

        # Close the window after submission
        self.master.destroy()


def create_gui(auto_submit=False):
    root = tk.Tk()
    app = App(root, auto_submit)
    root.mainloop()
    return app.result


# Example usage
if __name__ == "__main__":
    try:
        # For manual submission
        ot = OT(
            format="quarto::html",
            config_file=r"D:\Dokumente neu\Repositories\R\ObsidianKnittr_py\DynamicArguments.ini",
            ddl_param_delimiter="-<>-",
        )

    except Exception as e:
        print(e)
