from .processing_module_runner import BaseModule
import re


class ProcessInvalidQuartoFrontmatterFields(BaseModule):
    def __init__(self, name="ProcessInvalidQuartoFrontmatterFields", config=None):
        super().__init__(name, config=config)
        # Get erroneous_keys as a dictionary from config, e.g., {"aliases": []}
        self.erroneous_keys = self.get_config("erroneous_keys", default={})

    def process(self, data):
        """
        Fix invalid frontmatter fields by replacing 'null' values for specified keys with their configured replacement.

        Parameters:
            data (str): Input text data containing YAML frontmatter to process.

        Returns:
            str: Processed data with 'null' values replaced by specified replacements for each key in frontmatter.
        """
        lines = data.splitlines()
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
                    pattern = rf"^{key}:\s*null\s*$"
                    if re.match(pattern, trimmed):
                        line = f"{key}: {replacement_value}"
                        break
            result_lines.append(line)

        # Rebuild the entire file content as a single string
        return "\n".join(result_lines)