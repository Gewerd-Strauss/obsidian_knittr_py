import os
import yaml
import subprocess
import logging
from obsidianknittrpy.modules.rendering.YamlHandler import YamlHandler


class RenderingPipeline:
    """
    Rendering pipeline class responsible for taking multiple manuscript-strings in different formats
    and rendering them into documents.
    """

    def __init__(
        self,
        file_strings,
        file_suffixes,
        output_directory="output",
        input_name=None,
        custom_file_names=None,
        debug=False,
        log_level=None,
        RL=None,
    ):
        """
        Initialize the rendering pipeline.

        :param file_strings: Dict of format-specific strings to be rendered, e.g., {'html': 'html_file_string', 'pdf': 'pdf_file_string'}
        :param output_directory: Directory to store the rendered outputs
        :param input_name: Optional input note filename for naming output files
        :param custom_file_names: Optional dict of custom file names per format, e.g., {'html': 'custom_name.html'}
        :param debug: Enable or disable debug logging
        """
        self.file_strings = file_strings
        self.file_suffixes = file_suffixes
        self.output_directory = output_directory
        self.input_name = input_name
        self.custom_file_names = custom_file_names if custom_file_names else {}
        self.debug = debug
        self.RL = RL

        # Set up logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(level=log_level)

        # Ensure output directory exists
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory, exist_ok=True)
            self.RL.log(
                self.__class__.__module__
                + "."
                + self.__class__.__qualname__
                + ".render",
                "created",
                self.output_directory,
            )
        print("\n")
        self.logger.info("RenderingPipeline initialized.")

    def validate(self):
        """
        Placeholder method to be called for various validations.
        """
        # Example validation: Ensure `file_strings` is a dictionary
        if not isinstance(self.file_strings, dict):
            self.logger.error(
                "file_strings must be a dictionary of format-specific strings."
            )
            raise ValueError(
                "file_strings must be a dictionary of format-specific strings."
            )
        self.logger.debug("Validation passed.")

    def set_working_directory(self, working_directory=None):
        """
        Sets the instance's working directory. Default is project directory unless specified.
        """
        if working_directory:
            os.chdir(working_directory)
            self.logger.info(f"Working directory set to {working_directory}")
            self.RL.log(
                self.__class__.__module__
                + "."
                + self.__class__.__qualname__
                + ".render",
                "set workdir",
                working_directory,
            )
        else:
            self.logger.info("Using default project directory as working directory.")

    def yamlialize(self, parameters, format_name):
        """
        Takes a dictionary of parameters and a format-name, converts it into a YAML file
        for Quarto rendering using the YamlHandler.

        :param parameters: Dict of YAML parameters for Quarto.
        :param format_name: Format name (e.g., 'html', 'pdf') to determine YAML file name.
        """
        yaml_file_path = os.path.join(
            self.output_directory, f"{format_name.replace('::', '_')}_config.yaml"
        )
        YamlHandler.clean_yaml_dump(parameters, yaml_file_path)
        self.RL.log(
            self.__class__.__module__
            + "."
            + self.__class__.__qualname__
            + ".yamlialize",
            "created",
            yaml_file_path,
        )
        self.logger.info(f"YAML configuration file created: {yaml_file_path}")
        return yaml_file_path

    def determine_output_filename(self, format_name):
        """
        Determines the output file name based on provided configurations.

        :param format_name: Format name (e.g., 'html', 'pdf').
        :return: Full path for the output file.
        """
        suffix = self.file_suffixes[format_name]
        if format_name in self.custom_file_names:
            filename = self.custom_file_names[format_name]
        elif self.input_name:
            filename = f"{self.input_name}.{suffix}"
        else:
            filename = f"index.{suffix}"

        output_file_path = os.path.join(self.output_directory, filename)
        self.logger.debug(f"Output filename determined: {output_file_path}")
        return output_file_path

    def write_file_string(self, file_string, format_name):
        """
        Writes the file string content to a temporary file for Quarto rendering.

        :param file_string: The file content to be written.
        :param format_name: Format name used in the filename.
        :return: Path to the temporary file.
        """
        file_path = os.path.join(
            self.working_directory, f"temp_{format_name.replace('::', '_')}.qmd"
        )
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(file_string)
        self.logger.info(f"File string written to: {file_path}")
        self.RL.log(
            self.__class__.__module__
            + "."
            + self.__class__.__qualname__
            + ".write_file_string",
            "created",
            file_path,
        )
        return file_path

    def render(self, parameters={}, working_directory=None):
        """
        Main rendering method. Renders each file string to its specified format using Quarto.

        :param parameters: Dictionary of common YAML parameters to apply to all formats.
        :param working_directory: The working directory for Quarto. Defaults to the .qmd file’s directory.
        """
        for format_name, file_string in self.file_strings.items():
            self.logger.info(f"Rendering format: {format_name}")

            # Generate YAML configuration for this format
            yaml_file_path = self.yamlialize(parameters[format_name], format_name)
            self.working_directory = working_directory
            # Write the file string to a temporary file
            temp_file_path = self.write_file_string(file_string, format_name)

            # Determine output filename
            output_file_path = self.determine_output_filename(format_name)

            # Determine the working directory for Quarto
            quart_working_directory = working_directory or os.path.dirname(
                temp_file_path
            )
            self.logger.info(
                f"Setting Quarto's working-directory to '{quart_working_directory}'"
            )
            self.RL.log(
                self.__class__.__module__
                + "."
                + self.__class__.__qualname__
                + ".render",
                "set quarto's workdir",
                quart_working_directory,
            )
            # Run Quarto render command
            try:
                command = [
                    "quarto",
                    "render",
                    temp_file_path,
                    "--to",
                    self.file_suffixes[format_name],
                    "--metadata-file",
                    yaml_file_path,
                    "--output",
                    os.path.basename(output_file_path),
                ]
                subprocess.run(command, check=True, cwd=quart_working_directory)
                self.logger.info(
                    f"Rendered {format_name} output to: '{os.path.normpath(os.path.join(quart_working_directory,os.path.basename(output_file_path)))}'"
                )
                self.RL.log(
                    self.__class__.__module__
                    + "."
                    + self.__class__.__qualname__
                    + ".render",
                    "rendered",
                    os.path.normpath(temp_file_path),
                )
                self.RL.log(
                    self.__class__.__module__
                    + "."
                    + self.__class__.__qualname__
                    + ".render",
                    "created",
                    os.path.normpath(
                        os.path.join(
                            quart_working_directory, os.path.basename(output_file_path)
                        )
                    ),
                )
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Failed to render {format_name} output. Error: {e}")
