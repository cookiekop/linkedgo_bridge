class APIREQUESTError(Exception):
    """The cloud rejected a request or did not confirm its result."""


class DeviceOfflineError(APIREQUESTError):
    """The cloud cannot reach the controller."""
