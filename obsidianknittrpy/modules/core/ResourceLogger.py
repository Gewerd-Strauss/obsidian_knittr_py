import os
import datetime


class ResourceLogger:
    def __init__(self, log_directory=None):
        # if log_directory is not None:
        #     self.log_file = os.path.join(log_directory, "resource_log.txt")
        self.logs_pre_logfile_existance = []
        self.log_file = None
        if log_directory is not None:
            self.log_file = os.path.join(log_directory, "resource_log.txt")

    def add_log_location(self, log_directory=None):
        if log_directory is not None:
            self.log_file = os.path.join(log_directory, "resource_log.txt")

    def log(self, module, action, resource):
        """Logs an action with a timestamp."""
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
