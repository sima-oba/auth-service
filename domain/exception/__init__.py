class AuthenticationError(Exception):
    def __init__(self, message: str = None):
        super().__init__(message or 'Invalid user credentials')


class AuthorizationError(Exception):
    def __init__(self, message: str = None):
        super().__init__(message or 'Unauthorized')


class UserError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class UserAlreadyActiveError(Exception):
    def __init__(self, doc: str):
        super().__init__(f'User with doc {doc} is already active')


class UserNotFound(Exception):
    def __init__(self, doc: str):
        super().__init__(f'User with doc {doc} was not found')


class RoleError(Exception):
    def __init__(self, message):
        super().__init__(message)


class GroupError(Exception):
    def __init__(self, message):
        super().__init__(message)


class UnexpectedError(Exception):
    def __init__(self, message: str = None):
        super().__init__(message or 'Unexpected error')
