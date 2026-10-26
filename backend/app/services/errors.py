class DomainError(Exception):
    code = "domain_error"
    message = "Request could not be processed"
    fields: dict[str, str]

    def __init__(self, fields: dict[str, str] | None = None) -> None:
        super().__init__(self.message)
        self.fields = fields or {}


class EmployeeNotFound(DomainError):
    code = "employee_not_found"
    message = "Employee not found"


class DuplicateEmployee(DomainError):
    code = "duplicate_employee"

    def __init__(self, field: str) -> None:
        super().__init__({field: "Already in use"})
        label = "employee code" if field == "employee_code" else field
        self.message = f"An employee with this {label} already exists"


class RuleViolation(DomainError):
    code = "validation_error"
    message = "Some fields are invalid"


class EmployeeTerminated(DomainError):
    code = "employee_terminated"
    message = "Terminated employees cannot be edited"
