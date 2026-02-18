"""Plugins package for Xerppy ERP Framework.

This package provides the plugin system for extending the ERP framework
with modular, discoverable components.
"""

from core.plugins.manager import PluginManager, XerppyPlugin

__all__ = ["PluginManager", "XerppyPlugin"]
