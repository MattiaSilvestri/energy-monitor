"""Define custom exceptions"""

class BrowserNotFound(Exception):
    """Raised when Chrome or Firefox are not found"""

    message = 'Google Chrome or Firefox not found, please install either of them'
    def __init__(self, message=message) -> None:
        self.message = message
        super().__init__(self.message)
