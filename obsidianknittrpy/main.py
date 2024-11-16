# main.py
import argparse
import sys
from obsidianknittrpy.modules.commandline import (
    common_arguments,
    convert_parser_setup,
    parser_add_disablers,
    gui_parser_setup,
)
from obsidianknittrpy.modules.command_handlers import (
    handle_convert,
    handle_gui,
)
from obsidianknittrpy.modules.utility import (
    init_picknick_basket,
    convert_format_args,
)
from obsidianknittrpy.modules.ConfigurationHandler import ConfigurationHandler
import logging


def main():
    parser = argparse.ArgumentParser(
        description="Utility supporting 'convert' and 'gui' commands.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- 'convert' command setup ---
    convert_parser = subparsers.add_parser(
        "convert",
        help="Convert a note to specified formats.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    common_arguments(convert_parser)
    convert_parser_setup(convert_parser)
    parser_add_disablers(convert_parser)

    # --- 'gui' command setup ---
    gui_parser = subparsers.add_parser(
        "gui", help="Launch GUI mode.", formatter_class=argparse.RawTextHelpFormatter
    )
    common_arguments(gui_parser)  # Reuse shared arguments for 'gui'
    gui_parser_setup(gui_parser)

    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel)

    pb = init_picknick_basket()
    # Command handling
    # 1. translate arguments
    args = convert_format_args(args)

    # 2. setup config-manager
    CH = ConfigurationHandler(
        last_run_path=None, loglevel=args["loglevel"], is_gui=True
    )

    # 3. setup resource-logger
    # RL = ResourceLogger()
    if args["command"] == "convert":
        # Parse pass-through arguments
        print("implement commandline-pathway")
        # Print all arguments in the desired format
        # print_arguments(parsed_args)
        handle_convert(args, pb, CH)
    elif args["command"] == "gui":
        handle_gui(args, pb, CH)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
