"""Core package for Xerppy ERP framework.

This package contains core application components including extensions,
models, and application factory setup.
"""

from core.extensions import db, ldap_manager, login_manager, migrate

__all__ = ["db", "login_manager", "migrate", "ldap_manager"]
