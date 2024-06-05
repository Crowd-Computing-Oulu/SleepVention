from datetime import datetime


class LoginResponseSchema:
    """
        Schema representing the response to a login request.

        Inherits from BaseSchema.

        :param user_id: Unique identifier for the user.
        :param token: Authentication token.
        :param expiry: Date and time when the token expires.
    """
    user_id: int
    token: str
    expiry: datetime

    class Config:
        from_attributes = True
