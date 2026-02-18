"""Sample Plugin for Xerppy ERP Framework.

This is a sample plugin demonstrating how to implement the XerppyPlugin
protocol. It provides a simple Flask blueprint with a single route.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flask import Blueprint, Flask, render_template_string

if TYPE_CHECKING:
    pass


class SamplePlugin:
    """Sample plugin demonstrating the XerppyPlugin protocol.

    This plugin creates a simple 'sample' blueprint with a hello world route.
    It can be used to test the plugin system.

    Attributes:
        name: The unique name of the plugin.
        version: The version string of the plugin.
    """

    name: str = "sample"
    version: str = "1.0.0"

    def __init__(self) -> None:
        """Initialize the sample plugin."""
        self._blueprint: Blueprint | None = None

    def register_blueprints(self, app: Flask) -> list[Blueprint]:
        """Register Flask blueprints with the application.

        Creates a simple 'sample' blueprint with a hello route.

        Args:
            app: The Flask application instance.

        Returns:
            List containing the registered blueprint.
        """
        self._blueprint = Blueprint(
            "sample",
            __name__,
            url_prefix="/sample",
        )

        @self._blueprint.route("/")
        def hello() -> str:
            """Sample route that returns a greeting.

            Returns:
                HTML greeting message.
            """
            return render_template_string(
                "<!DOCTYPE html><html><head><title>Sample Plugin</title></head>"
                "<body><h1>Hello from Sample Plugin!</h1>"
                "<p>This is a sample plugin for Xerppy ERP Framework.</p>"
                "<p>Plugin version: {{ version }}</p>"
                "</body></html>",
                version=self.version,
            )

        @self._blueprint.route("/info")
        def info() -> dict[str, str]:
            """Sample route that returns plugin info as JSON.

            Returns:
                JSON object with plugin information.
            """
            return {
                "name": self.name,
                "version": self.version,
                "description": "Sample plugin for testing the Xerppy plugin system",
            }

        app.register_blueprint(self._blueprint)
        return [self._blueprint]

    def register_models(self) -> list[type]:
        """Register SQLAlchemy models with the application.

        This sample plugin doesn't define any models, so it returns
        an empty list.

        Returns:
            Empty list since this plugin has no models.
        """
        return []

    def init_app(self, app: Flask) -> None:
        """Initialize the plugin with the Flask application.

        This is called when the Flask app is created. For this sample
        plugin, we just log that initialization occurred.

        Args:
            app: The Flask application instance.
        """
        app.logger.info(f"Initializing {self.name} plugin v{self.version}")


# Plugin instance for entry point discovery
plugin = SamplePlugin()
