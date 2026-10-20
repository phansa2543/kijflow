class PasswordRejected(ValueError):
    pass

class ScreeningUnavailable(ValueError):
    pass

class RegistrationConflict(Exception):
    pass

class RegistrationRateLimited(Exception):
    def __init__(self, retry_after_seconds: int):
        if retry_after_seconds < 1:
            raise ValueError("Invalid retry-after value")

        self.retry_after_seconds = retry_after_seconds
        super().__init__("Registration rate limit exceeded")


class RegistrationLimiterUnavailable(Exception):
    pass