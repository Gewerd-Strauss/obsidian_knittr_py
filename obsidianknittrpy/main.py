# main.py
import argparse
import os
import sys
import shutil
from obsidianknittrpy.modules.commandline import (
    common_arguments,
    parser_add_disablers,
    gui_parser_setup,
    import_parser_setup,
    set_parser_setup,
    unset_parser_setup,
    list_parser_setup,
    openlist_parser_setup,
    version_parser_setup,
)
from obsidianknittrpy.modules.command_handlers import (
    handle_gui,
    handle_version,
    handle_export,
    handle_import,
    handle_openlist,
)
from obsidianknittrpy.modules.utility import (
    init_picknick_basket,
    convert_format_args,
    pre_configure_obsidianhtml_fork,
)
from obsidianknittrpy.modules.core.ResourceLogger import ResourceLogger
from obsidianknittrpy.modules.core.ConfigurationHandler import ConfigurationHandler
from obsidianknittrpy.modules.core.ExternalHandler import ExternalHandler
import logging


def main():
    RL = ResourceLogger()
    parser = argparse.ArgumentParser(
        description="Utility supporting 'convert' and 'gui' commands.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- 'gui' command setup ---
    gui_parser = subparsers.add_parser(
        "gui", help="Launch GUI mode.", formatter_class=argparse.RawTextHelpFormatter
    )
    common_arguments(gui_parser)  # Reuse shared arguments for 'gui'
    gui_parser_setup(gui_parser)
    # --- 'version' command setup ---
    version_parser = subparsers.add_parser("version", help="Get the version.")
    version_parser = version_parser_setup(version_parser)
    # --- 'export' command setup ---
    export_parser = subparsers.add_parser(
        "export", help="Using the GUI, create a configuration to execute via 'import'."
    )
    common_arguments(export_parser)
    # --- 'import' command setup ---
    import_parser = subparsers.add_parser(
        "import", help="import a previously exported configuration."
    )
    import_parser = import_parser_setup(import_parser)

    # --- 'extension' command setup ---
    tools_parser = subparsers.add_parser("tools", help="Manage tool configurations.")
    tools_subparsers = tools_parser.add_subparsers(dest="action", required=True)

    # 'set' subcommand
    set_parser = tools_subparsers.add_parser("set", help="Set a tool path.")
    set_parser = set_parser_setup(set_parser)

    # 'unset' subcommand
    unset_parser = tools_subparsers.add_parser("unset", help="Unset a tool path.")
    unset_parser = unset_parser_setup(unset_parser)

    # 'list' subcommand
    list_parser = tools_subparsers.add_parser(
        "list", help="List all tool configurations."
    )
    list_parser = list_parser_setup(list_parser)

    # 'openlist' subcommand
    openlist_parser = subparsers.add_parser(
        "open", help="Trigger the open action. must be elaborated upon"
    )
    openlist_parser = openlist_parser_setup(openlist_parser)
    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
    elif args.command == "version":
        handle_version(args)
    elif args.command == "tools":
        # Command handling
        # 1. translate arguments
        args = convert_format_args(args)
        logging.basicConfig(level=args["loglevel"])
        pb = init_picknick_basket()
        # 2. setup config-manager
        RL.log("main", "inits", "default config")
        CH = ConfigurationHandler(
            last_run_path=None, loglevel=args["loglevel"], is_gui=True
        )
        CH.apply_defaults()
        # 3. setup externalHandler
        EH = ExternalHandler(
            interface_dir=CH.get_key("DIRECTORIES_PATHS", "interface_dir"),
            loglevel=args["loglevel"],
        )
        if args["action"] == "set":
            EH.set(args["file"], args["key"], args["value"])
        elif args["action"] == "unset":
            EH.unset(args["file"], args["key"])
        elif args["action"] == "list":
            EH.list(file=args["file"])
    else:
        # Command handling
        # 1. translate arguments
        args = convert_format_args(args)
        logging.basicConfig(level=args["loglevel"])
        pb = init_picknick_basket()
        # 2. setup config-manager
        RL.log("main", "inits", "default config")
        CH = ConfigurationHandler(
            last_run_path=None, loglevel=args["loglevel"], is_gui=True
        )
        CH.apply_defaults()
        EH = ExternalHandler(
            interface_dir=CH.get_key("DIRECTORIES_PATHS", "interface_dir"),
            loglevel=args["loglevel"],
        )
        if args["command"] != "open":

            RL.log("main", "sets", "own_ohtml_fork_dir")
            CH = pre_configure_obsidianhtml_fork(
                CH, EH, args
            )  # this must be done here to make sure that `load_`

            if args["custom_pipeline"] is not None:
                CH.load_custom_pipeline(args["custom_pipeline"])
            if args["custom_format_definitions"]:
                CH.load_custom_format_definitions(args["custom_format_definitions"])
            # 3. clear out work dir
            if os.path.exists(CH.get_key("DIRECTORIES_PATHS", "work_dir")):
                shutil.rmtree(CH.get_key("DIRECTORIES_PATHS", "work_dir"))
                RL.log("main", "clears", CH.get_key("DIRECTORIES_PATHS", "work_dir"))
            os.makedirs(CH.get_key("DIRECTORIES_PATHS", "work_dir"))
            RL.add_log_location(CH.get_key("DIRECTORIES_PATHS", "work_dir"))
            RL.log("main", "creates", CH.get_key("DIRECTORIES_PATHS", "work_dir"))
            RL.log("main", "creates", RL.log_file)
        if args["command"] == "gui":
            handle_gui(args, pb, CH, EH)
        elif args["command"] == "export":
            handle_export(args, pb, CH, EH)
        elif args["command"] == "import":
            handle_import(args, pb, CH)
        elif args["command"] == "open":
            handle_openlist(args, pb, CH)
        else:
            parser.print_help()


if __name__ == "__main__":
    main()
