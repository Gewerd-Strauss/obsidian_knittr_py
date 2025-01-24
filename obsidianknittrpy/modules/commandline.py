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
        help="Provide absolute path to a yaml-file containing a custom processing pipeline to execute. Source-files declaring Modules are expected to be placed in the processing-module-folder of the utility",
    )
    parser.add_argument(
        '--custom_format_definitions',
        default=None,
        help="Provide absolute path to a yaml-file containing a custom format-definition to use.",
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
    pass


def import_parser_setup(import_parser):
    import_parser.add_argument(
        "-i",
        "--input",
        required=False,
        help="Path to exported configuration-file for this utility.",
    )
    import_parser.add_argument(
        '--custom_pipeline',
        default=None,
        help="Provide absolute path to a yaml-file containing a custom processing pipeline to execute. Source-files declaring Modules are expected to be placed in the processing-module-folder of the utility",
    )
    import_parser.add_argument(
        '--custom_format_definitions',
        default=None,
        help="Provide absolute path to a yaml-file containing a custom format-definition to use.",
    )
    import_parser.add_argument(
        '--loglevel',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help="Set the logging level (default: INFO)",
    )
    import_parser.add_argument(
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


def export_parser_setup(export_parser):
    # EXPORT-specific options
    export_parser.add_argument(
        "-i",
        "--input",
        required=False,
        help="Path to exported configuration-file for this utility.",
    )
    export_parser.add_argument(
        '--custom_pipeline',
        default=None,
        help="Provide absolute path to a yaml-file containing a custom processing pipeline to execute. Source-files declaring Modules are expected to be placed in the processing-module-folder of the utility",
    )
    export_parser.add_argument(
        '--custom_format_definitions',
        default=None,
        help="Provide absolute path to a yaml-file containing a custom format-definition to use.",
    )
    export_parser.add_argument(
        '--loglevel',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help="Set the logging level (default: INFO)",
    )
    export_parser.add_argument(
        "pass_through",
        nargs="*",
        help="""
Pass-through arguments in format 'namespace::key=value'
Valid Examples:
\t- "quarto::pdf.author=Ballos"
\t- "quarto::html.author=Professor E GADD"
\t- "quarto::docx.author=Zote the mighty, a knight of great renown"
""",
    )


def set_parser_setup(set_parser):
    set_parser.add_argument(
        "file", help="The file of the key-value-pair (e.g., obsidian-html)."
    )
    set_parser.add_argument("key", help="The key (e.g., obsidian-html).")
    set_parser.add_argument("value", help="The value to associate with the 'key'.")
    set_parser.add_argument(
        "pass_through",
        nargs="*",
        help="""
        Pass-through arguments in format 'namespace::key=value'
        Valid Examples:
        \t- "quarto::pdf.author=Ballos"
        \t- "quarto::html.author=Professor E GADD"
        \t- "quarto::docx.author=Zote the mighty, a knight of great renown"
        """,
    )
    set_parser.add_argument(
        '--loglevel',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help="Set the logging level (default: INFO)",
    )


def openlist_parser_setup(openlist_parser):
    # Positional argument for the format (optional)
    openlist_parser.add_argument(
        "input",  # Positional argument
        nargs="?",  # Makes this argument optional
        help="Specify the format to open (e.g., 'quarto::html'). If not provided, the folder containing the output-files is opened.",
        type=str,
    )

    # Positional argument for pass-through parameters (optional)
    openlist_parser.add_argument(
        "pass_through",
        nargs="*",  # This allows for multiple pass-through arguments, if needed
        help="""
        Pass-through arguments in format 'namespace::key=value'
        Valid Examples:
        \t- "quarto::pdf.author=Ballos"
        \t- "quarto::html.author=Professor E GADD"
        \t- "quarto::docx.author=Zote the mighty, a knight of great renown"
        """,
    )
    openlist_parser.add_argument(
        '--loglevel',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help="Set the logging level (default: INFO)",
    )
    return openlist_parser


def unset_parser_setup(unset_parser):
    unset_parser.add_argument(
        "file", help="The file of the key-value-pair (e.g., obsidian-html)."
    )
    unset_parser.add_argument("key", help="The key (e.g., obsidian-html).")
    unset_parser.add_argument(
        "pass_through",
        nargs="*",
        help="""
        Pass-through arguments in format 'namespace::key=value'
        Valid Examples:
        \t- "quarto::pdf.author=Ballos"
        \t- "quarto::html.author=Professor E GADD"
        \t- "quarto::docx.author=Zote the mighty, a knight of great renown"
        """,
    )
    unset_parser.add_argument(
        '--loglevel',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help="Set the logging level (default: INFO)",
    )


def list_parser_setup(list_parser):
    list_parser.add_argument(
        "file", nargs="?", help="The file of the key-value-pair (e.g., obsidian-html)."
    )
    list_parser.add_argument(
        "pass_through",
        nargs="*",
        help="""
        Pass-through arguments in format 'namespace::key=value'
        Valid Examples:
        \t- "quarto::pdf.author=Ballos"
        \t- "quarto::html.author=Professor E GADD"
        \t- "quarto::docx.author=Zote the mighty, a knight of great renown"
        """,
    )
    list_parser.add_argument(
        '--loglevel',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help="Set the logging level (default: INFO)",
    )


def version_parser_setup(version_parser):
    version_parser.add_argument(
        "--clean",
        "-c",
        default=False,
        action="store_true",
        help="Return version number without descriptor-string.",
    )


def custommodule_parser_setup(custommodule_parser):
    """
    Set up the `custommodule` subparser and its subcommands: `list`, `add`, and `remove`.
    """

    # Add subparsers for `custommodule`
    custommodule_subparsers = custommodule_parser.add_subparsers(
        title="Custom Module Commands",
        dest="custommodule_command",
    )

    # Subcommand: `list`
    list_parser = custommodule_subparsers.add_parser(
        "list",
        help="List all custom modules.",
    )
    list_parser.add_argument(
        "--detailed",
        action="store_true",
        help="Display detailed information about each module.",
    )
    list_parser.add_argument(
        "pass_through",
        nargs="*",
        help="""
        Pass-through arguments in format 'namespace::key=value'
        Valid Examples:
        \t- "quarto::pdf.author=Ballos"
        \t- "quarto::html.author=Professor E GADD"
        \t- "quarto::docx.author=Zote the mighty, a knight of great renown"
        """,
    )
    list_parser.add_argument(
        '--loglevel',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help="Set the logging level (default: INFO)",
    )

    # Subcommand: `add`
    add_parser = custommodule_subparsers.add_parser(
        "add",
        help="Add a new custom module.",
    )
    add_parser.add_argument(
        "module_path",
        type=str,
        help="Path to the Python file containing the custom module.",
    )
    add_parser.add_argument(
        "pass_through",
        nargs="*",
        help="""
        Pass-through arguments in format 'namespace::key=value'
        Valid Examples:
        \t- "quarto::pdf.author=Ballos"
        \t- "quarto::html.author=Professor E GADD"
        \t- "quarto::docx.author=Zote the mighty, a knight of great renown"
        """,
    )
    add_parser.add_argument(
        '--loglevel',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help="Set the logging level (default: INFO)",
    )

    # Subcommand: `remove`
    remove_parser = custommodule_subparsers.add_parser(
        "remove",
        help="Remove an existing custom module.",
    )
    remove_parser.add_argument(
        "module_name",
        type=str,
        help="Name of the module to remove.",
    )
    remove_parser.add_argument(
        "pass_through",
        nargs="*",
        help="""
        Pass-through arguments in format 'namespace::key=value'
        Valid Examples:
        \t- "quarto::pdf.author=Ballos"
        \t- "quarto::html.author=Professor E GADD"
        \t- "quarto::docx.author=Zote the mighty, a knight of great renown"
        """,
    )
    remove_parser.add_argument(
        '--loglevel',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help="Set the logging level (default: INFO)",
    )

    # Set a default function to handle unknown subcommands
    custommodule_parser.set_defaults(func=lambda args: custommodule_parser.print_help())
