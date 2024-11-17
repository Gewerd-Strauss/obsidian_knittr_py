import logging
import shutil
from obsidianknittrpy.modules.core.ResourceLogger import ResourceLogger


class BaseModule:

    def __init__(
        self,
        name,
        config=None,
        log_directory=None,
        past_module_instance=None,
        past_module_method_instance=None,
        log_file=None,
    ):
        """
        Base class for all processing modules.
        :param name: Name of the module
        :param config: Optional dictionary of configurations
        """
        self.name = name
        self.config = config if config else {}
        self.log_directory = log_directory if log_directory else ""
        self.log_directory = os.path.normpath(
            os.path.join(self.log_directory, self.name)
        )

        self.past_module_instance = (
            past_module_instance if past_module_instance else "obsidian-html"
        )

        self.past_module_method_instance = (
            past_module_method_instance if past_module_method_instance else ""
        )
        self.RL = ResourceLogger()
        self.RL.log_file = log_file

    def get_config(self, key, default=None):
        """
        Get a configuration value, falling back to a default if the key is not present.
        :param key: Configuration key
        :param default: Default value if key is missing
        :return: Value from config or default
        """
        return self.config.get(key, default)

    def accept_args(self, **kwargs):
        """
        Accept arguments specific to the module and merge them with the existing config.
        :param kwargs: Arbitrary keyword arguments
        """
        self.config.update(kwargs)

    def init_log(self, debug):
        """method reserved for initialising the logging directory"""
        self.input_log_file = os.path.normpath(
            os.path.join(self.log_directory, "input.md")
        )
        self.output_log_file = os.path.normpath(
            os.path.join(self.log_directory, "output.md")
        )
        os.makedirs(self.log_directory, exist_ok=True)
        self.logger = logging.getLogger(
            self.__class__.__module__ + "." + self.__class__.__qualname__
        )
        self.logger.setLevel(logging.DEBUG if debug else logging.INFO)
        pass

    def log_input(self, input_str):
        """method reserved for logging input-state"""
        self.logger.info(
            f"Read input file-string provided by {self.past_module_instance}.{self.past_module_method_instance}."
        )
        self.pre_conversion_text = input_str
        self.log_write(input_str=input_str, inOut="input")
        pass

    def log_write(self, input_str, inOut="input", encoding='utf-8'):
        """logs string to file"""
        if inOut == "input":
            with open(self.input_log_file, 'w', encoding=encoding) as file:
                file.write(input_str)
        elif inOut == "output":
            with open(self.output_log_file, 'w', encoding=encoding) as file:
                file.write(input_str)

    def log_output(self, input_str):
        """method reserved for logging outnput-state"""
        if input_str != self.pre_conversion_text:
            self.logger.info("Modified File-string.")
            self.RL.log(
                module=f"{self.__module__}.{self.name}",
                action="modified",
                resource="file_string",
            )
        self.log_write(input_str=input_str, inOut="output")

    def process(self, input_str):
        """
        Process the input markdown string and return the modified string.
        Must be overridden by subclasses.
        :param input_str: Input markdown string
        :return: Processed string
        """
        raise NotImplementedError(
            f"Module {self.name} must implement 'process' method."
        )


import importlib
import os
import yaml


class ProcessingPipeline:
    """
    Main pipeline class responsible for execution processing-modules
    This class gets executed on the immediate output of obsidian-html
    """

    def __init__(
        self, config_file, arguments=None, debug=False, log_directory=None, RL=None
    ):
        """
        Initialize the processing pipeline.
        :param config_file: Path to YAML configuration file
        """
        self.logger = logging.getLogger(
            self.__class__.__module__ + "." + self.__class__.__qualname__
        )
        self.logger.setLevel(logging.DEBUG if debug else logging.INFO)
        self.debug = debug
        self.modules = []
        self.arguments = arguments if arguments else {}
        self.arguments["debug"] = debug
        self.log_directory = log_directory
        self.RL = RL
        if os.path.exists(self.log_directory):
            self.logger.info(f"Removed module-logging-directory {self.log_directory}.")
            self.RL.log(
                self.__class__.__module__ + "." + self.__class__.__qualname__,
                "removed",
                self.log_directory,
            )
            shutil.rmtree(self.log_directory)
        try:
            if os.path.exists(config_file):
                with open(config_file, "r") as f:
                    config = yaml.safe_load(f)
        except:
            config = config_file

        print("\n")
        self.logger.info("Initialising pipeline.")
        self.load_configuration_yaml(config)
        RL.log(
            self.__class__.__module__ + "." + self.__class__.__qualname__,
            "loaded",
            f"module-config from {os.path.normpath(os.path.dirname(__file__))}",
        )
        self.logger.info("Initialised pipeline.")

    def load_configuration_yaml(self, config):
        """
        Load the configuration from YAML and initialize modules dynamically.
        :param config: YAML-configuration to load
        """

        module_dir = os.path.normpath(os.path.dirname(__file__))

        past_module_instance = ""
        past_module_method_instance = ""
        for module_info in config["pipeline"]:
            if module_info["enabled"]:
                # Dynamically load the module by its filename (module_info['name'])
                module_file = f"{module_info['file_name']}.py"
                module_path = os.path.join(module_dir, module_file)

                if os.path.exists(module_path):
                    module_name = f"obsidianknittrpy.modules.processing.{module_info['file_name']}"
                    module = importlib.import_module(module_name)
                    module_class = getattr(module, module_info["module_name"])

                    # Start with the config from module_info
                    module_config = module_info.get("config", {}).copy()

                    # Override with any arguments from self.arguments
                    for key in module_config:
                        if key in self.arguments:
                            module_config[key] = self.arguments[key]

                    # Initialize the module with the merged config
                    module_instance = module_class(
                        module_info["module_name"],
                        config=module_config,
                        log_directory=self.log_directory,
                        past_module_instance=past_module_instance,
                        past_module_method_instance=past_module_method_instance,
                        log_file=self.RL.log_file,
                    )
                    past_module_instance = module_instance.__module__
                    past_module_method_instance = module_instance.name
                    self.RL.log(
                        self.__class__.__module__ + "." + self.__class__.__qualname__,
                        "initiated",
                        f"{module_path} : {module_info["module_name"]}",
                    )
                    self.modules.append(module_instance)
                else:
                    self.RL.log(
                        self.__class__.__module__ + "." + self.__class__.__qualname__,
                        "load_failed",
                        f"{module_dir}.{module_info["module_name"]}",
                    )
                    self.logger.warning(
                        f"Module {module_info['module_name']} not found in {module_dir}"
                    )

    def run(self, input_str):
        """
        Run the processing pipeline, passing the output of one module as the input to the next.
        :param input_str: The initial input string (markdown)
        :return: The final processed string
        """
        for module in self.modules:
            module.init_log(self.debug)
            module.log_input(input_str)
            input_str = module.process(input_str)
            module.log_output(input_str)
        self.logger.debug(f"Processing-pipeline finished conversion.")
        return input_str
