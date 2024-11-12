from .processing_module_runner import BaseModule
import re


class ProcessDiagramCodeblocks(BaseModule):

    def __init__(
        self,
        name="ProcessDiagramCodeblocks",
        config=None,
        log_directory=None,
        past_module_instance=None,
        past_module_method_instance=None,
    ):
        super().__init__(name, config=config)
        self.codeblock_langs = self.get_config("codeblock_langs", default={})
        self.log_directory = log_directory if log_directory else ""
        self.past_module_instance = past_module_instance if past_module_instance else ""
        self.past_module_method_instance = (
            past_module_method_instance if past_module_method_instance else ""
        )

    def process(self, data):
        """
        Wrap codeblock-identifiers in curly braces {identifier}.

        Parameters:
            data (str): Input file-string (text data) containing codeblocks to process.

        Returns:
            str: Processed file-string with configured codeblock-identifiers wrapped in curly braces '{}'.
        """
        for each in self.codeblock_langs:
            data = data.replace(f"```{each}", "```{" + each + "}")
        return data
