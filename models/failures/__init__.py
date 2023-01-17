from .__failure import Failure, FailureID

# Create a new exception class that takes a failure as an argument
class CommandException(Exception):
    def __init__(self, failure: Failure):
        self.failure = failure
        super().__init__(failure.message)

    @property
    def failure_id(self) -> FailureID:
        return self.failure.failureID

    @property
    def message(self) -> str:
        return self.failure.message

    def __str__(self) -> str:
        return f'Command Failure - "{self.failure_id.value}"   Message - "{self.message}"'

    def __repr__(self) -> str:
        return f"CommandException({self.failure_id}, \"{self.message}\")"