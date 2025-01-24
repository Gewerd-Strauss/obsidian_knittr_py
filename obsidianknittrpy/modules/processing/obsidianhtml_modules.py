from .processing_module_runner import BaseModule
import re as re
import urllib.parse
import html


class ConvertImageSRCs(BaseModule):
    """
    Documentation for 'ConvertImageSRCs'
    """

    def process(self, input_str):
        # Regex to match <img> tags with src, width, alt, and title attributes
        regex = r'<img src="(?P<src>.+?)" width="(?P<width>\d*)" alt="(?P<alt>.*?)" title="(?P<title>.*?)" \/>'
        buffer = input_str
        pos = 0

        while True:
            match = re.search(regex, buffer[pos:], re.IGNORECASE)
            if not match:
                break

            # Extract attributes from the match
            src = self.decode_uri_component(match.group("src"))
            width = match.group("width")
            alt = match.group("alt")
            title = match.group("title")

            # Build options string for knitr::include_graphics
            options = []
            if width:
                options.append(f"out.width='{width}'")
            if alt:
                options.append(f"fig.cap='{self.clean(alt)}'")
            if title:
                options.append(f"fig.title='{self.clean(title)}'")
            options_str = ", ".join(options)

            # Adjust src if it contains "../"
            if "../" in src:
                src = src.replace("../", "")

            # Create the template for QMD (Quarto markdown) format
            tpl = (
                f"```{{r, echo=FALSE, {options_str}}}\n"
                f"knitr::include_graphics('{src}')\n"
                f"```"
            )

            # Replace the matched HTML img tag with the new QMD block
            buffer = buffer[: pos + match.start()] + tpl + buffer[pos + match.end() :]
            pos += len(tpl)

        # Additional cleanup to remove figure tags and captions if necessary
        buffer = re.sub(r"<figure>|</figure>", "", buffer)
        buffer = re.sub(r"<figcaption>.*?</figcaption>", "", buffer)

        return buffer

    def clean(self, text):
        """
        Clean text by decoding HTML entities and escaping single quotes.
        """
        decoded_text = self.decode_html_entities(text)
        return decoded_text.replace("'", "\\'")

    def decode_uri_component(self, text):
        """
        Decode URI components, converting encoded characters like %20 back to their original form.
        """
        return urllib.parse.unquote(text)

    def decode_html_entities(self, text):
        """
        Decode common HTML entities in the text, such as &amp; -> &, &lt; -> <, etc.
        """

        return html.unescape(text)


class RemoveObsidianHTMLIncludeErrors(BaseModule):
    """
    Documentation for 'RemoveObsidianHTMLIncludeErrors'
    """

    def __init__(
        self,
        name="RemoveObsidianHTMLIncludeErrors",
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
        # Get error_needles as a dictionary from config, e.g., {"aliases": []}
        self.error_needles = self.get_config("error_needles", default={})
        # Compile each pattern
        self.compiled_error_needles = [
            re.compile(needle[2:-2]) for needle in self.error_needles
        ]

    def process(self, input_str):
        for regex in self.compiled_error_needles:
            input_str = re.sub(
                pattern=regex, repl="", string=input_str
            )  # Remove all matches (substitute with an empty string)
        return input_str
