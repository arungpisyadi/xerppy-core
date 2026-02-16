"""Plugin Manager for Xerppy ERP Framework.

This module provides the PluginManager class for discovering, loading,
and registering plugins in the ERP system. It uses importlib.metadata
to find plugins via entry points.
"""

from __future__ import annotations

import logging
from importlib.metadata import EntryPoint, entry_points
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from flask import Flask

if TYPE_CHECKING:
    from collections.abc import Sequence


# Configure logging
logger = logging.getLogger(__name__)


@runtime_checkable
class XerppyPlugin(Protocol):
    """Protocol defining the interface for Xerppy plugins.

    Plugins must implement this protocol to be properly recognized
    and loaded by the PluginManager.

    Attributes:
        name: The unique name of the plugin.
        version: The version string of the plugin.
    """

    name: str
    version: str

    def register_blueprints(self, app: Flask) -> list[Flask]:
        """Register Flask blueprints with the application.

        Args:
            app: The Flask application instance.

        Returns:
            List of registered Flask blueprints.
        """
        ...

    def register_models(self) -> list[type]:
        """Register SQLAlchemy models with the application.

        This is optional - plugins that don't define models
        can omit this method.

        Returns:
            List of SQLAlchemy model classes.
        """
        ...

    def init_app(self, app: Flask) -> None:
        """Initialize the plugin with the Flask application.

        This is called when the Flask app is created, allowing
        the plugin to perform any necessary setup.

        Args:
            app: The Flask application instance.
        """
        ...


class PluginManager:
    """Manages plugin discovery, loading, and registration for the ERP system.

    This class handles:
    - Discovering plugins via entry points
    - Loading individual plugins
    - Registering plugins with the Flask application
    - Tracking loaded plugins

    Example:
        >>> manager = PluginManager()
        >>> manager.discover_plugins()
        >>> manager.register_all(app)
        >>> print(manager.get_loaded_plugins())
    """

    ENTRY_POINT_GROUP: str = "xerppy.plugins"

    def __init__(self) -> None:
        """Initialize the PluginManager."""
        self._discovered_plugins: list[EntryPoint] = []
        self._loaded_plugins: dict[str, XerppyPlugin] = {}

    def discover_plugins(self) -> list[EntryPoint]:
        """Discover all installed plugins via entry points.

        Uses importlib.metadata.entry_points() to find plugins registered
        under the 'xerppy.plugins' group. Supports both Python 3.12+ (.select())
        and older versions (.get()).

        Returns:
            List of discovered entry points for plugins.
        """
        self._discovered_plugins = []

        try:
            # Python 3.12+ uses .select()
            eps = entry_points(group=self.ENTRY_POINT_GROUP)
            if hasattr(eps, "select"):
                self._discovered_plugins = list(eps.select())
            else:
                # Older Python versions
                self._discovered_plugins = list(eps)  # type: ignore[arg-type]
            logger.info(f"Discovered {len(self._discovered_plugins)} plugin(s)")
        except TypeError:
            # Handle case where entry_points() is called without arguments
            # and doesn't support group parameter (older Python versions)
            try:
                eps = entry_points()
                if isinstance(eps, dict):
                    plugins = eps.get(self.ENTRY_POINT_GROUP, [])
                else:
                    # For select-based entry points that don't have group
                    plugins = list(eps)  # type: ignore[union-attr]
                self._discovered_plugins = list(plugins)
                logger.info(f"Discovered {len(self._discovered_plugins)} plugin(s)")
            except Exception as e:
                logger.warning(f"Failed to discover plugins: {e}")
                self._discovered_plugins = []

        return self._discovered_plugins

    def load_plugin(self, entry_point: EntryPoint) -> XerppyPlugin | None:
        """Load a single plugin from an entry point.

        Args:
            entry_point: The entry point to load the plugin from.

        Returns:
            The loaded plugin instance, or None if loading failed.
        """
        plugin_name = entry_point.name
        try:
            plugin_instance = entry_point.load()

            # Check if the plugin implements the required interface
            if not isinstance(plugin_instance, XerppyPlugin):
                logger.warning(
                    f"Plugin '{plugin_name}' does not implement XerppyPlugin protocol"
                )
                # Try to instantiate if it's a class
                if isinstance(plugin_instance, type):
                    plugin_instance = plugin_instance()

            if isinstance(plugin_instance, XerppyPlugin):
                self._loaded_plugins[plugin_instance.name] = plugin_instance
                logger.info(f"Loaded plugin: {plugin_instance.name} v{plugin_instance.version}")
                return plugin_instance
            else:
                logger.error(f"Plugin '{plugin_name}' is not a valid XerppyPlugin")
                return None

        except Exception as e:
            logger.error(f"Failed to load plugin '{plugin_name}': {e}")
            return None

    def register_all(self, app: Flask) -> None:
        """Register all discovered plugins with the Flask app.

        This method:
        1. Discovers plugins if not already done
        2. Loads each plugin
        - Calls init_app() if available
        - Calls register_blueprints() if available
        - Calls register_models() if available

        Args:
            app: The Flask application instance.
        """
        # Discover plugins if not already done
        if not self._discovered_plugins:
            self.discover_plugins()

        for entry_point in self._discovered_plugins:
            plugin = self.load_plugin(entry_point)
            if plugin is None:
                continue

            try:
                # Call init_app if available
                if hasattr(plugin, "init_app"):
                    plugin.init_app(app)
                    logger.debug(f"Called init_app for plugin: {plugin.name}")

                # Register blueprints
                if hasattr(plugin, "register_blueprints"):
                    blueprints = plugin.register_blueprints(app)
                    for bp in blueprints:
                        app.register_blueprint(bp)
                    logger.debug(f"Registered {len(blueprints)} blueprint(s) for plugin: {plugin.name}")

                # Register models (informational, models are registered via SQLAlchemy)
                if hasattr(plugin, "register_models"):
                    models = plugin.register_models()
                    logger.debug(f"Found {len(models)} model(s) for plugin: {plugin.name}")

                logger.info(f"Successfully registered plugin: {plugin.name}")

            except Exception as e:
                logger.error(f"Error registering plugin '{plugin.name}': {e}")
                # Continue loading other plugins

    def get_loaded_plugins(self) -> list[str]:
        """Get list of loaded plugin names.

        Returns:
            List of plugin names that were successfully loaded.
        """
        return list(self._loaded_plugins.keys())

    def get_plugin(self, name: str) -> XerppyPlugin | None:
        """Get a specific plugin by name.

        Args:
            name: The name of the plugin to retrieve.

        Returns:
            The plugin instance, or None if not found.
        """
        return self._loaded_plugins.get(name)

    @property
    def discovered_count(self) -> int:
        """Get the number of discovered plugins.

        Returns:
            Number of plugins discovered.
        """
        return len(self._discovered_plugins)

    @property
    def loaded_count(self) -> int:
        """Get the number of loaded plugins.

        Returns:
            Number of plugins successfully loaded.
        """
        return len(self._loaded_plugins)
