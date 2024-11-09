# command_handlers.py

from obsidianknittrpy.modules.utility import convert_format_args, load_text_file
from obsidianknittrpy.modules.guis import handle_ot_guis, ObsidianKnittrGUI
from obsidianknittrpy.modules.vault_limiter import ObsidianHTML_Limiter
from obsidianknittrpy.modules.ObsidianHTML import ObsidianHTML
from obsidianknittrpy.modules.processing.processing_module_runner import (
    ProcessingPipeline,
)
import warnings as wn
import os as os


def main(pb):
    wn.warn("main processing function is not implemented yet.")
    # Level = 0 > manuscript_dir > check
    # Level = -1 > true vault-root > check
    # Level > 0 = manuscript_dir - level
    # obsidian_limiter.add_limiter() # < these must be called before and after oHTML is processed.
    # obsidian_limiter.remove_limiter() # < these must be called before and after oHTML is processed.
    if pb["settings"]["obsidian_html"]["limit_scope"]:
        obsidian_limiter = ObsidianHTML_Limiter(
            manuscript_path=os.path.normpath(pb["manuscript"]["manuscript_path"]),
            auto_submit=pb["settings"]["general_configuration"]["full_submit"],
        )
        pb["objects"]["obsidian_limiter"] = obsidian_limiter
        pb["objects"]["obsidian_limiter"].add_limiter()

    # Example usage:
    obsidian_html = ObsidianHTML(
        manuscript_path=pb["manuscript"]["manuscript_path"],
        config_path=r"assets\temp_obsidianhtml_config.yml",
        use_convert=pb["settings"]["obsidian_html"]["verb"] == "convert",
        use_own_fork=pb["settings"]["obsidian_html"]["use_custom_fork"],
        verbose=pb["settings"]["obsidian_html"]["verbose_flag"],
        own_ohtml_fork_dir=r"D:\Dokumente neu\Repositories\python\obsidian-html",
        work_dir=os.path.normpath(
            os.path.join(
                os.path.expanduser("~"),
                "Desktop",
                "TempTemporal",
                "obsidian-html-output",
            )
        ),
        # work_dir=r"D:\Dokumente neu\Repositories\python\obsidian-html",
        output_dir=os.path.normpath(
            os.path.join(
                os.path.expanduser("~"),
                "Desktop",
                "TempTemporal",
                "obsidian-html-output",
            )
        ),
    )
    obsidian_html.run()
    if pb["settings"]["obsidian_html"]["limit_scope"]:
        pb["objects"]["obsidian_limiter"].remove_limiter()
    arguments = pb["settings"]["general_configuration"]
    pipeline = ProcessingPipeline(
        config_file="assets/pipeline.yml", arguments=arguments, debug=True
    )
    processed_string = pipeline.run(
        load_text_file(
            obsidian_html.output["output_path"],
        )
    )
    print(processed_string)
    pass


def handle_convert(args, pb):
    """Execute the convert command."""
    print(f"Converting {args.input} to formats: {args.format}")
    # Implement conversion logic here based on arguments
    args = convert_format_args(args)
    # TOOD: implement processing from GUI-classes that _is_ required, see 'handle_ot_gui_passthrough()'
    pb = handle_ot_guis(args, pb)
    main(pb)


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
