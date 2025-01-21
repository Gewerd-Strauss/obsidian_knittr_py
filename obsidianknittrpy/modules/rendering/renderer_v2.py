import subprocess, os, yaml, json, shutil, re
from obsidianknittrpy.modules.rendering.YamlHandler import YamlHandler
from obsidianknittrpy.modules.core.ResourceLogger import ResourceLogger
import logging
import time


class RenderManager:
    def __init__(
        self,
        file_strings,
        file_suffixes,
        mod_directory,
        output_directory="output",
        input_name=None,
        custom_file_names=None,
        log_level=None,
        use_parallel=False,
        debug=False,
        parameters=None,
        working_directory=None,
    ):
        self.mod_directory = mod_directory
        self.use_parallel = use_parallel
        self.file_strings = file_strings
        self.file_suffixes = file_suffixes
        self.output_directory = output_directory
        self.input_name = input_name
        self.custom_file_names = custom_file_names if custom_file_names else {}
        self.debug = debug
        self.log_level = log_level
        self.dependencies = {}
        self.parameters = parameters if parameters else {}
        self.working_directory = working_directory

        # Set up logging
        self.logger = logging.getLogger(__name__)
        self.resource_logger = ResourceLogger(output_directory)
        self.logger.setLevel(level=log_level)
        # Ensure output directory exists
        os.makedirs(self.output_directory, exist_ok=True)
        self.mod_filesjson_data = os.path.normpath(
            os.path.join(self.mod_directory, "index\\files.json")
        )
        self.ohtml_paths_collection = os.path.normpath(
            os.path.join(self.mod_directory, "paths.json")
        )
        print("\n")
        self.logger.info("RenderManager initialized.")

    def parse_mod_files(self):
        """Parses obsidianHTML mod files (e.g., files.json, paths.json)."""
        try:
            with open(self.mod_filesjson_data, "r") as f:
                self.dependency_files = json.load(f)
                self.resource_logger.log(
                    action="read",
                    module=self.__class__.__module__
                    + "."
                    + self.__class__.__qualname__
                    + ".parse_mod_files",
                    resource=self.mod_filesjson_data,
                )
            with open(self.ohtml_paths_collection, "r") as f:
                self.ohtml_paths = json.load(f)
                self.resource_logger.log(
                    action="read",
                    module=self.__class__.__module__
                    + "."
                    + self.__class__.__qualname__
                    + ".parse_mod_files",
                    resource=self.ohtml_paths_collection,
                )
            # Additional parsing logic if required for other mod files.
        except FileNotFoundError:
            raise FileNotFoundError(f"Mod files not found in {self.mod_directory}")

    def extract_yaml_frontmatter(self, input_str: str):
        """
        Modify the frontmatter of a Quarto document and return it formatted properly.
        Assumes that the frontmatter is a valid YAML block within the document.
        """
        # Split the document into frontmatter and content
        if input_str.startswith('---'):
            frontmatter_end = input_str.find('---', 3)  # Find the second '---'
            if frontmatter_end == -1:
                raise ValueError("Invalid frontmatter format, no closing '---' found.")

            frontmatter_str = input_str[
                3:frontmatter_end
            ].strip()  # Extract frontmatter
            markdown_content = input_str[
                frontmatter_end + 3 :
            ].strip()  # Extract markdown content

            # Parse the YAML frontmatter into a Python dictionary
            try:
                frontmatter_dict = yaml.safe_load(frontmatter_str)
            except yaml.YAMLError as e:
                raise ValueError(f"Error parsing YAML frontmatter: {e}")

            # Dump the frontmatter back into YAML format
            # We set default_flow_style=False for pretty formatting
            # You can also customize the indentations here if needed
            return frontmatter_dict
        else:
            raise ValueError("The input-string does not contain valid frontmatter.")

    def _is_relative_path(self, value):
        """
        Helper method to check if a string is a relative file path.
        """
        # A path is relative if:
        # - It is not absolute (no drive letter or leading '/')
        # - It is not empty
        # - It does not start with a drive letter or a root directory
        return (
            not os.path.isabs(value)
            and not value.startswith(('/', '\\'))
            and ':' not in value
        )

    def convert_to_forward_slashes(self, path: str) -> str:
        return path.replace("\\", "/")

    def find_matching_directories(self, paths, pattern):
        # Compile the regex pattern
        regex = re.compile(pattern)

        # Filter directories matching the pattern
        matching_directories = [path for path in paths if regex.search(path)]

        return matching_directories

    def resolve_dependencies(self):
        """Resolves file and directory dependencies."""
        frontmatter_keys = ["csl", "bibliography", "filters"]
        self.logger.info(f"Resolving File-dependencies:")
        for format_name, file_string in self.file_strings.items():
            # TODO: in here, parse the text and replace dependencies as found
            # parse the file-string. for every match, copy the entry in self.dependency_files
            # over. The root into which to copy shall be %working_directory%
            # The root in the self.dependency_files from which to trim is the `tmpdir/input` .
            # The directory-structures beyond that are what is required to be the second half of the combined
            # filepath of the resolved dependency. Doing this should mean that relative filepaths will be
            # parseable by quarto when converting the doc; since they were placed into and relative to the
            # working directory.
            #
            # Exception: any filepath structured like `./path/to/file.suffix`, or `../path/to/another/file.suffix`
            # will fail because we cannot just base them into working_directory and call it a day. Instead, for these
            # we must update the references in the filestrings.

            # Find all occurences of
            # - "^\w*source\((?<path>.*(R|RData|xlsx|csv|...))\)"
            # - "(\W+\.bib)"
            # - "(\W+\.csl)"
            # check if they are relative. If they are, continue with replacing them
            #
            # Once they are collected, iterate over self.dependency_files
            # And on match,
            # - replace the relative paths with an absolute path constructed from %working_directory%
            # - replace the reference to that file in the file-string with the constructed absolute path in %working_directory%
            #           - is this dumb? I think this isn't actually necessary, since the working directory is already the working directory. If the files are positioned correctly therein, we can just insert them
            #             However, for files which lay further upstream than the working directory, their paths will have to be fixed if they are relative.
            try:
                frontmatter = self.extract_yaml_frontmatter(file_string)
                frontmatter_init = frontmatter
            except ValueError as e:
                self.logger.error(f"Error parsing frontmatter for  {format_name}: {e}")
                continue
            # iterate through the specified frontmatter keys
            for key in frontmatter_keys:
                #  Iterate through keys in the list of keys to purge
                # self.logger.info(f"Resolving File-dependencies:")
                if key in frontmatter:
                    values = frontmatter[key]
                    # Check if the value is a string or a list of file paths
                    self.logger.info(f"\t{key} ({format_name})")
                    if not isinstance(values, list):
                        # Handle the case for a single string (a relative file path)
                        values = [values]

                    resolved_values = []
                    for value in values:
                        if "filters" in key:  # in case of filters, we must
                            if self._is_relative_path(value):

                                # Define the pattern
                                pattern = r"_extensions/.*/" + value
                                # get the extensions' files
                                matches = self.find_matching_directories(
                                    self.dependency_files, pattern
                                )
                                # construct the target-paths
                                ## get source-dir
                                source_directory = os.path.dirname(
                                    self.ohtml_paths["obsidian_entrypoint"]
                                )
                                source_extensions_directory = os.path.normpath(
                                    os.path.join(source_directory, "_extensions")
                                )
                                destination_extensions_directory = os.path.normpath(
                                    os.path.join(self.working_directory, '_extensions')
                                )
                                # move them over to the working directory
                                if os.path.exists(source_extensions_directory):
                                    shutil.copytree(
                                        source_extensions_directory,
                                        destination_extensions_directory,
                                        dirs_exist_ok=True,
                                    )
                                    self.resource_logger.log(
                                        resource=destination_extensions_directory,
                                        action="created",
                                        module=__name__ + ".resolve_dependencies",
                                    )
                                resolved_values.append(value)
                            else:
                                resolved_values.append(value)
                            # filters must be provided as a yaml-list, never as a key. even if there is only a single filter active.
                            frontmatter[key] = resolved_values
                        else:
                            if self._is_relative_path(value):
                                resolved_path = self._resolve_dependency_path(value)
                                resolved_path = self.convert_to_forward_slashes(
                                    resolved_path
                                )
                                # resolved_path = os.path.relpath(
                                #     resolved_path, self.working_directory
                                # )
                                if resolved_path:
                                    resolved_values.append(resolved_path)
                                else:
                                    self.logger.error(
                                        f"Could not resolve dependency: {value}"
                                    )
                            else:
                                resolved_values.append(value)
                            frontmatter[key] = (
                                resolved_values
                                if len(resolved_values) > 1
                                else resolved_values[0]
                            )
            if frontmatter != frontmatter_init:
                self.resource_logger.log(
                    resource=f"file-string '{format_name}'",
                    action="modified",
                    module=__name__ + ".resolve_dependencies",
                )
            new_frontmatter = yaml.dump(frontmatter, default_flow_style=False)
            new_file_string = (
                f"---\n{new_frontmatter}---\n{file_string.split('---',2)[2]}"
            )
            self.file_strings[format_name] = new_file_string
            pass
        for dependency in self.dependencies:
            abs_path = os.path.abspath(dependency)
            if not os.path.exists(abs_path):
                raise RuntimeError(
                    f"Dependency {dependency} cannot be resolved at {abs_path}."
                )
            self.dependencies[dependency] = abs_path

    def _resolve_dependency_path(self, relative_path):
        """
        Resolves a relative path by matching it with an entry in self.dependency_files.
        Returns the resolved path or None if not found.
        """
        base_dir = self.ohtml_paths["obsidian_folder"]
        for dependency_path in self.dependency_files:
            # Reconstruct absolute path
            relative_base = os.path.relpath(dependency_path, base_dir)
            if relative_path.lstrip("./") in relative_base:
                # Construct the new path relative to the working directory
                new_path = os.path.join(self.working_directory, relative_base)
                # Ensure the directory exists
                os.makedirs(os.path.dirname(new_path), exist_ok=True)
                # Copy the file to the new path
                shutil.copy(dependency_path, new_path)
                return new_path
        return None

    def yamlialize(self):
        """
        Takes a dictionary of parameters and a format-name, converts it into a YAML file
        for Quarto rendering using the YamlHandler.

        :param parameters: Dict of YAML parameters for Quarto.
        :param format_name: Format name (e.g., 'html', 'pdf') to determine YAML file name.
        """
        yaml_file_paths = {}
        for format_name, file_string in self.file_strings.items():
            yaml_file_paths[format_name] = os.path.join(
                self.output_directory, f"{format_name.replace('::', '_')}_config.yaml"
            )
            YamlHandler.clean_yaml_dump(
                self.parameters[format_name], yaml_file_paths[format_name]
            )
            self.logger.info(
                f"YAML configuration file created: {yaml_file_paths[format_name]}"
            )
            self.resource_logger.log(
                self.__class__.__module__
                + "."
                + self.__class__.__qualname__
                + ".yamlialize",
                "created",
                yaml_file_paths[format_name],
            )
        self.yaml_file_paths = yaml_file_paths

    def execute(self):
        """Sets up and executes the appropriate rendering pipeline."""
        self.parse_mod_files()  # load dependencies
        self.resolve_dependencies()  # TODO: this must modify self.filestrings and resolve dependencies.
        # dependencies in:
        # - frontmatter
        # - codeblocks
        # - embeds/images
        self.yamlialize()  # TODO: this must save the quarto-yaml-configuration-files to file.

        pipeline = (
            MultiRenderingPipeline_v2(
                file_strings=self.file_strings,
                file_suffixes=self.file_suffixes,
                output_directory=self.output_directory,
                input_name=self.input_name,
                custom_file_names=self.custom_file_names,
                debug=self.debug,
                log_level=self.log_level,
                working_directory=self.working_directory,
                yaml_files=self.yaml_file_paths,
            )
            if self.use_parallel
            else RenderingPipeline_v2(
                file_strings=self.file_strings,
                file_suffixes=self.file_suffixes,
                output_directory=self.output_directory,
                input_name=self.input_name,
                custom_file_names=self.custom_file_names,
                debug=self.debug,
                log_level=self.log_level,
                working_directory=self.working_directory,
                yaml_files=self.yaml_file_paths,
            )
        )
        self.logger.info(
            f"Executing {pipeline.__class__.__qualname__} ({"parallel" if self.use_parallel else "sequential"})"
        )
        start_time = time.time()
        pipeline.run()
        self.output_data = {
            "rendered_output_paths": pipeline.rendered_output_paths,
            "rendered_output_directory": pipeline.rendered_output_directory,
        }
        end_time = time.time()
        self.resource_logger.log(
            action="exec-time",
            module=self.__class__.__module__
            + "."
            + self.__class__.__qualname__
            + ".execute",
            resource=f"({"parallel" if self.use_parallel else "sequential"}: {(time.time() - start_time)}s)",
        )
        pass


