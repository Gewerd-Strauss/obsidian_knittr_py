import atexit
import os
from collections.abc import MutableMapping
from typing import Iterator


class Log(MutableMapping):
    def __init__(self, path, cache):
        print("HI")

    def __new__(cls, path, cache, encoding="utf-8"):
        instance = super(Log, cls).__new__(cls)
        instance.tpl = """
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
        instance.__path = path
        instance.__encoding = encoding
        instance.__cache = False
        instance.auto_write_to_file = True

        # Write initial template to log file
        instance.writeFile_Log(path, instance.tpl, encoding, safe_overwrite=True)

        # Load content for caching
        with open(path, "r", encoding=encoding) as tempfile:
            instance.content = tempfile.read()

        # Keep file pointer open for further operations
        instance.__h = open(path, "w", encoding=encoding)
        instance.Cache(cache)

        # Ensure file is closed on exit
        atexit.register(instance.close)
        return instance

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        key_placeholder = "{" + f"{key}" + "}"
        # Update the in-memory content with the new value
        self.content = self.content.replace(key_placeholder, str(value))

        if self.auto_write_to_file:
            self.write_to_file(self.content)

    def __delitem__(self, key):
        # Remove placeholder replacement
        # key_placeholder = "{" + f"{key}" + "}"
        # self.content = self.content.replace(key_placeholder, "")
        # if self.auto_write_to_file:
        #     self.write_to_file(self.content)
        return 0

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
