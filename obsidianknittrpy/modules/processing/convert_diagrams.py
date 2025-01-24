from .processing_module_runner import BaseModule


class ProcessDiagramCodeblocks(BaseModule):
    """
    This module ensures that code block languages/identifiers in Markdown files are wrapped in curly braces.

    ## Example

    Given the following Markdown document:

    ````md
    ---
    format: docx
    title: ProcessDiagramCodeblocks_Example
    ---

    ```mermaid
    flowchart LR
    Start --> Stop
    ```

    ```mermaid
    sequenceDiagram
    participant Alice
    participant Bob
    Alice->>John: Hello John, how are you?
    loop Healthcheck
        John->>John: Fight against hypochondria
    end
    Note right of John: Rational thoughts <br/>prevail!
    John-->>Alice: Great!
    John->>Bob: How about you?
    Bob-->>John: Jolly good!
    ```

    ````

    The module will transform it into:

    ````md
    ---
    format: docx
    title: ProcessDiagramCodeblocks_Example
    ---

    ```{mermaid}
    flowchart LR
    Start --> Stop
    ```

    ```{mermaid}
    sequenceDiagram
    participant Alice
    participant Bob
    Alice->>John: Hello John, how are you?
    loop Healthcheck
        John->>John: Fight against hypochondria
    end
    Note right of John: Rational thoughts <br/>prevail!
    John-->>Alice: Great!
    John->>Bob: How about you?
    Bob-->>John: Jolly good!
    ```

    ````

    ## Defaults

    By default, the module wraps the following identifiers in curly braces:

    - `mermaid`
    - `dot`

    This ensures that any code block with one of these identifiers will be wrapped in `{}`. For example, the `mermaid` language identifier will be transformed as shown above.

    ## Customization

    The module can be customized to wrap additional identifiers. You can modify the list of supported languages as needed.
    """

    def __init__(
        self,
        name="ProcessDiagramCodeblocks",
        config=None,
        log_directory=None,
        past_module_instance=None,
        past_module_method_instance=None,
        log_file=None,
    ):
        super().__init__(
            name,
            config=config,
            log_directory=log_directory,
            past_module_instance=past_module_instance,
            past_module_method_instance=past_module_method_instance,
            log_file=log_file,
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
