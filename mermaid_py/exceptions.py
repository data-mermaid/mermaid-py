class UnauthorizedClientException(Exception):
    def __init__(self, code: int = None, message: str = None):
        self.message = f"Unauthorized Client -- Attempt Token Refresh"
        if code:
            self.message = f"Response Code: {code}. {self.message}"
        if message:
            self.message = message
        super().__init__(self.message)


class InvalidResourceException(Exception):
    def __init__(self, resource: str, code: int = None, message: str = None):
        self.message = f"Invalid Resource: {resource}"
        if code:
            self.message = f"Response Code: {code}. {self.message}"
        if message:
            self.message = message
        super().__init__(self.message)


class InvalidProjectException(Exception):
    def __init__(
        self,
        id: str = None,
        name: str = None,
    ):
        self.message = f"Invalid Project "
        if id and name:
            self.message = f"{self.message} -- id: {id} name: {name}"
        elif id:
            self.message = f"{self.message} -- id: {id}"
        elif name:
            self.message = f"{self.message} -- name: {name}"
        super().__init__(self.message)
