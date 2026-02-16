"""Core package for Xerppy ERP framework.

This package contains core application components including extensions,
models, and application factory setup.
"""

from core.extensions import db, login_manager, migrate, ldap_manager

__all__ = ["db", "login_manager", "migrate", "ldap_manager"]
