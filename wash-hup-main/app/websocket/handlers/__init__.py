# app/websocket/handlers/__init__.py
from typing import Dict, Type
from .base import BaseHandler
# from .chat import ChatHandler
from .issue import IssueHandler
from .issue_admin import IssueAdminHandler
# from .wash import WashHandler

_registry: Dict[str, BaseHandler] = {
    # "chat": ChatHandler(),
    "issue": IssueHandler(),
    "admin_issue": IssueAdminHandler()
    # "wash": WashHandler(),
}

def get_handler(action: str) -> BaseHandler | None:
    if _registry.get(action) == None:
        return None
    return _registry.get(action)