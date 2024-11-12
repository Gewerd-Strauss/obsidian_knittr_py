import logging


class BaseModule:
    def __init__(
        self, name, config=None, log_directory=None, past_module_instance=None
    ):
        """
        Base class for all processing modules.
        :param name: Name of the module
        :param config: Optional dictionary of configurations
        """
        self.name = name
        self.config = config if config else {}
        self.log_directory = log_directory if log_directory else ""
        self.past_module_instance = past_module_instance if past_module_instance else ""

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
        print("DD")
        # os.makedirs(self.log_directory, exist_ok=True)
        self.logger = logging.getLogger(
            self.__class__.__module__ + "." + self.__class__.__qualname__
        )
        self.logger.setLevel(logging.DEBUG if debug else logging.INFO)
        pass

    def log_input(self, input_str):
        """method reserved for logging input-state"""
        self.log_write(input_str=input_str, inOut="input")
        pass

    def log_write(self, input_str, inOut="input"):
        """logs string to file"""
        self.logger.info("Read ")

    def log_output(self, input_str):
        """method reserved for logging outnput-state"""
        pass

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

    def __init__(self, config_file, arguments=None, debug=False, log_directory=None):
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
        try:
            if os.path.exists(config_file):
                with open(config_file, "r") as f:
                    config = yaml.safe_load(f)
        except:
            config = config_file

        self.load_configuration_yaml(config)

    def load_configuration_yaml(self, config):
        """
        Load the configuration from YAML and initialize modules dynamically.
        :param config: YAML-configuration to load
        """

        module_dir = os.path.normpath(os.path.dirname(__file__))

        past_module_instance = ""
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
                    )
                    past_module_instance = module_instance.__module__
                    self.modules.append(module_instance)
                else:
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
        return input_str
