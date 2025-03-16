
class RuleError(Exception):
    stop_execution: bool

    def __init__(self, message, *args, stop_execution=False):
        super().__init__(message, *args)
        self.stop_execution = stop_execution
