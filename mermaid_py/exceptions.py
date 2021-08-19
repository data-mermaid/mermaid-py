class UnauthorizedClientException(Exception):
    """Exception class Unauthorized Client request"""

    def __init__(self, message: str = None):
        self.message = "Unauthorized Client -- Attempt Token Refresh"
        if message:
            self.message = message
        super().__init__(self.message)


class InvalidResourceException(Exception):
    """Exception class for handling invalid resource parameters"""

    def __init__(self, resource: str, message: str = None):
        self.message = f"Invalid Resource:{resource}"
        if message:
            self.message = message
        super().__init__(self.message)


class InvalidProjectException(Exception):
    """Exception class for handling invalid resource parameters"""

    def __init__(
        self,
        id: str = None,
        name: str = None,
    ):
        self.message = f"Invalid Project "
        if id and name:
            self.message += f"id:{id} name:{name}"
        elif id:
            self.message += f"id:{id}"
        elif name:
            self.message += f"id:{id} name:{name}"
        super().__init__(self.message)
