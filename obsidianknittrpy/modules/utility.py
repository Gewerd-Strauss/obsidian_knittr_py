def convert_format_args(args):
    """Execute the convert command."""

    # Prepare a dictionary for the arguments
    arguments = {}

    # Handle pass-through arguments
    if args.pass_through:
        for item in args.pass_through:
            if "::" in item and "=" in item:
                key, value = item.split("=", 1)
                arguments[key.strip()] = value.strip()
            else:
                # Here, we can just store the item as is
                arguments[item.strip()] = (
                    ""  # Assuming you want an empty value for other pass-through items
                )

    # Add other arguments to the dictionary
    for key, value in vars(
        args
    ).items():  # Use vars() to convert Namespace to dictionary
        if key != "pass_through":  # Skip pass_through since it's already handled
            arguments[key] = value  # Add each argument to the dictionary

    # Print all arguments in the specified format
    print("Formatted Arguments:")
    for k, v in arguments.items():
        print(f'["{k}"] = "{v}"')

    return arguments


def init_picknick_basket():
    # Define the settings dictionary
    settings = {
        "bVerboseCheckbox": bool,  # boolean
        "bKeepFilename": bool,  # boolean
        "bBackupOutput": bool,  # boolean
        "bRendertoOutputs": bool,  # boolean
        "bRemoveHashTagFromTags": bool,  # boolean
        "bRemoveQuartoReferenceTypesFromCrossrefs": bool,  # boolean
        "bConvertInsteadofRun": bool,  # boolean
        "bRemoveObsidianHTMLErrors": bool,  # boolean
        "bRestrictOHTMLScope": bool,  # boolean
        "bStripLocalMarkdownLinks": bool,  # boolean
        "ExecutionDirectory": str,  # path/directory
        "bAutoSubmitOTGUI": bool,  # boolean
        "bUseOwnOHTMLFork": bool,  # boolean
    }
    manuscript = {
        "manuscript_path": str,  # path
        "manuscript_dir": str,  # directory
        "manuscript_name": str,  # filename
    }
    # Define the other dictionary
    other = {
        "sel": list,  # placeholder for selection
        "output_formats": {},  # list of output formats
        "input_suffixes": [],  # list of input suffixes
        "file_suffixes": [],  # list of file suffixes
    }

    return {"settings": settings, "objects": other, "manuscript": manuscript}
