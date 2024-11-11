# command_handlers.py

from obsidianknittrpy.modules.utility import convert_format_args, load_text_file
from obsidianknittrpy.modules.guis import handle_ot_guis, ObsidianKnittrGUI
from obsidianknittrpy.modules.vault_limiter import ObsidianHTML_Limiter
from obsidianknittrpy.modules.ObsidianHTML import ObsidianHTML
from obsidianknittrpy.modules.processing.processing_module_runner import (
    ProcessingPipeline,
)
from obsidianknittrpy.modules.ConfigurationHandler import ConfigurationHandler
import warnings as wn
import os as os


def main(pb, CH):
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
        use_convert=pb["settings"]["obsidian_html"]["verb"] in ["convert", True],
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
    pb, CH = handle_ot_guis(args, pb, CH="")
    main(pb)


def handle_gui(args, pb):
    """Execute the GUI command."""
    # 1. translate arguments
    args = convert_format_args(args)
    # 2. setup config-manager
    CH = ConfigurationHandler(last_run_path=None)
    # setup defaults, load last-run
    CH.apply_defaults()
    CH.load_last_run(
        last_run_path=CH.default_guiconfiguration_location
    )  # must be modified to point to the lastrun-path.
    # load file-history
    CH.load_file_history(file_history_path=CH.default_history_location)
    # retrieve objects for use in later
    settings = CH.get_config("settings")
    # 2. launch main GUI
    main_gui = ObsidianKnittrGUI(
        settings=settings,
        file_history=CH.get_config("file_history"),
        formats=CH.get_formats(CH.get_config("format_definitions")),
    )
    # 3. Save file-history
    main_gui.update_filehistory(main_gui.results["manuscript"]["manuscript_path"])
    CH.file_history = main_gui.file_history
    CH.save_file_history(CH.default_history_location)
    # 4. Merge applied settings into the storage.
    CH.merge_config_for_save(
        {"exec_dir_selection": main_gui.results["execution_directory"]},
        "EXECUTION_DIRECTORIES",
    )
    CH.merge_config_for_save(main_gui.results["obsidian_html"], "OBSIDIAN_HTML")
    CH.merge_config_for_save(
        main_gui.results["general_configuration"], "GENERAL_CONFIGURATION"
    )
    CH.merge_config_for_save(
        main_gui.results["engine_configurations"], "ENGINE_CONFIGURATION"
    )
    # >> manuscript-section is saved in file-history, not here
    # CH.merge_config_for_save(main_gui.results["manuscript"], "manuscript")
    CH.applied_settings["OUTPUT_TYPE"] = main_gui.results["output_type"]
    CH.save_last_run(CH.default_guiconfiguration_location)
    # 3. when main GUI submits, parse the selected formats and launch the OT-guis
    # for result in main_gui.results["general_configuration"].items():
    #     pb.
    pb["settings"] = main_gui.results
    pb["objects"]["sel"] = main_gui.results["output_type"]
    pb["manuscript"] = main_gui.results["manuscript"]
    pb = handle_ot_guis(
        args=args, pb=pb, format_definitions=CH.get_config("format_definitions")
    )
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
    main(pb, CH)


# You can also include other handler functions if needed.


def handle_version():
    """Handle the 'version' command."""
    print(f"Versioning not set up yet. Alpha. 0.0.1.9000")
    exit(0)
