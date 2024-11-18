def common_arguments(parser):
    """Add common arguments to each subcommand."""
    parser.add_argument(
        "-i",
        "--input",
        required=False,
        help="Path to input file, must be within an Obsidian vault.",
    )
    parser.add_argument(
        "-f",
        "--format",
        required=False,
        nargs="+",
        help="Formats to convert to (e.g., 'quarto::docx quarto::html').",
    )
    parser.add_argument(
        "--OHTML.UseCustomFork",
        action="store_true",
        help="Use a custom ObsidianHTML fork.",
    )
    parser.add_argument(
        "--OHTML.ForkPath",
        help="Path to custom ObsidianHTML fork, if using `--OHTML.UseCustomFork`.",
    )
    parser.add_argument(
        '--loglevel',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help="Set the logging level (default: INFO)",
    )
    parser.add_argument(
        '--custom_pipeline',
        default=None,
        help="Set the logging level (default: INFO)",
    )
    # Add pass-through argument
    parser.add_argument(
        "pass_through",
        nargs="*",
        # help="""
        # Pass-through arguments in format 'namespace::key=value'`nValid Examples:\n- "
        # + "quarto::pdf.author=Ballos"
        # + "\n- "
        # + "quarto::html.author=Professor E GADD"
        # + "\n- "
        # + "quarto::docx.author=Zote the mighty, a knight of great renown
        # """,
        help="""
Pass-through arguments in format 'namespace::key=value'
Valid Examples:
\t- "quarto::pdf.author=Ballos"
\t- "quarto::html.author=Professor E GADD"
\t- "quarto::docx.author=Zote the mighty, a knight of great renown"
""",
    )
    # Add more common arguments as needed


def convert_parser_setup(parser):
    # Convert-specific arguments
    parser.add_argument(
        "--last-exec-dir",
        type=int,
        choices=[1, 2],
        default=1,
        help="Set to '1' for OHTML-output directory, '2' for vault-subfolder.",
    )
    ## OHTML
    parser.add_argument(
        "--OHTMLLevel", type=int, help="Specify OHTML level, e.g., -1 to N."
    )
    parser.add_argument(
        "--OHTML.Verbose", action="store_true", help="Enable verbose logging for OHTML."
    )
    parser.add_argument(
        "--OHTML.Convert",
        action="store_true",
        help="Use OHTML 'convert' verb (default).",
    )
    parser.add_argument(
        "--OHTML.Run",
        action="store_true",
        help="Use OHTML 'run' verb (overrides 'convert' if set).",
    )
    parser.add_argument(
        "--OHTML.TrimErrors",
        action="store_true",
        help="Remove error messages inserted by ObsidianHTML.",
    )
    ## INTER
    parser.add_argument(
        "--INTER.striplocalMDLinks",
        action="store_true",
        help="Set flag to remove local markdown-links and only leave behind the links' title.",
    )

    parser.add_argument(
        "--INTER.stripHashesfromTags",
        action="store_true",
        help="Set flag to remove the hashtag ('#') from tags",
    )
    parser.add_argument(
        "--QUARTO.TrimRefTypes",
        action="store_true",
        help="set flag to remove prefixes from crossreferences. (E.g. link to figure with [1], instead of [Fig. 1])",
    )

    parser.add_argument(
        "--IntermediatesRemovalLevel",
        type=int,
        help="Specify intermediate file removal level.",
    )


def parser_add_disablers(convert_parser):
    # Disablers
    disablers_group = convert_parser.add_argument_group("Disablers")
    disablers_group.add_argument(
        "--noMove", action="store_true", help="Convert the note locally."
    )
    disablers_group.add_argument(
        "--noIntermediates",
        action="store_true",
        help="Delete intermediate files after execution.",
    )
    disablers_group.add_argument(
        "--noRender",
        action="store_true",
        help="Only create (q|r)md file without rendering.",
    )
    disablers_group.add_argument(
        "--noOpen",
        action="store_true",
        help="Do not open output directory after execution.",
    )
    disablers_group.add_argument(
        "--noContent",
        action="store_true",
        help="Generate chapter outline only, no content blocks.",
    )
    # Add more disabler arguments as needed


def gui_parser_setup(gui_parser):
    # GUI-specific options
    gui_parser.add_argument(
        "--theme", choices=["light", "dark"], default="light", help="GUI theme"
    )
    gui_parser.add_argument(
        "--fullscreen", action="store_true", help="Launch GUI in fullscreen mode"
    )
