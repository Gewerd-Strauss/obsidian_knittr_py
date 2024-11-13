from .processing_module_runner import BaseModule
import re


class ProcessInvalidQuartoFrontmatterFields(BaseModule):

    def __init__(
        self,
        name="ProcessInvalidQuartoFrontmatterFields",
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
    def __init__(
        self,
        name="EnforceLinebreaksOnQuartoBlocks",
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
