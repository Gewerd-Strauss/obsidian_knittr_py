from .processing_module_runner import BaseModule
import re


class ProcessTags(BaseModule):
    """
    Documentation for 'ProcessTags'
    """

    def process(self, input_str):
        remove_hashtags = self.get_config("remove_hashtags_from_tags")
        contents = input_str

        # Process front matter to handle missing tags
        contents = self.ensure_tags_field(contents)

        if "_obsidian_pattern" in contents:
            tags, orig_tags = self.extract_tags(contents)
            already_replaced = set()

            if not tags:
                # Use the first tag if no tags were extracted
                tag = self.trim_newline(orig_tags[0])
                contents = self.replace_pattern(contents, tag, remove_hashtags)
                already_replaced.add(tag)
            else:
                tags = [self.strip_bullet(tag) for tag in tags]
                tags = self.clean_tags(tags)

                for tag in tags:
                    if tag and tag not in already_replaced:
                        contents = self.replace_pattern(contents, tag, remove_hashtags)
                        already_replaced.add(tag)

                contents = self.rebuild_tags(contents, orig_tags, tags)
                contents = re.sub(r"---\r?\n---", "\n---\n", contents)
                contents = re.sub(r"\r?\n\r?\n", "\n", contents)

            contents = self.replace_unmatched_tags(
                contents, already_replaced, remove_hashtags
            )

        return contents

    def ensure_tags_field(self, contents):
        # Ensures the 'tags' field exists in the frontmatter
        if "tags:" in contents:
            tags_section = contents.split("tags:")[1].splitlines()
            tags = [line.strip() for line in tags_section if line.startswith("- ")]

            # Initialize 'tags' field if no tags are present
            if not tags:
                contents = contents.replace("tags:", "tags: []")
        return contents

    def extract_tags(self, contents):
        tags_section = contents.split("tags:")[1] if "tags:" in contents else ""
        lines = tags_section.splitlines()
        tags, orig_tags = [], []

        for line in lines:
            if line.startswith("- "):
                tags.append(line.strip())
                orig_tags.append(line)
            if line.startswith("---"):
                break

        return tags, "\n".join(orig_tags)

    def strip_bullet(self, tag):
        return tag[2:].strip() if tag.startswith("- ") else tag

    def clean_tags(self, tags):
        clean_tags = []
        end_chars = set(self.get_config("obsidian_tag_end_chars", []))

        for tag in tags:
            for char in end_chars:
                if char in tag:
                    tag = tag.split(char, 1)[0]
            clean_tags.append(tag.strip())

        return clean_tags

    def replace_pattern(self, contents, tag, remove_hashtags):
        needle = f"`{{_obsidian_pattern_tag_{tag}}}`"
        replacement = tag if remove_hashtags else f"#{tag}"
        return contents.replace(needle, replacement)

    def rebuild_tags(self, contents, orig_tags, tags):
        rebuilt_tags = "\n".join(f"- {tag}" for tag in tags if tag)
        return contents.replace(orig_tags, f"\n{rebuilt_tags}\n")

    def replace_unmatched_tags(self, contents, already_replaced, remove_hashtags):
        matches = re.findall(r"\{_obsidian_pattern_tag_(.+?)\}`", contents)

        for tag in matches:
            if tag not in already_replaced:
                replacement = tag if remove_hashtags else f"#{tag}"
                contents = contents.replace(
                    f"``{{_obsidian_pattern_tag_{tag}}}``", replacement
                )

        return contents


class ProcessAbstract(BaseModule):
    """
    Documentation for 'ProcessAbstract'
    """

    def process(self, input_str):
        lines = input_str.splitlines()
        rebuild = []
        abstract_found = False

        for index, line in enumerate(lines):
            # If abstract has been encountered, process the line accordingly
            if abstract_found:
                if line.startswith(" "):
                    rebuild.append(
                        f" {line.lstrip()}"
                    )  # Preserve indentation for lines starting with a space
                else:
                    rebuild.append(
                        f"{line}"
                    )  # Add newline for lines that don't start with a space
            else:
                # If abstract is not found, append the line as is
                if "abstract" in line.lower():
                    rebuild.append(line if index == 0 else f"{line}")
                    abstract_found = True
                else:
                    rebuild.append(line if index == 0 else f"{line}")
                    # rebuild.append(line)
        return "\n".join(rebuild)


class ProcessFrontmatterNulls(BaseModule):
    """
    Module processes the frontmatter section to ensure that a YAML key with value 'null' (unquoted) gets quoted. Should always be run.

    E.g.

    ```md
    ---
    format: docx
    title: ProcessFrontmatterNulls_Example
    alias: null
    ---
    ```

    converts to

    ```md
    ---
    format: docx
    title: ProcessFrontmatterNulls_Example
    alias: "null"
    ---
    ```
    """

    def process(self, input_str):
        lines = input_str.splitlines()
        rebuild = []
        in_front_matter = False

        for idx, line in enumerate(lines):
            trimmed_line = line.strip()

            if "---" in trimmed_line and not in_front_matter and idx == 0:
                # Start of front matter
                in_front_matter = True
            elif "---" in trimmed_line and in_front_matter and idx > 0:
                # End of front matter
                in_front_matter = False
                rebuild.append(line)
            elif in_front_matter:
                # Within the front matter
                # Replace 'null' values with quoted '""null""'
                if re.search(r".+:\s*null\b", line):
                    line = line.replace("null", '"null"')

                # Check if 'tags:' is empty, add empty list if so
                if "tags:" in line and not any(
                    tag_line.startswith("- ") for tag_line in lines[idx + 1 :]
                ):
                    line = "tags: []"

            rebuild.append(line)

        return "\n".join(rebuild)
