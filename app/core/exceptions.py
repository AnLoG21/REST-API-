from fastapi import HTTPException, status


class BaseAPIException(HTTPException):
    status_code: int
    detail: str


class NotFoundException(BaseAPIException):
    def __init__(self, resource: str, resource_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'{resource} with id {resource_id} not found'
        )


class ValidationException(BaseAPIException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )


class ConflictException(BaseAPIException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail
        )


class ActivityNestingLevelException(ValidationException):
    def __init__(self):
        super().__init__('Maximum activity nesting level is 3')

