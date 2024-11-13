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
        super().__init__(
            name,
            config=config,
            log_directory=log_directory,
            past_module_instance=past_module_instance,
            past_module_method_instance=past_module_method_instance,
        )
        self.codeblock_langs = self.get_config("codeblock_langs", default={})

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