class RenderingPipeline_v2:
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
        working_directory=None,
        yaml_files=None,
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
        self.working_directory = working_directory
        self.yaml_file_paths = yaml_files
        self.rendered_output_paths = {}

        # Set up logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(level=log_level)
        self.resource_logger = ResourceLogger(output_directory)

        # Ensure output directory exists
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory, exist_ok=True)
            self.resource_logger.log(
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
            self.resource_logger.log(
                self.__class__.__module__
                + "."
                + self.__class__.__qualname__
                + ".render",
                "set workdir",
                working_directory,
            )
        else:
            self.logger.info("Using default project directory as working directory.")

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
        self.resource_logger.log(
            self.__class__.__module__
            + "."
            + self.__class__.__qualname__
            + ".write_file_string",
            "created",
            file_path,
        )
        return file_path

    def run(self):
        """
        Main rendering method. Renders each file string to its specified format using Quarto.
        """
        for format_name, file_string in self.file_strings.items():
            self.logger.info(f"Rendering format: {format_name}")
            # self.resource_logger.log("yamlialize", "created", yaml_file_path)

            # Write the file string to a temporary file
            temp_file_path = self.write_file_string(file_string, format_name)

            # Determine output filename
            output_file_path = self.determine_output_filename(format_name)

            # Determine the working directory for Quarto
            quart_working_directory = self.working_directory
            self.logger.info(
                f"Setting Quarto's working-directory to '{quart_working_directory}'"
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
                    self.yaml_file_paths[format_name],
                    "--output",
                    os.path.basename(output_file_path),
                ]
                subprocess.run(command, check=True, cwd=quart_working_directory)
                abs_output_path = os.path.normpath(
                    os.path.join(
                        quart_working_directory, os.path.basename(output_file_path)
                    )
                )
                self.logger.info(
                    f"Rendered {format_name} output to: '{abs_output_path}'."
                )
                self.rendered_output_paths[format_name] = abs_output_path
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Failed to render {format_name} output. Error: {e}")


from concurrent.futures import ThreadPoolExecutor


class MultiRenderingPipeline_v2(RenderingPipeline_v2):
    def run(self):
        """
        Main rendering method. Renders each file string to its specified format using Quarto.
        Executes in parallel
        """
        self.output_paths = {}
        self.output_filenames = {}
        # prepare file-strings, write to path; then collect the paths.
        for format_name, file_string in self.file_strings.items():
            self.logger.info(f"Rendering format: {format_name}")
            # self.resource_logger.log("yamlialize", "created", yaml_file_path)

            # Write the file string to a temporary file
            self.output_paths[format_name] = self.write_file_string(
                file_string, format_name
            )

            # Determine output filename
            self.output_filenames[format_name] = self.determine_output_filename(
                format_name
            )

            # Determine the working directory for Quarto
        quart_working_directory = self.working_directory
        self.logger.info(
            f"Setting Quarto's working-directory to '{quart_working_directory}'"
        )
        # Run Quarto render command
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self.futures_render, format_name)
                for format_name, parameters in self.output_paths.items()
            ]
            for future in futures:
                future.result()

        dirs = []
        for (
            format_name,
            file_path,
        ) in self.rendered_output_paths.items():  # retrieve uniform dirname
            dir_name = os.path.dirname(file_path)
            dirs.append(dir_name)

        if len(set(dirs)) <= 1:  # check if all elements are identical
            self.rendered_output_directory = dirs[0]

    def futures_render(self, format_name):
        """Combines YAML generation and rendering for parallel execution."""
        # yaml_file_path = self.yamlialize(parameters, format_name)
        # self.resource_logger.log("MultiRenderingPipeline", "rendering", yaml_file_path)

        # Render via subprocess.
        try:
            command = [
                "quarto",
                "render",
                self.output_paths[format_name],
                "--to",
                self.file_suffixes[format_name],
                "--metadata-file",
                self.yaml_file_paths[format_name],
                "--output",
                os.path.basename(self.output_filenames[format_name]),
            ]
            subprocess.run(command, check=True, cwd=self.working_directory)
            abs_output_path = os.path.normpath(
                os.path.join(
                    self.working_directory,
                    os.path.basename(self.output_filenames[format_name]),
                )
            )
            self.logger.info(f"Rendered {format_name} output to: '{abs_output_path}'.")
            self.rendered_output_paths[format_name] = abs_output_path
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to render {format_name} output. Error: {e}")
