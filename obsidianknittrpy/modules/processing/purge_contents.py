from .processing_module_runner import BaseModule
import re
import yaml
import os


class PurgeContents(BaseModule):
    """
    Removes all contents in a document, except
    1. the frontmatter
    2. the section-headers, e.g.

    ``````qmd
    ---
    format: pdf
    ---

    # This is a header

    with some contents.

    ## and a subheader

    ```{r some_codeblock}
    variable = 2
    new_var = variable**variable
    ```

    Lorem ipsum dolor sit amet, consectetur adipiscing
    elit, sed do eiusmod tempor incididunt ut labore et
    dolore magna aliqua. Ut enim ad minim veniam, quis
    nostrud exercitation ullamco laboris nisi ut aliquip
    ex ea commodo consequat. Duis aute irure dolor in
    reprehenderit in voluptate velit esse cillum dolore
    eu fugiat nulla pariatur. Excepteur sint occaecat
    cupidatat non proident, sunt in culpa qui officia
    deserunt mollit anim id est laborum.
    ``````

    This document will be converted into

    ``````qmd
    ---
    format: pdf
    ---

    # This is a header

    ## and a subheader

    ``````

    # Limitations

    The following cases will cause this module to fail:

    The presence of a dynamic bibliography- or CSL-file in the working-directory, e.g.

    ``````qmd
    ---
    format: pdf
    bibliography:
    - grateful-refs.bib
    ---
    # The document body

    continues on here
    ``````

    Because this utility by default cleans its working directory before rendering.
    Since this means that these local files can never exist to be referenced by 'Quarto' during rendering, these keys are dropped from the frontmatter to prevent 'Quarto' from crashing.
    """

    def __init__(
        self,
        name="PurgeContents",
        config=None,
        log_directory=None,
        past_module_instance=None,
        past_module_method_instance=None,
    ):
        super().__init__(
            name,
            config=config,
            log_directory=log_directory,
            past_module_instance=past_module_instance,
            past_module_method_instance=past_module_method_instance,
        )
        self.purged_frontmatter_keys = self.get_config(
            "purged_frontmatter_keys", default=[]
        )

    def modify_frontmatter(self, data):
        """
        Modifies the front-matter to remove keys which contain relative file-paths - if they do not exist.
        """

        # Split the data into frontmatter and content (assuming YAML frontmatter starts with '---')
        if data.startswith('---'):
            frontmatter_end = data.find('---', 3)  # Find the second '---'
            if frontmatter_end == -1:
                raise ValueError("Invalid frontmatter format, no closing '---' found.")
            frontmatter_str = data[3:frontmatter_end].strip()  # Extract frontmatter
            markdown_content = data[
                frontmatter_end + 3 :
            ].strip()  # The rest of the content

            # Parse the YAML frontmatter into a Python dictionary
            frontmatter_dict = yaml.safe_load(frontmatter_str)

            # If frontmatter is None (empty YAML), initialize as an empty dictionary
            if frontmatter_dict is None:
                frontmatter_dict = {}

            # Iterate through keys in the list of keys to purge
            for key in self.purged_frontmatter_keys:
                if key in frontmatter_dict:
                    value = frontmatter_dict[key]
                    # Check if the value is a string or a list of file paths
                    if isinstance(value, str):
                        # Handle the case for a single string (a relative file path)
                        if self._is_relative_path(value) and not os.path.exists(value):
                            del frontmatter_dict[key]
                    elif isinstance(value, list):
                        # Handle the case for a list of file paths
                        invalid_paths = [
                            v
                            for v in value
                            if isinstance(v, str) and not os.path.isabs(v)
                        ]
                        if len(invalid_paths) == len(value):
                            # If all paths in the list are invalid, remove the key
                            del frontmatter_dict[key]
                        else:
                            # Remove invalid paths from the list
                            frontmatter_dict[key] = [
                                v
                                for v in value
                                if (isinstance(v, str) and os.path.isabs(v))
                            ]

            # Convert the modified frontmatter dictionary back to a YAML string
            new_frontmatter_str = yaml.dump(frontmatter_dict, default_flow_style=False)

            # Reassemble the final file content
            new_data = f'---\n{new_frontmatter_str}---\n{markdown_content}'

            return new_data
        else:
            raise ValueError("Invalid frontmatter format, no opening '---' found.")

    def _is_relative_path(self, value):
        """
        Helper method to check if a string is a relative file path.
        """
        # Check if the string is a relative file path (i.e., does not start with a drive letter or root '/')
        return not os.path.isabs(value) and (
            value.startswith('./')
            or value.startswith('../')
            or '/' in value
            or '\\' in value
        )

    def purge_main(self, data):
        """
        Removes text-blocks and code-blocks; and returns only the headers of the document to create an outline.

        Parameters:
            data (str): Input file-string (text data) containing codeblocks to process.

        Returns:
            str: Processed file-string with all contents besides section headers removed.
        """
        lines = data.split("\n")
        in_front_matter = False
        in_code_block = False
        rebuild = []

        for i, line in enumerate(lines):
            trimmed = line.strip()

            # Detect the start of the front matter section
            if trimmed == "---" and not in_front_matter and i == 0:
                in_front_matter = True
                rebuild.append(line)
                continue

            # Process within front matter
            if in_front_matter:
                rebuild.append(line)
                if trimmed == "---" and i > 0:  # End of front matter
                    in_front_matter = False
                continue

            # Detect the start of a code block in the main content
            if re.match(r"^```\{", trimmed) and not in_code_block:
                in_code_block = True
                continue

            # Inside code block, skip lines until code block closes
            if in_code_block:
                if re.match(r"^```$", trimmed):
                    in_code_block = False
                continue

            # Outside front matter and code blocks
            if not in_front_matter and not in_code_block:
                # Only include lines that are not valid section headers
                if not re.match(r"^(?!#{1,}\s+).*", line):
                    rebuild.append(line)

        return "\n".join(rebuild)

    def process(self, data):
        """
        The module's entry-point executed during 'ProcessingPipeline.Run()'
        """
        data = self.purge_main(data)
        data = self.modify_frontmatter(data)
        return data
