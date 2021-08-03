import typing


class NotFoundError(BaseException):
    def __init__(self, error: typing.Optional[str] = None):
        self.error = error
