class CustomValidationError(Exception):
    """
    This is the custom exception class for validation error. Raise this exception when request
    have invalid data.
    """

    def __init__(self, message):
        super().__init__(message)
        self.status_code = 400


class UnauthorizedUserError(Exception):
    """
    This is the custom exception class to raise unauthorized user error
    """

    def __init__(self):
        super().__init__("Unauthorized user")
        self.status_code = 401


class RecordNotFoundError(Exception):
    """
    This is the custom exception class to raise an error is record not found.
    """

    def __init__(self, error_msg=None):
        super().__init__(error_msg or "Record not found!!!")
        self.status_code = 404


class PathNotFoundError(Exception):
    """
    This is the custom exception class to raise an error is record not found.
    """

    def __init__(self, method: str):
        super().__init__(
            f"The requested URL with method type '{method}' was not found on the server. If you entered "
            f"the URL manually please check your spelling and method and try again."
        )
        self.status_code = 404


class DuplicateEntry(Exception):
    """
    This is the custom exception class to raise an error for conflict
    """

    def __init__(self, error_msg=None):
        super().__init__(error_msg or "Duplicate Entry !!!")
        self.status_code = 409
