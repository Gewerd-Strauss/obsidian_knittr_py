from collections.abc import MutableMapping
from typing import Iterator
import atexit
import os


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
        old_length = len(self.content)
        key_placeholder = "{" + f"{key}" + "}"

        self.content = self.content.replace(key_placeholder, value)
        new_length = len(self.content)

        if new_length < old_length:
            diff = abs(new_length - old_length)
            self.content += " " * diff

        if hasattr(self, "auto_write_to_file") and not self.auto_write_to_file:
            self.handle()
            return

        self.write(self.content)
        self.handle()

    def __len__(self):
        """not necessary/how to implement"""
        return 0

    def __delitem__(self, k):
        """not implemented: remove items"""
        self[k] = None

    def __iter__(self) -> Iterator:
        return super().__iter__()

    def write_to_file(self, content):
        with open(self.path, "w", encoding=self.encoding) as f:
            f.write(content)

    def cache(self, set_value=""):
        if not set_value:
            return self.cache_enabled
        self.cache_enabled = bool(set_value)

    def toggle_auto_write(self, enable):
        self.auto_write_to_file = bool(enable)

    def close(self):
        if not self.auto_write_to_file:
            self.write(self.content)
        self._Log__h.close()

    def handle(self):
        return self._Log__h

    def write(self, content):
        self._Log__h.write(content)

    def get_total_duration(self, atc1, atc2, key="TotalExecution_Duration"):
        diff = atc2 - atc1
        time_str = self.pretty_tick_count(diff)
        self.set_value(key, time_str)

    def pretty_tick_count(self, time_in_milliseconds):
        elapsed_hours = time_in_milliseconds // 3600000
        elapsed_minutes = (time_in_milliseconds % 3600000) // 60000
        elapsed_seconds = (time_in_milliseconds % 60000) // 1000
        elapsed_milliseconds = time_in_milliseconds % 1000
        return f"{elapsed_hours}h:{elapsed_minutes}m:{elapsed_seconds}s.{elapsed_milliseconds}"

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

    def close(self):
        if hasattr(self, "__h") and not self.__h.closed:
            self.__h.close()

    def Cache(self, cache_value):
        self.__cache = cache_value
