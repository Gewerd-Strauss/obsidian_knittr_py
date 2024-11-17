from .processing_module_runner import BaseModule
import re
import yaml


class ProcessInvalidQuartoFrontmatterFields(BaseModule):
    """
    Documentation for 'ProcessInvalidQuartoFrontmatterFields'
    """

    def __init__(
        self,
        name="ProcessInvalidQuartoFrontmatterFields",
        config=None,
        log_directory=None,
        past_module_instance=None,
        past_module_method_instance=None,
        log_file=None,
    ):
        super().__init__(
            name,
            config=config,
            log_directory=log_directory,
            past_module_instance=past_module_instance,
            past_module_method_instance=past_module_method_instance,
            log_file=log_file,
        )
        # Get erroneous_keys as a dictionary from config, e.g., {"aliases": []}
        self.erroneous_keys = self.get_config("erroneous_keys", default={})

    def process(self, input_str):
        """
        Fix invalid frontmatter fields by replacing 'null' values for specified keys with their configured replacement.

        Parameters:
            input_str (str): Input text input_str containing YAML frontmatter to process.

        Returns:
            str: Processed input_str with 'null' values replaced by specified replacements for each key in frontmatter.
        """
        lines = input_str.splitlines()
        in_frontmatter = False
        result_lines = []

        for i, line in enumerate(lines):
            trimmed = line.strip()

            # Detect start or end of frontmatter section
            if trimmed == "---" and not in_frontmatter and i == 0:
                in_frontmatter = True
            elif trimmed == "---" and in_frontmatter and i > 0:
                in_frontmatter = False

            # Process within frontmatter
            if in_frontmatter:
                for key, replacement_value in self.erroneous_keys.items():
                    # Look for `key: null` pattern and replace with `key: <replacement_value>`
                    pattern = rf'^{key}:\s*"*null"*\s*'
                    # pattern = rf"^{key}:\s*null\s*$"
                    if re.match(pattern, trimmed):
                        line = f"{key}: {replacement_value}"
                        break
            result_lines.append(line)

        # Rebuild the entire file content as a single string
        return "\n".join(result_lines)


class EnforceLinebreaksOnQuartoBlocks(BaseModule):
    """
    Documentation for 'EnforceLinebreaksOnQuartoBlocks'
    """

    def __init__(
        self,
        name="EnforceLinebreaksOnQuartoBlocks",
        config=None,
        log_directory=None,
        past_module_instance=None,
        past_module_method_instance=None,
        log_file=None,
    ):
        super().__init__(
            name,
            config=config,
            log_directory=log_directory,
            past_module_instance=past_module_instance,
            past_module_method_instance=past_module_method_instance,
            log_file=log_file,
        )

    def process(self, input_str):
        """Process the text by enforcing line breaks around headers and code blocks."""
        lines = input_str.splitlines()
        rebuild = []
        inside_code_block = False

        for idx, line in enumerate(lines):
            trimmed_line = line.strip()

            # Detect the start of a code block (``` or ```{)
            if re.match(r"^```", trimmed_line):
                if inside_code_block:
                    # We're at the end of a code block, add a newline after it
                    rebuild.append(line + "\n")
                    inside_code_block = False
                else:
                    # Beginning of a code block, add a newline before it
                    rebuild.append("\n" + line)
                    inside_code_block = True
            elif inside_code_block:
                # Skip lines inside a code block
                rebuild.append(line)
            elif re.match(r"^#+\s+.*", trimmed_line):
                # It's a header, add a newline before and after the header
                rebuild.append("\n" + line + "\n")
            else:
                # Otherwise, just append the line
                rebuild.append(line)

        return '\n'.join(rebuild)


class EnforceMinimalLinebreaks(BaseModule):
    """
    Documentation for 'EnforceMinimalLinebreaks'
    """

    def __init__(
        self,
        name="EnforceMinimalLinebreaks",
        config=None,
        log_directory=None,
        past_module_instance=None,
        past_module_method_instance=None,
        log_file=None,
    ):
        super().__init__(
            name,
            config=config,
            log_directory=log_directory,
            past_module_instance=past_module_instance,
            past_module_method_instance=past_module_method_instance,
            log_file=log_file,
        )

    def enforce_max_newlines(self, input_str):
        """Helper function to add empty lines before/after headers and code blocks."""
        # Regular expression patterns to match code blocks and LaTeX environments
        code_block_pattern = r"(```.*?```|`{3}[\s\S]*?`{3})"  # Non-greedy match for code blocks (``` ... ```)
        latex_pattern = (
            r"(\$\$.*?\$\$)"  # Match LaTeX environments: $$ ... $$ or \[ ... \]
        )

        # Replace multiple newlines with exactly two newlines, but respect code blocks and LaTeX environments
        def replace_newlines_inside_match(match):
            # Inside code blocks or LaTeX environments, just return the match as is
            return match.group(0)

        # Replace multiple newlines in normal text, keeping LaTeX and code blocks intact
        def replace_newlines_outside_matches(text):
            # Replace multiple newlines with exactly two newlines in the non-matched sections
            return re.sub(r"\n{3,}", "\n\n", text)

        # Step 1: Replace code blocks and LaTeX environments with placeholders so they are not modified
        input_str = re.sub(code_block_pattern, replace_newlines_inside_match, input_str)
        # input_str = re.sub(latex_pattern, replace_newlines_inside_match, input_str)

        # Step 2: Apply the newline replacement on the non-matching (normal) text
        input_str = replace_newlines_outside_matches(input_str)

        return input_str

    def process(self, input_str):
        """Process the text by enforcing line breaks around headers and code blocks."""
        input_str = self.enforce_max_newlines(input_str)
        return input_str


