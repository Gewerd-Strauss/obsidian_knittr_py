# command_handlers.py
from obsidianknittrpy import __version__
from obsidianknittrpy.modules.utility import (
    convert_format_args,
    load_text_file,
    get_text_file_path,
    pre_configure_obsidianhtml_fork,
    open_folder,
)
from obsidianknittrpy.modules.guis.guis import handle_ot_guis, ObsidianKnittrGUI
from obsidianknittrpy.modules.obsidian_html.ObsidianHTML_Limiter import (
    ObsidianHTML_Limiter,
)
from obsidianknittrpy.modules.core.ResourceLogger import ResourceLogger
from obsidianknittrpy.modules.core.ExternalHandler import ExternalHandler
from obsidianknittrpy.modules.obsidian_html.ObsidianHTML import ObsidianHTML
from obsidianknittrpy.modules.processing.processing_module_runner import (
    ProcessingPipeline,
)
from obsidianknittrpy.modules.rendering.renderer_v2 import RenderManager
from obsidianknittrpy.modules.rendering.renderer import (
    RenderingPipeline,
)
from obsidianknittrpy.modules.rendering.file_strings import (
    prepare_file_strings,
    prepare_file_suffixes,
)
import warnings as wn
import os as os
import sys as sys
import logging as logging
import yaml as yaml


