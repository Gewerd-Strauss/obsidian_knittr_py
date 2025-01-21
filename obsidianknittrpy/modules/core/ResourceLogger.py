import os
import datetime


class ResourceLogger:
    """
    Class is responsible for generating the log-file `output/resource-log.txt` in the application-directory.

    # Log-format

    Principal format of a line:

    ```
    [ISO-timestamp] <module>.<function>   <verb>    <target>
    ```

    Example:
    ```
    [2025-01-21T19:47:59.142734] main   inits   default config

    ```

    Note that its implementation is not absolute and still a work-in-progress.

    # Workflow:

    - the main invoked method `.log()` records a module, its action, and the resource it modified.
    - if actions must be logged before the log-file could be written to disk, they get cached until the file can be written to disk.
      In that case, use `.add_log_location()` to add a log-file's path after the class has been instantiated and cached logging has already occured.
    """

    def __init__(self, log_directory=None):
        """Set up class structure"""
        self.logs_pre_logfile_existance = []
        self.log_file = None
        if log_directory is not None:
            self.log_file = os.path.join(log_directory, "resource_log.txt")

    def add_log_location(self, log_directory=None):
        """
        Associate a class-instance with a log-file's path after the class was instantiated.
        This method will then write currently-cached logs to disk, and all subsequent logs will occur normally.
        """
        if log_directory is not None:
            self.log_file = os.path.join(log_directory, "resource_log.txt")

    def log(self, module, action, resource):
        """Logs an action with a timestamp to the class-instance's log-file."""
        timestamp = datetime.datetime.now().isoformat()
        log_entry = f"[{timestamp}] {module.ljust(100)} {action.ljust(30)} {resource}\n"
        if self.log_file is not None:
            with open(self.log_file, "a", encoding="utf-8") as log:
                if len(self.logs_pre_logfile_existance) > 0:
                    for each_log_entry in self.logs_pre_logfile_existance:
                        log.write(each_log_entry)
                    self.logs_pre_logfile_existance = []
                    log.write(log_entry)
                else:
                    log.write(log_entry)
        else:
            self.logs_pre_logfile_existance.append(log_entry)
