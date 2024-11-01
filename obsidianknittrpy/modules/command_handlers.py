# command_handlers.py

from obsidianknittrpy.modules.DynamicArguments import OT
from obsidianknittrpy.modules.utility import convert_format_args

config_file = "D:/Dokumente neu/Repositories/python/obsidian_knittr_py/assets/DynamicArguments.ini"


def handle_convert(args):
    """Execute the convert command."""
    print(f"Converting {args.input} to formats: {args.format}")
    # Implement conversion logic here based on arguments


def handle_gui(args):
    """Execute the GUI command."""
    args = convert_format_args(args)
    print(f"Launching GUI in {args["theme"]} theme")
    # Implement GUI launch logic here
    # args = {"quarto::pdf.toc": "false"}
    sel = ["quarto::pdf", "quarto::docx", "quarto::html"]
    sel = ["quarto::docx", "quarto::pdf", "quarto::html"]
    sel = ["quarto::docx"]
    sel = ["quarto::html"]
    sel = ["quarto::pdf"]
    sel = ["quarto::html", "quarto::pdf", "quarto::docx"]
    bAutoSubmitOTGUI = False
    x = 1645
    y = 475
    output_formats = {}
    ShowGui = 1
    for format in sel:
        ot = OT(
            config_file=config_file,
            format=format,
            DDL_ParamDelimiter="-<>-",
            skip_gui=False,
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
            setattr(ot, "SkipGUI", bAutoSubmitOTGUI)  # Set the attribute SkipGUI
            ot.generate_gui(
                x, y, True, "ParamsGUI:", 1, 1, 674, ShowGui
            )  # Call GenerateGUI method
        ot.assemble_format_string()  # Call AssembleFormatString method
        output_formats[format] = (
            ot  # Store the instance in output_formats with format as key
        )
        print(ot.assembled_format_string)
    # print(output_formats["quarto::docx"].assembled_format_string)
    # print(output_formats["quarto::pdf"].assembled_format_string)
    # print(output_formats["quarto::html"].assembled_format_string)


# You can also include other handler functions if needed.


def handle_version():
    """Handle the 'version' command."""
    print(f"Versioning not set up yet. Alpha. 0.0.1.9000")
    exit(0)
