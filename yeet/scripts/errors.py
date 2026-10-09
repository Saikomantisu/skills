"""The one exception the CLI turns into an error message and exit code."""

# Exit codes
ERROR = 1
EXISTS = 3   # deploy: the name is already one of your sites (use --overwrite)
TAKEN = 4    # deploy: someone else has the name; delete: not one of your sites
UNSAFE = 5   # the folder looks unsafe to publish; nothing was uploaded


class Fail(Exception):
    def __init__(self, message, code=ERROR):
        super().__init__(message)
        self.code = code
