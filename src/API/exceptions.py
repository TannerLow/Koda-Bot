
class NewUserError(RuntimeError):
    def __init__(self, message: str):
        super().__init__(message)

class LackOfContributionError(RuntimeError):
    def __init__(self, message: str):
        super().__init__(message)
        