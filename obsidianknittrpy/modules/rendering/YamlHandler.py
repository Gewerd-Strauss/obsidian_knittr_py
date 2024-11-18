import yaml


class YamlHandler:
    """
    Handles YAML serialization with custom options for Quarto rendering configurations.
    """

    @staticmethod
    def sanitize_parameters(parameters):
        """
        Sanitizes parameters by removing unnecessary quotes and converting certain string values
        to appropriate types (e.g., booleans, numbers).

        :param parameters: The dictionary of parameters to sanitize.
        :return: Sanitized dictionary with cleaned-up values.
        """
        sanitized = {}
        for key, value in parameters.items():
            if isinstance(value, str):
                clean_value = value.strip('"')
                if clean_value.lower() == 'true':
                    sanitized[key] = True
                elif clean_value.lower() == 'false':
                    sanitized[key] = False
                elif clean_value.isdigit():
                    sanitized[key] = int(clean_value)
                elif clean_value.lower() == '[]':
                    # fix `pdf-engine-opt: '[]'` >  `pdf-engine-opt: []`
                    sanitized[key] = []
                else:
                    sanitized[key] = clean_value
            else:
                sanitized[key] = value
        return sanitized

    @staticmethod
    def clean_yaml_dump(data, file_path):
        """
        Dumps YAML data to file without unnecessary quotes around booleans, numbers, and other values.

        :param data: The dictionary to be dumped to YAML.
        :param file_path: The path where the YAML file should be saved.
        """
        sanitized_data = YamlHandler.sanitize_parameters(data)
        with open(file_path, "w") as yaml_file:
            yaml.dump(sanitized_data, yaml_file, default_flow_style=False)
