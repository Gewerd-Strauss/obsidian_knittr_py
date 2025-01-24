import logging


def prepare_file_strings(file_string, output_types, output_format_values):
    """
    Prepares a dictionary of file strings per format to render.

    :param file_string: The single file-string to use for all formats.
    :param output_types: A list of format names to render to (e.g., ['quarto::pdf', 'quarto::html']).
    :param output_format_values: A dict with keys matching format names, containing the YAML data for each format.
    :return: A dict with format names as keys and the file-string as the value.
    """
    # Initialize the file_strings dictionary with specified formats
    file_strings = {}

    # Iterate over the specified output types
    for format_name in output_types:
        if format_name in output_format_values:
            # Assign the same file_string to each format in file_strings
            file_strings[format_name] = file_string
        else:
            # Log or handle the case where the format is not found in output_format_values
            logging.warning(
                f"Format '{format_name}' not found in output_format_values."
            )

    return file_strings


def prepare_file_suffixes(output_formats):
    """
    Extracts file suffixes from the output_formats dictionary.

    :param output_formats: Dictionary where keys are format names and values are dictionaries containing 'filesuffix' key.
    :return: Dictionary mapping format names to their respective file suffixes.
    """
    file_suffixes = {}
    for format_name, format_data in output_formats.items():
        # Extract the 'filesuffix' if it exists in the format_data dictionary
        if hasattr(format_data, "filesuffix"):
            file_suffixes[format_name] = format_data.filesuffix
        else:
            # Optionally, handle the case where 'filesuffix' is missing
            print(f"Warning: 'filesuffix' not found for format {format_name}")

    return file_suffixes