def main(pb, CH, loglevel=None, export=False, import_=False):
    # Level = 0 > manuscript_dir > check
    # Level = -1 > true vault-root > check
    # Level > 0 = manuscript_dir - level
    # obsidian_limiter.add_limiter() # < these must be called before and after oHTML is processed.
    # obsidian_limiter.remove_limiter() # < these must be called before and after oHTML is processed.
    RL = ResourceLogger(log_directory=CH.get_key("DIRECTORIES_PATHS", "work_dir"))
    if CH.get_key("OBSIDIAN_HTML", "limit_scope"):
        obsidian_limiter = ObsidianHTML_Limiter(
            manuscript_path=os.path.normpath(
                CH.get_key("MANUSCRIPT", "manuscript_path")
            ),
            auto_submit=CH.get_key("GENERAL_CONFIGURATION", "full_submit"),
            level=CH.get_key("OBSIDIAN_HTML_LIMITER", "level"),
            loglevel=loglevel,
        )
        obsidian_limiter.add_limiter()
        if obsidian_limiter.selected_limiter_is_vaultroot:
            RL.log(
                action="used vault",
                module=f"{obsidian_limiter.__module__}.add_limiter",
                resource=obsidian_limiter.selected_limiter_directory,
            )
        elif not obsidian_limiter.selected_limiter_preexisted:
            RL.log(
                action="created",
                module=f"{obsidian_limiter.__module__}.add_limiter",
                resource=obsidian_limiter.selected_limiter_directory,
            )
        else:
            RL.log(
                action="used pre-existing non-root",
                module=f"{obsidian_limiter.__module__}.add_limiter",
                resource=obsidian_limiter.selected_limiter_directory,
            )
            logging.critical(
                f"{obsidian_limiter.__module__} used the directory '{obsidian_limiter.selected_limiter_directory}', but it was flagged as both pre-existing and non-root. This should be impossible."
            )
        pb["objects"]["obsidian_limiter"] = obsidian_limiter
        CH.applied_settings["OBSIDIAN_HTML_LIMITER"]["level"] = obsidian_limiter.level
        CH.applied_settings["OBSIDIAN_HTML_LIMITER"][
            "selected_limiter_preexisted"
        ] = obsidian_limiter.selected_limiter_preexisted
        CH.applied_settings["OBSIDIAN_HTML_LIMITER"][
            "selected_limiter_is_vaultroot"
        ] = obsidian_limiter.selected_limiter_is_vaultroot
    if not export:
        # make sure state-changes only occur when neither exporting nor importing
        if not import_:
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
        obsidian_html.setup_config(RL)

        obsidian_html.run()
        path_ = get_text_file_path(
            obsidian_html.output["output_path"],
        )
        RL.log(
            action="created",
            module=f"{obsidian_html.__module__}.run",
            resource=obsidian_html.output["output_path"],
        )
    if CH.get_key("OBSIDIAN_HTML", "limit_scope"):
        pb["objects"]["obsidian_limiter"].remove_limiter()
        if pb["objects"]["obsidian_limiter"].removed_selected_limiter_directory_success:
            RL.log(
                action="removed",
                module=f"{pb["objects"]["obsidian_limiter"].__module__}.remove_limiter",
                resource=obsidian_limiter.selected_limiter_directory,
            )
        else:
            RL.log(
                action="kept",
                module=f"{pb["objects"]["obsidian_limiter"].__module__}.remove_limiter",
                resource=obsidian_limiter.selected_limiter_directory,
            )
    if export:
        CH.export_config()
    elif not export:
        arguments = {}
        arguments.update(CH.get_key("GENERAL_CONFIGURATION"))
        arguments.update(CH.get_key("OBSIDIAN_HTML"))
        arguments.update(CH.get_key("ENGINE_CONFIGURATION"))
        pipeline = ProcessingPipeline(
            config_file=CH.applied_pipeline,
            arguments=arguments,
            debug=True,
            log_directory=os.path.normpath(
                os.path.join(CH.get_key("DIRECTORIES_PATHS", "output_dir"), "mod")
            ),
            RL=RL,
        )
        processed_string = pipeline.run(load_text_file(path_))
        # RL.log(action="read",module=)
        file_strings = ""
        if CH.get_key("EXECUTION_DIRECTORIES", "exec_dir_selection") == 1:
            # OHTML-output-directory
            working_directory = os.path.dirname(os.path.realpath(path_))
        elif CH.get_key("EXECUTION_DIRECTORIES", "exec_dir_selection") == 2:
            # Location of source-note in vault
            working_directory = os.path.dirname(
                os.path.realpath(CH.get_key("MANUSCRIPT", "manuscript_path"))
            )
        elif False:
            pass  # figure out how to set the rendering directory dynamically.

        # Call function
        file_strings = prepare_file_strings(
            file_string=processed_string,
            output_types=CH.get_key("OUTPUT_TYPE"),
            output_format_values=CH.get_key("OUTPUT_FORMAT_VALUES"),
        )
        file_suffixes = prepare_file_suffixes(pb["objects"]["output_formats"])

        logger__ = logging.getLogger("main")
        if CH.get_key("GENERAL_CONFIGURATION", "render_to_outputs"):
            # if logger__.getEffectiveLevel() <= logging.DEBUG:
            mod_directory = os.path.normpath(
                os.path.join(
                    os.path.dirname(
                        obsidian_html.output["output_path"],
                    ),
                    "mod",
                )
            )
            renderManager = RenderManager(
                file_strings=file_strings,
                custom_file_names=None,
                debug=False,
                file_suffixes=file_suffixes,
                input_name=None,
                log_level=loglevel,
                mod_directory=mod_directory,
                output_directory=CH.get_key("DIRECTORIES_PATHS", "work_dir"),
                use_parallel=CH.get_key(
                    "GENERAL_CONFIGURATION", "parallelise_rendering"
                ),
                parameters=CH.get_key("OUTPUT_FORMAT_VALUES"),
                working_directory=working_directory,
            )
            renderManager.execute()
            # and store the output directory in a config-file to be openable afterwards.
            OH = ExternalHandler(
                interface_dir=CH.get_key("DIRECTORIES_PATHS", "output_dir")
            )
            OH.set(
                "output-data",
                "directory",
                renderManager.output_data["rendered_output_directory"],
            )
            RL.log(
                action="created",
                module=f"{OH.__module__}.set",
                resource=OH._get_filepath("output-data"),
            )


def handle_openlist(args, pb, CH):
    """Open the directory containing the last-rendered documents"""
    OH = ExternalHandler(interface_dir=CH.get_key("DIRECTORIES_PATHS", "output_dir"))
    p = OH._get_filepath("output-data")
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8") as f:
            yml_data = yaml.safe_load(f)
        print(f"and now, we can open '{yml_data["directory"]}'")
        if os.path.exists(yml_data["directory"]):
            open_folder(yml_data["directory"])
    else:
        raise FileNotFoundError(
            f"Information about the previous rendering were already deleted.\nReason: The working-directory has been cleaned after the last time this utility rendered any documents.\n- Did you use the verb 'export'?\n- Did you use the verb 'gui' (without rendering to output-targets)?"
        )


