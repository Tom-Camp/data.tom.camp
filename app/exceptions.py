class NotFoundError(Exception):
    def __init__(self, detail: str = "Not found"):
        self.detail = detail


class ConflictError(Exception):
    def __init__(self, detail: str = "Conflict"):
        self.detail = detail
