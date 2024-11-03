# command_handlers.py

from obsidianknittrpy.modules.DynamicArguments import OT
from obsidianknittrpy.modules.utility import convert_format_args

config_file = "D:/Dokumente neu/Repositories/python/obsidian_knittr_py/assets/DynamicArguments.ini"

def main(pb):
    wn.warn("main processing function is not implemented yet.")
    pass

def handle_convert(args):
    """Execute the convert command."""
    print(f"Converting {args.input} to formats: {args.format}")
    # Implement conversion logic here based on arguments


def handle_gui(args, pb):
    """Execute the GUI command."""
    # 1. translate arguments
    args = convert_format_args(args)
    # 2. launch main GUI
    main_gui = ObsidianKnittrGUI()
    # 3. when main GUI submits, parse the selected formats and launch the OT-guis
    # for result in main_gui.results["general_configuration"].items():
    #     pb.
    pb["settings"] = main_gui.results
    pb["objects"]["sel"] = main_gui.results["output_type"]
    pb["manuscript"] = main_gui.results["manuscript"]
    pb = handle_ot_guis(args, pb)
    for format, ot in pb["objects"]["output_formats"].items():
        # Here, format is the key (e.g., "quarto::docx")
        # and ot is the instance of the OT class
        # print(f"Format: {format}, Output Type: {ot.type}, Arguments: {ot.arguments}")
        for arg, value in ot.arguments.items():
            a = value["Value"]
            b = ot.arguments["date"]["Value"]
            c = ot.arguments[arg].Default
            D = ot.arguments[arg].DD
            print(
                f"{arg}: Value: {value["Value"]}, Default: {value["Default"]}, Type: {value.Type}"
            )
    main(pb)


# You can also include other handler functions if needed.


def handle_version():
    """Handle the 'version' command."""
    print(f"Versioning not set up yet. Alpha. 0.0.1.9000")
    exit(0)
