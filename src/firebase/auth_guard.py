from typing import List, Callable, Any
from functools import wraps

from src.firebase.firebase_service import FirebaseService
from src.utils.logger import get_logger

logger = get_logger(__name__)

class AuthGuard:
    """
    Foundation for Role-Based Access Control (RBAC) route protection.
    Provides utility decorators for protecting routes or functions based on
    the current authenticated user's role.
    """
    def __init__(self, firebase_service: FirebaseService):
        self.firebase_service = firebase_service

    def require_auth(self, func: Callable) -> Callable:
        """Decorator to ensure a user is logged in."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not self.firebase_service.get_current_user():
                logger.warning("Access denied: User is not authenticated.")
                raise PermissionError("Unauthenticated: Please log in.")
            return func(*args, **kwargs)
        return wrapper

    def require_roles(self, allowed_roles: List[str]) -> Callable:
        """Decorator to ensure the user has one of the allowed roles."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                current_role = self.firebase_service.get_current_role()
                
                if not current_role:
                    logger.warning("Access denied: User is not authenticated or has no role.")
                    raise PermissionError("Unauthenticated: Please log in.")
                    
                if current_role not in allowed_roles and current_role != "admin":
                    logger.warning(f"Access denied: Role '{current_role}' is not in allowed roles {allowed_roles}.")
                    raise PermissionError("Forbidden: Insufficient privileges.")
                    
                return func(*args, **kwargs)
            return wrapper
        return decorator

    # Pre-defined scope protectors
    def require_admin(self, func: Callable) -> Callable:
        return self.require_roles(["admin"])(func)

    def require_vc(self, func: Callable) -> Callable:
        return self.require_roles(["vc"])(func)

    def require_dean(self, func: Callable) -> Callable:
        return self.require_roles(["dean"])(func)

    def require_hod(self, func: Callable) -> Callable:
        return self.require_roles(["hod"])(func)

    def require_teacher(self, func: Callable) -> Callable:
        return self.require_roles(["teacher"])(func)

    def require_student(self, func: Callable) -> Callable:
        return self.require_roles(["student"])(func)