class ProcessEquationReferences(BaseModule):
    """
    Documentation for 'ProcessEquationReferences'
    """

    def __init__(
        self,
        name="ProcessEquationReferences",
        config=None,
        log_directory=None,
        past_module_instance=None,
        past_module_method_instance=None,
        log_file=None,
    ):
        super().__init__(
            name,
            config=config,
            log_directory=log_directory,
            past_module_instance=past_module_instance,
            past_module_method_instance=past_module_method_instance,
            log_file=log_file,
        )

    def process(self, input_str):
        """
        Moves equation references outside of LaTeX blocks and appends them at the end of the respective blocks.
        The reference format is changed to `{#eq:<label>}`.

        Args:
            input_str (str): The input markdown string containing LaTeX blocks with references.

        Returns:
            str: The modified string with equation references moved and reformatted.
        """
        # Regex pattern to match LaTeX blocks and capture the equation reference
        latex_block_pattern = r"(\$\$.*?)(\()(\\#eq:.*?)(\))(.*?\$\$)"
        result_str = input_str

        # Find all LaTeX blocks with equation references inside
        matches = re.finditer(latex_block_pattern, input_str, re.DOTALL)

        for match in matches:
            latex_block = match.group(1)
            opening_brace = match.group(2)
            equation_reference = match.group(
                3
            ).strip()  # Extract reference like \#eq:fieldcapacityequation1
            closing_brace = match.group(4)
            remaining_latex = match.group(5)

            # Remove the equation reference from the LaTeX block
            latex_block_clean = latex_block.replace(equation_reference, "").strip()

            # merge the block-portions
            latex_block_combined = latex_block_clean + remaining_latex

            # Format the reference to be appended after the block
            label = equation_reference.replace(
                "\\#", "{#"
            ).strip()  # Remove the backslash and hash
            label = label.replace("#eq:", "#eq-")
            formatted_reference = f"$$ {label}" + "}"

            total_block = latex_block_combined + formatted_reference

            total_block = total_block.replace(
                "$$" + formatted_reference, formatted_reference
            )
            # Replace the old LaTeX block in the original string with the clean one
            result_str = result_str.replace(
                match.group(0), "\n\n" + total_block + "\n\n"
            )

        return result_str


class ConvertBookdownToQuartoReferencing(BaseModule):
    """
    Documentation for 'ConvertBookdownToQuartoReferencing'
    """

    def __init__(
        self,
        name="ConvertBookdownToQuartoReferencing",
        config=None,
        log_directory=None,
        past_module_instance=None,
        past_module_method_instance=None,
        log_file=None,
    ):
        super().__init__(
            name,
            config=config,
            log_directory=log_directory,
            past_module_instance=past_module_instance,
            past_module_method_instance=past_module_method_instance,
            log_file=log_file,
        )
        # Retrieve the flag for removing Quarto reference types from cross-references
        self.quarto_strip_reference_prefixes = self.get_config(
            "quarto_strip_reference_prefixes", False
        )

    def process(self, input_str):
        """
        Convert Bookdown-style references to Quarto-style references and optionally remove Quarto reference types from cross-references.

        Parameters:
            input_str (str): Input string containing the markdown with Bookdown references.

        Returns:
            str: The modified string with Bookdown references converted to Quarto references.
        """
        needle = r"\\@ref\((?P<Type>\w*):(?P<Label>[^)]*)\)"
        matches = re.finditer(needle, input_str)

        for match in matches:
            full_match = match.group(0)
            type_ = match.group("Type")
            label = match.group("Label")
            lbl = label  # Just to match the AHK variable names (although 'lbl' is unused in AHK)

            # Adjust label based on the reference type
            if type_ == "tab":
                if "tbl-" not in label:
                    label = "tbl-" + label
                type_ = "tbl"
            else:
                if f"{type_}-" not in label:
                    label = f"{type_}-{label}"

            # Replace the reference in the string
            if self.quarto_strip_reference_prefixes:
                input_str = input_str.replace(full_match, f"[-@{label}]")
            else:
                input_str = input_str.replace(full_match, f"@{label}")

            # Replace table references (e.g., 'tbl-WateringMethodTables' → 'tbl-WateringMethodTables')
            input_str = input_str.replace(f"r {lbl}", f"r {label}")

        return input_str


class EnforceFrontmatterYAML(BaseModule):
    """
    Module extracts the frontmatter-yaml from the file-string and formats it via

    ```py
    yaml.dump(
        yaml.safe_load(frontmatter_str),
        default_flow_style=False,
        allow_unicode=True
        )
    ```

    to ensure it conforms to standard frontmatter formatting rules.
    """

    def __init__(
        self,
        name="EnforceFrontmatterYAML",
        config=None,
        log_directory=None,
        past_module_instance=None,
        past_module_method_instance=None,
        log_file=None,
    ):
        super().__init__(
            name,
            config=config,
            log_directory=log_directory,
            past_module_instance=past_module_instance,
            past_module_method_instance=past_module_method_instance,
            log_file=log_file,
        )

    def process(self, input_str: str):
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
            new_frontmatter_str = yaml.dump(
                frontmatter_dict, default_flow_style=False, allow_unicode=True
            )

            # if the string begins with another `---`, strip that away for safety.
            if markdown_content[0:3] == "---":
                markdown_content = markdown_content[3:]
            # Ensure proper Quarto frontmatter format by adding the --- delimiters
            new_input_str = f'---\n{new_frontmatter_str}---\n{markdown_content}'

            return new_input_str
        else:
            raise ValueError("The input-string does not contain valid frontmatter.")
