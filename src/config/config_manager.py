"""
==============================================================================
Mahy Mythic Labs Studio OS

Configuration Manager

Central configuration entry point.

Responsibilities
----------------
- Load configuration
- Merge YAML files
- Resolve environment variables
- Validate configuration
- Provide configuration API

Author : Mahy Mythic Labs
License: MIT
==============================================================================
"""

from __future__ import annotations

from pathlib import Path
from threading import Lock
from typing import Any

from src.config.defaults import (
    DEFAULT_CONFIG_DIRECTORY,
    DEFAULT_CONFIG_FILES,
)

from src.config.env_loader import (
    EnvironmentLoader,
)

from src.config.path_resolver import (
    PathResolver,
)

from src.config.validator import (
    ConfigValidator,
)

from src.config.yaml_loader import (
    YAMLLoader,
)


class ConfigManager:
    """
    Singleton configuration manager.

    Example
    -------

    config = ConfigManager()

    config.load()

    model = config.get(
        "providers.default_llm"
    )
    """

    _instance = None

    _lock = Lock()

    # ------------------------------------------------------------------ #

    def __new__(cls):

        with cls._lock:

            if cls._instance is None:

                cls._instance = super().__new__(cls)

        return cls._instance

    # ------------------------------------------------------------------ #

    def __init__(
        self,
        project_root: str | Path | None = None,
    ) -> None:

        if hasattr(self, "_initialized"):
            return

        self._initialized = True

        # -------------------------------------------------------------- #
        # Project Root
        # -------------------------------------------------------------- #

        if project_root is None:

            self.project_root = (
                Path.cwd()
            )

        else:

            self.project_root = (
                Path(project_root)
                .resolve()
            )

        # -------------------------------------------------------------- #
        # Components
        # -------------------------------------------------------------- #

        self.path_resolver = PathResolver(
            self.project_root
        )

        self.env_loader = EnvironmentLoader(
            self.project_root
        )

        self.yaml_loader = YAMLLoader(
            self.env_loader
        )

        self.validator = ConfigValidator()

        # -------------------------------------------------------------- #
        # Internal State
        # -------------------------------------------------------------- #

        self.config: dict[str, Any] = {}

        self.loaded_files: list[str] = []

        self.loaded = False

        self.config_directory = (
            self.path_resolver.resolve(
                DEFAULT_CONFIG_DIRECTORY
            )
        )

        self.config_files = [

            self.config_directory / name

            for name in DEFAULT_CONFIG_FILES

        ]

        # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def load(self) -> None:
        """
        Load the complete application configuration.

        Steps
        -----
        1. Load environment variables
        2. Load YAML configuration files
        3. Validate configuration
        4. Mark configuration as loaded
        """

        if self.loaded:
            return

        self._load_environment()

        self._load_yaml_files()

        self.validator.validate_files(
            self.loaded_files
        )

        self.validator.validate(
            self.config
        )

        self.validator.raise_if_invalid()

        self.loaded = True

    # ------------------------------------------------------------------ #

    def reload(self) -> None:
        """
        Reload the complete configuration.
        """

        self.loaded = False

        self.config.clear()

        self.loaded_files.clear()

        self.env_loader.reload()

        self.load()

    # ------------------------------------------------------------------ #
    # Internal Methods
    # ------------------------------------------------------------------ #

    def _load_environment(self) -> None:
        """
        Load .env file.
        """

        self.env_loader.load()

    # ------------------------------------------------------------------ #

    def _load_yaml_files(self) -> None:
        """
        Load every configured YAML file.
        """

        self.loaded_files.clear()

        self.config.clear()

        for file in self.config_files:

            if not file.exists():
                continue

            yaml_data = self.yaml_loader.load_file(
                file
            )

            self.config = self.yaml_loader.merge(
                self.config,
                yaml_data,
            )

            self.loaded_files.append(
                file.name
            )

    # ------------------------------------------------------------------ #

    def is_loaded(self) -> bool:
        """
        Returns True if configuration has already
        been loaded.
        """

        return self.loaded

    # ------------------------------------------------------------------ #

    def configuration_files(self) -> list[Path]:
        """
        Return all configured YAML files.
        """

        return self.config_files.copy()

    # ------------------------------------------------------------------ #

    def loaded_configuration_files(
        self,
    ) -> list[str]:
        """
        Return successfully loaded configuration files.
        """

        return self.loaded_files.copy()

        # ------------------------------------------------------------------ #
    # Configuration Access
    # ------------------------------------------------------------------ #

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Get configuration value using dot notation.

        Example
        -------
        config.get("providers.default_llm")
        """

        if not self.loaded:
            self.load()

        current = self.config

        for part in key.split("."):

            if not isinstance(current, dict):
                return default

            if part not in current:
                return default

            current = current[part]

        return current

    # ------------------------------------------------------------------ #

    def set(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Set configuration value.

        Example
        -------
        config.set("providers.default_llm", "openai")
        """

        current = self.config

        parts = key.split(".")

        for part in parts[:-1]:

            if (
                part not in current
                or not isinstance(current[part], dict)
            ):
                current[part] = {}

            current = current[part]

        current[parts[-1]] = value

    # ------------------------------------------------------------------ #

    def exists(
        self,
        key: str,
    ) -> bool:
        """
        Check whether configuration key exists.
        """

        current = self.config

        for part in key.split("."):

            if not isinstance(current, dict):
                return False

            if part not in current:
                return False

            current = current[part]

        return True

    # ------------------------------------------------------------------ #

    def remove(
        self,
        key: str,
    ) -> bool:
        """
        Remove configuration key.

        Returns
        -------
        bool
            True if removed successfully.
        """

        current = self.config

        parts = key.split(".")

        for part in parts[:-1]:

            if (
                part not in current
                or not isinstance(current[part], dict)
            ):
                return False

            current = current[part]

        return current.pop(parts[-1], None) is not None

    # ------------------------------------------------------------------ #

    def all(self) -> dict[str, Any]:
        """
        Return complete configuration.
        """

        return self.config.copy()

    # ------------------------------------------------------------------ #

    def keys(self) -> list[str]:
        """
        Return top-level configuration keys.
        """

        return list(self.config.keys())

    # ------------------------------------------------------------------ #

    def sections(self) -> list[str]:
        """
        Alias for keys().
        """

        return self.keys()

    # ------------------------------------------------------------------ #

    def clear(self) -> None:
        """
        Clear loaded configuration.
        """

        self.config.clear()

        self.loaded_files.clear()

        self.loaded = False

        # ------------------------------------------------------------------ #
    # Configuration Access
    # ------------------------------------------------------------------ #

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Get configuration value using dot notation.

        Example
        -------
        config.get("providers.default_llm")
        """

        if not self.loaded:
            self.load()

        current = self.config

        for part in key.split("."):

            if not isinstance(current, dict):
                return default

            if part not in current:
                return default

            current = current[part]

        return current

    # ------------------------------------------------------------------ #

    def set(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Set configuration value.

        Example
        -------
        config.set("providers.default_llm", "openai")
        """

        current = self.config

        parts = key.split(".")

        for part in parts[:-1]:

            if (
                part not in current
                or not isinstance(current[part], dict)
            ):
                current[part] = {}

            current = current[part]

        current[parts[-1]] = value

    # ------------------------------------------------------------------ #

    def exists(
        self,
        key: str,
    ) -> bool:
        """
        Check whether configuration key exists.
        """

        current = self.config

        for part in key.split("."):

            if not isinstance(current, dict):
                return False

            if part not in current:
                return False

            current = current[part]

        return True

    # ------------------------------------------------------------------ #

    def remove(
        self,
        key: str,
    ) -> bool:
        """
        Remove configuration key.

        Returns
        -------
        bool
            True if removed successfully.
        """

        current = self.config

        parts = key.split(".")

        for part in parts[:-1]:

            if (
                part not in current
                or not isinstance(current[part], dict)
            ):
                return False

            current = current[part]

        return current.pop(parts[-1], None) is not None

    # ------------------------------------------------------------------ #

    def all(self) -> dict[str, Any]:
        """
        Return complete configuration.
        """

        return self.config.copy()

    # ------------------------------------------------------------------ #

    def keys(self) -> list[str]:
        """
        Return top-level configuration keys.
        """

        return list(self.config.keys())

    # ------------------------------------------------------------------ #

    def sections(self) -> list[str]:
        """
        Alias for keys().
        """

        return self.keys()

    # ------------------------------------------------------------------ #

    def clear(self) -> None:
        """
        Clear loaded configuration.
        """

        self.config.clear()

        self.loaded_files.clear()

        self.loaded = False

        # ------------------------------------------------------------------ #
    # Dictionary Interface
    # ------------------------------------------------------------------ #

    def __getitem__(
        self,
        key: str,
    ) -> Any:
        """
        Dictionary-style access.

        Example
        -------
        config["providers.default_llm"]
        """

        value = self.get(key)

        if value is None:
            raise KeyError(
                f"Configuration key '{key}' not found."
            )

        return value

    # ------------------------------------------------------------------ #

    def __setitem__(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Dictionary-style assignment.

        Example
        -------
        config["logging.level"] = "DEBUG"
        """

        self.set(key, value)

    # ------------------------------------------------------------------ #

    def __contains__(
        self,
        key: str,
    ) -> bool:
        """
        Support 'in' operator.

        Example
        -------
        if "logging.level" in config:
            ...
        """

        return self.exists(key)

    # ------------------------------------------------------------------ #

    def __len__(self) -> int:
        """
        Number of top-level sections.
        """

        return len(self.config)

    # ------------------------------------------------------------------ #

    def __iter__(self):
        """
        Iterate over top-level sections.

        Example
        -------
        for section in config:
            ...
        """

        return iter(self.config)

    # ------------------------------------------------------------------ #

    def items(self):
        """
        Return configuration items.
        """

        return self.config.items()

    # ------------------------------------------------------------------ #

    def values(self):
        """
        Return configuration values.
        """

        return self.config.values()

    # ------------------------------------------------------------------ #

    def copy(self) -> dict[str, Any]:
        """
        Return shallow copy of configuration.
        """

        return self.config.copy()

    # ------------------------------------------------------------------ #
    # String Representation
    # ------------------------------------------------------------------ #

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"loaded={self.loaded}, "
            f"sections={len(self.config)}, "
            f"files={len(self.loaded_files)})"
        )

    # ------------------------------------------------------------------ #

    def __str__(self) -> str:

        return (
            f"ConfigManager("
            f"loaded={self.loaded}, "
            f"sections={list(self.config.keys())})"
        )