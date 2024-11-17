import os
import ast
import shutil
import logging
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from obsidianknittrpy.modules.core.ConfigurationHandler import ConfigurationHandler


class ModuleDocExtractor:
    def __init__(
        self,
        source_directory,
        documentation_output_directory,
        include_method_docs=False,
        log_level="INFO",
        pipeline=None,
    ):
        # Set up logger with the desired format
        self.logger = logging.getLogger("ModuleDocExtractor")
        log_format = logging.Formatter(
            "%(levelname)s:%(name)s.%(funcName)s: %(message)s"
        )
        self.pipeline = pipeline
        handler = logging.StreamHandler()
        handler.setFormatter(log_format)
        self.logger.addHandler(handler)
        self.logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        self.source_directory = source_directory
        self.documentation_output_directory = documentation_output_directory
        if os.path.exists(self.documentation_output_directory):
            shutil.rmtree(self.documentation_output_directory)
        os.makedirs(self.documentation_output_directory, exist_ok=True)
        self.include_method_docs = include_method_docs

    def run(self):
        for root, _, files in os.walk(self.source_directory):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    with open(file_path, "r", encoding="utf-8") as f:
                        source_code = f.read()
                    self.process_file(file_path, source_code)

    def process_file(self, file_path, source_code):
        tree = ast.parse(source_code, filename=file_path)
        classes = [node for node in tree.body if isinstance(node, ast.ClassDef)]

        for class_node in classes:
            if self.is_base_module_subclass(class_node):
                docstring = ast.get_docstring(class_node)
                for module in self.pipeline["pipeline"]:
                    if module["module_name"] == class_node.name:
                        module_config = module["config"]
                        break
                    else:
                        continue
                methods_docstrings = (
                    self.extract_method_docstrings(class_node)
                    if self.include_method_docs
                    else []
                )
                self.write_markdown_doc(
                    file_path,
                    class_node.name,
                    docstring,
                    methods_docstrings,
                    module,
                )

    def is_base_module_subclass(self, class_node):
        # Check if any base class of the class inherits from BaseModule
        return any(
            base.id == "BaseModule"
            for base in class_node.bases
            if isinstance(base, ast.Name)
        )

    def extract_method_docstrings(self, class_node):
        # Collect docstrings for each method if they exist
        methods_docs = []
        for item in class_node.body:
            if isinstance(item, ast.FunctionDef):
                method_docstring = ast.get_docstring(item)
                if method_docstring:
                    methods_docs.append((item.name, method_docstring))
        return methods_docs

    #     def write_markdown_doc(
    #         self, file_path, class_name, class_docstring, methods_docstrings
    #     ):
    #         # Create directory structure in documentation_output_directory based on source file location
    #         relative_path = os.path.relpath(file_path, self.source_directory)
    #         relative_dir = os.path.dirname(relative_path)
    #         output_dir = os.path.join(self.documentation_output_directory, relative_dir)
    #         os.makedirs(output_dir, exist_ok=True)

    #         # Define the output path based on the class name
    #         output_path = os.path.join(output_dir, f"{class_name}.md")

    #         # Build markdown content with template
    #         methods_section = "\n".join(
    #             f"### `{method_name}`\n\n{docstring}\n"
    #             for method_name, docstring in methods_docstrings
    #         )

    #         template = f"""
    # ---
    # name: {class_name}
    # tags:
    # - documentation/modules/processing
    # ---

    # {class_docstring or "No class docstring provided."}

    # ## Methods

    # {methods_section if methods_docstrings else "No methods documented."}
    # """
    #         self.logger.info(f"Generating Documentation for module {class_name}")
    #         # Write the template content to the markdown file
    #         with open(output_path, "w", encoding="utf-8") as md_file:
    #             md_file.write(template.strip())
    def write_markdown_doc(
        self, file_path, class_name, class_docstring, methods_docstrings, module_config
    ):
        # Create directory structure in documentation_output_directory based on source file location
        relative_path = os.path.relpath(file_path, self.source_directory)
        relative_dir = os.path.dirname(relative_path)
        output_dir = os.path.join(self.documentation_output_directory, relative_dir)
        os.makedirs(output_dir, exist_ok=True)

        # Define the output path based on the class name
        output_path = os.path.join(output_dir, f"{class_name}.md")

        # Build markdown content with template for configuration section
        config_section = self.generate_configuration_section(module_config)

        methods_section = "\n".join(
            f"### `{method_name}`\n\n{docstring}\n"
            for method_name, docstring in methods_docstrings
        )

        template = f"""
---
name: {class_name}
tags:
- documentation/modules/processing
---

{class_docstring or "No class docstring provided."}

## Configuration

{config_section}

## Methods

{methods_section if methods_docstrings else "No methods documented."}
    """
        self.logger.info(f"Generating Documentation for module {class_name}")

        # Write the template content to the markdown file
        with open(output_path, "w", encoding="utf-8") as md_file:
            md_file.write(template.strip())

    def generate_configuration_section(self, module_config):
        """Generates a configuration section for documentation."""
        config_entries = module_config.get("config", {})
        enabled_state = module_config.get("enabled", False)

        if not config_entries and not enabled_state:
            return "No configuration required."

        config_lines = []

        # Document each config key and its default value
        if config_entries:
            config_lines.append("### Configuration Parameters\n")
            for key, value in config_entries.items():
                config_lines.append(f"- **{key}**: Default value `{value}`")

        # Document the enabled state
        config_lines.append("\n### Enabled State\n")
        config_lines.append(
            f"- **Enabled by default**: {'Yes' if enabled_state else 'No'}"
        )

        return "\n".join(config_lines)


if __name__ == "__main__":
    source_directory = os.path.abspath(
        os.path.normpath(r"obsidianknittrpy\\modules\\processing")
    )
    documentation_output_directory = os.path.abspath(
        os.path.normpath(r"dev\\docs\\documentation\\processing-modules")
    )
    include_method_docs = True  # Set to True if you want method docstrings as well
    CH = ConfigurationHandler(last_run_path=None, loglevel="INFO", is_gui=False)
    CH.apply_defaults()
    pipeline = CH.get_config("pipeline")
    extractor = ModuleDocExtractor(
        source_directory=source_directory,
        documentation_output_directory=documentation_output_directory,
        include_method_docs=include_method_docs,
        pipeline=pipeline,
    )
    extractor.run()
