class BaseModule:
    def __init__(self, name, config=None):
        """
        Base class for all processing modules.
        :param name: Name of the module
        :param config: Optional dictionary of configurations
        """
        self.name = name
        self.config = config if config else {}

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

    def log_input(self):
        """method reserved for logging input-state"""
        pass

    def log_output(self):
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
    def __init__(self, config_file, arguments=None, debug=False):
        """
        Initialize the processing pipeline.
        :param config_file: Path to YAML configuration file
        """
        self.debug = debug
        self.modules = []
        self.arguments = arguments if arguments else {}
        self.arguments["debug"] = debug
        self.load_config(config_file)

    def load_config(self, config_file):
        """
        Load the configuration from YAML and initialize modules dynamically.
        :param config_file: Path to YAML configuration file
        """
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)

        module_dir = os.path.normpath(os.path.dirname(__file__))

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
                        module_info["module_name"], config=module_config
                    )
                    self.modules.append(module_instance)
                else:
                    print(
                        f"Module {module_info['module_name']} not found in {module_dir}"
                    )

    def run(self, input_str):
        """
        Run the processing pipeline, passing the output of one module as the input to the next.
        :param input_str: The initial input string (markdown)
        :return: The final processed string
        """
        for module in self.modules:
            module.log_input()
            input_str = module.process(input_str)
            module.log_output()
        return input_str