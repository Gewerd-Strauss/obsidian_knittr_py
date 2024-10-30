import atexit
import os
from collections.abc import MutableMapping
from typing import Iterator


class Log(MutableMapping):

    def __init__(self, path, cache, encoding="utf-8"):
        self.tpl = """
___________________________________________________
Overview:

Manuscript                : {manuscriptname}
Used Verb                 : {UsedVerb}
OHTML - Version           : {obsidianhtml_version}
Used Personal Fork        : {bUseOwnOHTMLFork}
ObsidianKnitr - Version   : {ObsidianKnittr_Version}
Quarto - Version          : {Quarto_Version}

___________________________________________________
Timings:

ObsidianHTML              > {ObsidianHTML_Start}
ObsidianHTML              < {ObsidianHTML_End}
                                         {ObsidianHTML_Duration}
intermediary Processing   > {Intermediary_Start}
intermediary Processing   < {Intermediary_End}
                                         {Intermediary_Duration}
Compilation               > {Compilation_Start}
Compilation               < {Compilation_End}
                                         {Compilation_Duration}

Total (not ms-precise)                   {TotalExecution_Duration}
Total + Startup_AHK (not ms-precise)     {TOTAL_COUNT}

___________________________________________________
Script Execution Settings:

ObsidianKnittr:
ObsidianKnittr - Version  : {ObsidianKnittr_Version}
Output - Formats          : {formats}
Keep Filename             : {bKeepFilename}
Stripped '#' from Tags    : {bRemoveHashTagFromTags}

ObsidianHTML:
OHTML - Version           : {obsidianhtml_version}
Used Verb                 : {UsedVerb}
Used Personal Fork        : {bUseOwnOHTMLFork}
Verbosity                 : {bVerboseCheckbox}
Stripped OHTML - Errors   : {bRemoveObsidianHTMLErrors}
Stripped Local MD-Links   : {bStripLocalMarkdownLinks}
Vault Limited             : {bRestrictOHTMLScope}

RMD:
Execute R-Script          : {bRendertoOutputs}

QMD: 
Quarto - Version          : {Quarto_Version}
Strip Type from Crossrefs : {bRemoveQuartoReferenceTypesFromCrossrefs}

___________________________________________________
Fed OHTML - Config:

{configfile_contents}

___________________________________________________
RMarkdown Document Settings:

{DocumentSettings}

___________________________________________________
Paths:
manuscriptlocation        : {manuscriptpath}
Vault limited to childs of: {temporaryVaultpath}
Vault-Limiter removed     : {temporaryVaultpathRemoved}
Output Folder             : {output_path}
Raw Input Copy            : {rawInputcopyLocation}
ObsidianHTML - Path       : {obsidianHTML_path}
Config - Template         : {configtemplate_path}
ObsidianHTMLCopy Dir      : {ObsidianHTMLCopyDir}
ObsidianHTMLWorking Dir   : {ObsidianHTMLWorkDir}
ObsidianHTMLOutputPath    : {ObsidianHTMLOutputPath}
___________________________________________________
OHTML - StdStreams:
Issued Command            : {ObsidianHTMLCMD}
stdOut                    : {ObsidianHTMLstdOut}
___________________________________________________
R - StdStreams:
Issued Command            : {RCMD}
Working Directory         : {RWD}
stdOut                    : {Rdata_out}
___________________________________________________
OK - Errorlog:
{Errormessage}
"""
        # Store initial template as a blank copy
        self.original_tpl = self.tpl
        self.__path = path
        self.__encoding = encoding
        self.__cache = False
        self.auto_write_to_file = True

        # Initialize storage to track populated keys
        self.storage_dict = {}

        # Write initial template to log file
        self.writeFile_Log(path, self.tpl, encoding, safe_overwrite=True)

        # Load content for caching and initialize with template content
        with open(path, "r", encoding=encoding) as tempfile:
            self.content = tempfile.read()

        self.__h = open(path, "w", encoding=encoding)
        self.Cache(cache)

        atexit.register(self.close)
        # return self

    def __new__(cls, path, cache, encoding="utf-8"):
        instance = super(Log, cls).__new__(cls)
        return instance

    def __getitem__(self, key):
        if key not in self.storage_dict:
            raise ValueError(
                f"key '{key}' has not been inserted into the log-file."
                f"The given key has not been populated so far, and thus could not be retrieved."
            )
        else:
            return self.storage_dict[key]

    def __setitem__(self, key, value):
        key_placeholder = "{" + f"{key}" + "}"

        self.storage_dict[key] = str(value)
        if key_placeholder in self.content:
            # If key placeholder is still in the template, replace it in `content`
            self.content = self.content.replace(key_placeholder, str(value))
        else:
            # Key was previously populated: update in storage, then re-populate
            self.tpl = self.original_tpl  # Reset template content
            self.content = self.tpl  # Refresh content with a blank template
            for k, v in self.storage_dict.items():
                self.content = self.content.replace("{" + f"{k}" + "}", v)

        # Optionally write to file if auto-write is enabled
        if self.auto_write_to_file:
            self.write_to_file(self.content)

    def __delitem__(self, key):
        """Remove key-value from log by removing it from storage, then rebuilding the log."""
        self.storage_dict.pop(key)
        self.tpl = self.original_tpl  # Reset template content
        self.content = self.tpl  # Refresh content with a blank template
        for k, v in self.storage_dict.items():
            self.content = self.content.replace("{" + f"{k}" + "}", v)

    def __iter__(self) -> Iterator:
        return iter(vars(self))

    def __len__(self):
        return len(vars(self))

    def write_to_file(self, content):
        # Overwrite the file from start
        with open(self.__path, "w", encoding=self.__encoding) as f:
            f.write(content)

    def toggle_auto_write(self, enable):
        # Handle toggle for auto-write functionality
        if enable and not self.auto_write_to_file:
            # Write current cache to file upon enabling auto-write
            self.write_to_file(self.content)
        self.auto_write_to_file = bool(enable)

    def close(self):
        # Ensure the latest content is written upon exit
        if not self.auto_write_to_file:
            self.write_to_file(self.content)

    def Cache(self, cache_value):
        self.__cache = cache_value

    def writeFile_Log(
        self, path, content, encoding="utf-8", flags="w", safe_overwrite=False
    ):
        if safe_overwrite:
            # Check if the file exists and delete it if it does
            if os.path.exists(path):
                os.remove(path)
            # Now write the file with exclusive creation
            with open(path, "x", encoding=encoding) as file:
                file.write(content)
        else:
            # Write file as usual with specified flags
            with open(path, flags, encoding=encoding) as file:
                file.write(content)
