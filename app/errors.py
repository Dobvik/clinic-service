"""Ошибки предметной области без зависимости от HTTP и HTML."""


class NotFoundError(LookupError):
    """Запрошенная сущность не существует."""


class ConflictError(ValueError):
    """Операция противоречит текущему состоянию данных."""
