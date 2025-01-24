# main.py
import os
import sys
import shutil
from obsidianknittrpy.modules.commandline import (
    commandline_setup,
)
from obsidianknittrpy.modules.command_handlers import (
    handle_gui,
    handle_version,
    handle_export,
    handle_import,
    handle_openlist,
    handle_processingmodule_add,
    handle_processingmodule_remove,
    handle_processingmodule_list,
)
from obsidianknittrpy.modules.utility import (
    init_picknick_basket,
    convert_format_args,
    pre_configure_obsidianhtml_fork,
)
from obsidianknittrpy.modules.core.ResourceLogger import ResourceLogger
from obsidianknittrpy.modules.core.ConfigurationHandler import ConfigurationHandler
from obsidianknittrpy.modules.core.ExternalHandler import ExternalHandler
from obsidianknittrpy.modules.core.CustomModuleHandler import CustomModuleHandler
import logging


def main():
    RL = ResourceLogger()
    parser = commandline_setup()
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
        if args["command"] not in ["open", "processingmodules"]:

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
        elif args["command"] == "processingmodules":
            CMH = CustomModuleHandler(
                custom_modules_dir=CH.get_key("DIRECTORIES_PATHS", "custom_module_dir"),
                loglevel=args["loglevel"],
            )
            if args["custommodule_command"] == "add":
                handle_processingmodule_add(args, CH, CMH)
            if args["custommodule_command"] == "remove":
                handle_processingmodule_remove(args, CH, CMH)
            if args["custommodule_command"] == "list":
                handle_processingmodule_list(CH, CMH)
        else:
            parser.print_help()


if __name__ == "__main__":
    main()
