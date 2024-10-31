# main.py
import argparse
from obsidianknittrpy.modules.commandline import (
    common_arguments,
    convert_parser_setup,
    parser_add_disablers,
    gui_parser_setup,
)


from obsidianknittrpy.modules.command_handlers import handle_convert, handle_gui


def main():
    parser = argparse.ArgumentParser(
        description="Utility supporting 'convert' and 'gui' commands."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- 'convert' command setup ---
    convert_parser = subparsers.add_parser(
        "convert", help="Convert a note to specified formats."
    )
    common_arguments(convert_parser)
    convert_parser_setup(convert_parser)
    parser_add_disablers(convert_parser)

    # --- 'gui' command setup ---
    gui_parser = subparsers.add_parser("gui", help="Launch GUI mode.")
    common_arguments(gui_parser)  # Reuse shared arguments for 'gui'
    gui_parser_setup(gui_parser)

    args = parser.parse_args()

    # Command handling
    if args.command == "convert":
        handle_convert(args)
    elif args.command == "gui":
        handle_gui(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