def handle_import(args, pb, CH):
    """Import config-file generated by export."""

    # CH.load_last_run(
    #     last_run_path=CH.default_guiconfiguration_location
    # )  # must be modified to point to the lastrun-path.
    RL = ResourceLogger(log_directory=CH.get_key("DIRECTORIES_PATHS", "work_dir"))
    RL.log(
        action="loaded",
        module=f"{CH.__module__}.handle_import",
        resource=CH.default_guiconfiguration_location,
    )
    CH.merge_applied_settings(args["input"])

    RL.log(
        action="loaded",
        module=f"{CH.__module__}.handle_import",
        resource=args["input"],
    )
    CH.applied_settings["GENERAL_CONFIGURATION"]["full_submit"] = True

    pb, CH = handle_ot_guis(
        args=args,
        pb=pb,
        CH=CH,
        same_manuscript_chosen=True,
        format_definitions=CH.get_config("format_definitions"),
    )

    main(pb, CH, args["loglevel"], export=False, import_=True)


def handle_gui(args, pb, CH, EH, export=False, import_=False):
    """Execute the GUI command."""

    # setup defaults, load last-run
    CH.load_last_run(
        last_run_path=CH.default_guiconfiguration_location
    )  # must be modified to point to the lastrun-path.
    RL = ResourceLogger(log_directory=CH.get_key("DIRECTORIES_PATHS", "work_dir"))
    RL.log(
        action="loaded",
        module=f"{CH.__module__}.handle_gui",
        resource=CH.default_guiconfiguration_location,
    )
    CH = pre_configure_obsidianhtml_fork(
        CH, EH, args
    )  # must be repeated as such to overwrite changes made by loading the last-run config in its entirety will overwrite previously-made changes to the state of the CH.
    RL.log(
        action="modifies",
        module=f"{CH.__module__}.handle_gui",
        resource=CH.default_guiconfiguration_location,
    )
    # load file-history
    CH.load_file_history(file_history_path=CH.default_history_location)
    RL.log(
        action="loaded",
        module=f"{CH.__module__}.handle_gui",
        resource=CH.default_history_location,
    )
    # retrieve objects for use in later
    settings = CH.get_config("settings")
    # 2. launch main GUI
    for module in CH.applied_pipeline["pipeline"]:
        logging.debug(str(module))
    main_gui = ObsidianKnittrGUI(
        pipeline=CH.applied_pipeline["pipeline"],
        settings=settings,
        file_history=CH.get_config("file_history"),
        formats=CH.get_formats(CH.get_config("format_definitions")),
        loglevel=args["loglevel"],
        command=args["command"],
    )
    if main_gui.closed:
        sys.exit(0)
    # 3. Save file-history
    main_gui.update_filehistory(main_gui.results["manuscript"]["manuscript_path"])
    CH.file_history = main_gui.file_history
    if not export and not import_:
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
        # 2.1 If it is, load the lastrun-selections **over the** commandline-provided and the default selections.
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

        if same_manuscript_chosen or export:
            CH.applied_settings["OUTPUT_FORMAT_VALUES"][format] = {}
        for arg, value in ot.arguments.items():
            if same_manuscript_chosen or export:
                CH.applied_settings["OUTPUT_FORMAT_VALUES"][format][arg] = ot.arguments[
                    arg
                ]["Value"]
            logging.debug(
                f"{arg}: Value: {value["Value"]}, Default: {value["Default"]}, Type: {value.Type}"
            )

    main(pb, CH, args["loglevel"], export=export)


def handle_export(args, pb, CH, EH):
    """
    Executes the 'export'-command.

    This is just a wrapper around 'handle_gui',
    but without executing any actual 'processing' itself
    TODO: verify that this is state-exchangeable with 'handle_gui'.
    """
    handle_gui(args, pb, CH, EH, True, False)


def handle_version():
    """Handle the 'version' command."""
    print(f"Current version: {__version__}")
    exit(0)
