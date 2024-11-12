# command_handlers.py

from obsidianknittrpy.modules.utility import convert_format_args, load_text_file
from obsidianknittrpy.modules.guis import handle_ot_guis, ObsidianKnittrGUI
from obsidianknittrpy.modules.vault_limiter import ObsidianHTML_Limiter
from obsidianknittrpy.modules.ObsidianHTML import ObsidianHTML
from obsidianknittrpy.modules.processing.processing_module_runner import (
    ProcessingPipeline,
)
from obsidianknittrpy.modules.rendering.renderer import (
    RenderingPipeline,
    prepare_file_strings,
)
from obsidianknittrpy.modules.ConfigurationHandler import ConfigurationHandler
import warnings as wn
import os as os
import sys as sys


def main(pb, CH):
    wn.warn("main processing function is not implemented yet.")
    # Level = 0 > manuscript_dir > check
    # Level = -1 > true vault-root > check
    # Level > 0 = manuscript_dir - level
    # obsidian_limiter.add_limiter() # < these must be called before and after oHTML is processed.
    # obsidian_limiter.remove_limiter() # < these must be called before and after oHTML is processed.
    if CH.get_key("OBSIDIAN_HTML", "limit_scope"):
        obsidian_limiter = ObsidianHTML_Limiter(
            manuscript_path=os.path.normpath(
                CH.get_key("MANUSCRIPT", "manuscript_path")
            ),
            auto_submit=CH.get_key("GENERAL_CONFIGURATION", "full_submit"),
            level=CH.get_key("OBSIDIAN_HTML_LIMITER", "level"),
        )
        obsidian_limiter.add_limiter()
        pb["objects"]["obsidian_limiter"] = obsidian_limiter
        CH.applied_settings["OBSIDIAN_HTML_LIMITER"]["level"] = obsidian_limiter.level
        CH.applied_settings["OBSIDIAN_HTML_LIMITER"][
            "selected_limiter_preexisted"
        ] = obsidian_limiter.selected_limiter_preexisted
        CH.applied_settings["OBSIDIAN_HTML_LIMITER"][
            "selected_limiter_is_vaultroot"
        ] = obsidian_limiter.selected_limiter_is_vaultroot
    CH.save_last_run(CH.default_guiconfiguration_location)
    obsidian_html = ObsidianHTML(
        manuscript_path=CH.get_key("MANUSCRIPT", "manuscript_path"),
        config_path=CH.default_obsidianhtmlconfiguration_location,
        use_convert=CH.get_key("OBSIDIAN_HTML", "verb") in ["convert", True],
        use_own_fork=CH.get_key("OBSIDIAN_HTML", "use_custom_fork"),
        verbose=CH.get_key("OBSIDIAN_HTML", "verbose_flag"),
        own_ohtml_fork_dir=CH.get_key("DIRECTORIES_PATHS", "own_ohtml_fork_dir"),
        work_dir=CH.get_key("DIRECTORIES_PATHS", "work_dir"),
        # work_dir=r"D:\Dokumente neu\Repositories\python\obsidian-html",
        output_dir=CH.get_key("DIRECTORIES_PATHS", "output_dir"),
    )
    obsidian_html.run()
    if CH.get_key("OBSIDIAN_HTML", "limit_scope"):
        pb["objects"]["obsidian_limiter"].remove_limiter()
    arguments = CH.get_key("GENERAL_CONFIGURATION")
    pipeline = ProcessingPipeline(
        config_file=CH.applied_pipeline, arguments=arguments, debug=True
    )
    processed_string = pipeline.run(
        load_text_file(
            obsidian_html.output["output_path"],
        )
    )
    print(processed_string)
    file_strings = ""
    working_directory = ""

    # Call function
    file_strings = prepare_file_strings(
        file_string=processed_string,
        output_types=CH.get_key("OUTPUT_TYPE"),
        output_format_values=CH.get_key("OUTPUT_FORMAT_VALUES"),
    )
    renderer = RenderingPipeline(
        custom_file_names=None,
        debug=False,
        file_strings=file_strings,
        output_directory=CH.get_key("DIRECTORIES_PATHS", "work_dir"),
    )
    renderer.render(
        parameters=CH.get_key("OUTPUT_FORMAT_VALUES"),
        working_directory=working_directory,
    )
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
    CH = ConfigurationHandler(last_run_path=None, is_gui=True)
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
    if main_gui.closed:
        sys.exit(0)
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
    # 3. when main GUI submits, parse the selected formats and launch the OT-guis
    # for result in main_gui.results["general_configuration"].items():
    #     pb.
    same_manuscript_chosen = (
        CH.applied_settings["MANUSCRIPT"] == main_gui.results["manuscript"]
    )
    CH.applied_settings["MANUSCRIPT"] = main_gui.results["manuscript"]
    # CH.applied_settings[]
    pb, CH = handle_ot_guis(
        args=args,
        pb=pb,
        CH=CH,
        same_manuscript_chosen=same_manuscript_chosen,
        format_definitions=CH.get_config("format_definitions"),
    )
    for format, ot in pb["objects"]["output_formats"].items():
        # Here, format is the key (e.g., "quarto::docx")
        # and ot is the instance of the OT class
        # print(f"Format: {format}, Output Type: {ot.type}, Arguments: {ot.arguments}")
        # If same manuscript was chosen again, load the config 1:1, but with the modifications made during GUI.
        # So, the rule here is:
        # 0. Load the default configuration
        # 1. Merge commandline-provided selections into it
        # 2. Determine if this manuscript is the same as the past manuscript
        # 2.1 If it is, load the lastrun-selections over the commandline-provided and the default selections.
        # 2.2 If it is not, continue
        #
        # Or maybe we should apply the commandline-changes above the lastrun-changes; so that we can
        # apply huge standards by lastrun, and then when calling the GUI via the commandline selective overpower the lastrun?
        #
        #
        #
        ## CLI-ONLY ##
        # In case of the CLI-path, the configuration merged shall require to be fully-declared in the provided config-file.
        # This means that the CLI always executes default parameters, unless the parameter has been added in a provided config-file.
        # And then, have console-provided parameters ovewrite the values provided via the provided config-file.
        #
        #
        #
        # If we select the latter solution, the logic-flow is identical for both CLI and GUI modes; meaning I could simplify this significantly.

        if same_manuscript_chosen:
            CH.applied_settings["OUTPUT_FORMAT_VALUES"][format] = {}
        for arg, value in ot.arguments.items():
            if same_manuscript_chosen:
                CH.applied_settings["OUTPUT_FORMAT_VALUES"][format][arg] = ot.arguments[
                    arg
                ]["Value"]
            print(
                f"{arg}: Value: {value["Value"]}, Default: {value["Default"]}, Type: {value.Type}"
            )

    main(pb, CH)


# You can also include other handler functions if needed.


def handle_version():
    """Handle the 'version' command."""
    print(f"Versioning not set up yet. Alpha. 0.0.1.9000")
    exit(0)
