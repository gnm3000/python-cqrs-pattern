"""Centralized TTL configuration for read-side cache entries."""

TTL_EMPLOYEE_LIST = 5
TTL_EMPLOYEE_DETAIL = 2
TTL_SALARY_VIEW = 1

EMPLOYEE_LIST_CACHE_KEY = "employee:list"


def employee_detail_cache_key(employee_id: int) -> str:
    return f"employee:detail:{employee_id}"
