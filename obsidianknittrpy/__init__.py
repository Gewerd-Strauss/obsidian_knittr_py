import argparse
import sys


def main():
    """Main entry point for the package."""
    # Parse command-line arguments
    parser_ = setup_parser()
    args = parser_.parse_args()

    # If no arguments, show help dialog
    if len(sys.argv) == 1:
        parser_.print_help()
        sys.exit(1)

    # Process commands based on parsed arguments
    if args.command == "convert":
        handle_convert(args)
    elif args.command == "gui":
        handle_gui(args)
    elif args.command.lower() in ["version", "-v"]:
        handle_version()
    elif args.command in ["help", "-h"]:
        parser_.print_help()
        sys.exit(1)


def setup_parser():
    """Parse command-line arguments for the package."""
    parser = argparse.ArgumentParser(
        description="A utility package with 'convert' and 'gui' commands."
    )
    # parser.add_help(True)

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Define 'convert' command
    convert_parser = subparsers.add_parser("convert", help="Run the conversion process")
    convert_parser.add_argument("-i", "--input", required=True, help="Input file path")
    convert_parser.add_argument(
        "-o", "--output", required=True, help="Output file path"
    )

    # Define 'gui' command
    gui_parser = subparsers.add_parser("gui", help="Launch the GUI")
    gui_parser.add_argument(
        "--theme", default="light", choices=["light", "dark"], help="GUI theme"
    )

    # Define 'help' command

    help_parser = subparsers.add_parser("help", help="Show the help")
    help_parser.add_argument("gui", help="DD")

    return parser


def handle_convert(args):
    """Handle the 'convert' command."""
    print(f"Converting file from {args.input} to {args.output}")
    # Conversion logic goes here


def handle_gui(args):
    """Handle the 'gui' command."""
    print(f"Launching GUI with {args.theme} theme")
    # GUI launch logic goes here


def handle_version():
    """Handle the 'version' command."""
    print(f"Versioning not set up yet. Alpha. 0.0.1.9000")
    exit(0)


if __name__ == "__main__":
    main()
