"""
==============================================================================
Mahy Mythic Labs Studio OS

Configuration Validator

Validates loaded configuration against the application schema.

Responsibilities
----------------
- Validate configuration files
- Validate required sections
- Validate required keys
- Validate value types
- Validate allowed values
- Apply default values
- Produce validation report

Author : Mahy Mythic Labs
License: MIT
==============================================================================
"""

from __future__ import annotations

from typing import Any

from src.config.schema import (
    REQUIRED_CONFIG_FILES,
    REQUIRED_KEYS,
    REQUIRED_SECTIONS,
    EXPECTED_TYPES,
    DEFAULT_VALUES,
    ALLOWED_ENVIRONMENTS,
    LOG_LEVELS,
)


class ConfigValidator:
    """
    Validate application configuration.

    Example
    -------
    validator = ConfigValidator()

    validator.validate(config)

    if validator.has_errors():
        print(validator.report())
    """

    # ------------------------------------------------------------------ #

    def __init__(self) -> None:

        self.errors: list[str] = []

        self.warnings: list[str] = []

    # ------------------------------------------------------------------ #

    def validate(
        self,
        config: dict[str, Any],
    ) -> bool:
        """
        Validate complete configuration.

        Parameters
        ----------
        config
            Complete configuration dictionary.

        Returns
        -------
        bool
            True if configuration is valid.
        """

        self.errors.clear()

        self.warnings.clear()

        self.validate_sections(config)

        self.validate_required_keys(config)

        self.validate_types(config)

        self.validate_allowed_values(config)

        self.apply_defaults(config)

        return not self.has_errors()

    # ------------------------------------------------------------------ #

    def add_error(
        self,
        message: str,
    ) -> None:

        self.errors.append(message)

    # ------------------------------------------------------------------ #

    def add_warning(
        self,
        message: str,
    ) -> None:

        self.warnings.append(message)

        # ------------------------------------------------------------------ #
    # Configuration File Validation
    # ------------------------------------------------------------------ #

    def validate_files(
        self,
        loaded_files: list[str],
    ) -> None:
        """
        Validate required configuration files.

        Parameters
        ----------
        loaded_files
            List of configuration filenames that were loaded.
        """

        loaded = set(loaded_files)

        required = set(REQUIRED_CONFIG_FILES)

        missing = required - loaded

        for file in sorted(missing):

            self.add_error(
                f"Missing configuration file: '{file}'"
            )

    # ------------------------------------------------------------------ #
    # Section Validation
    # ------------------------------------------------------------------ #

    def validate_sections(
        self,
        config: dict[str, Any],
    ) -> None:
        """
        Validate required configuration sections.

        Example
        -------
        settings
        providers
        paths
        logging
        models
        """

        for section in REQUIRED_SECTIONS:

            if section not in config:

                self.add_error(
                    f"Missing configuration section: "
                    f"'{section}'"
                )

                continue

            if not isinstance(config[section], dict):

                self.add_error(
                    f"Configuration section "
                    f"'{section}' must be a dictionary."
                )

    # ------------------------------------------------------------------ #
    # Required Key Validation
    # ------------------------------------------------------------------ #

    def validate_required_keys(
        self,
        config: dict[str, Any],
    ) -> None:
        """
        Validate required keys inside every section.
        """

        for section, keys in REQUIRED_KEYS.items():

            if section not in config:
                continue

            section_data = config[section]

            if not isinstance(section_data, dict):
                continue

            for key in keys:

                if key not in section_data:

                    self.add_error(
                        f"Missing required key: "
                        f"'{section}.{key}'"
                    )

    # ------------------------------------------------------------------ #
    # Utility
    # ------------------------------------------------------------------ #

    def section_exists(
        self,
        config: dict[str, Any],
        section: str,
    ) -> bool:
        """
        Check whether a configuration section exists.
        """

        return (
            section in config
            and isinstance(config[section], dict)
        )

    # ------------------------------------------------------------------ #

    def key_exists(
        self,
        config: dict[str, Any],
        path: str,
    ) -> bool:
        """
        Check whether a dotted key exists.

        Example
        -------
        providers.default_llm
        """

        current: Any = config

        for part in path.split("."):

            if not isinstance(current, dict):
                return False

            if part not in current:
                return False

            current = current[part]

        return True

        # ------------------------------------------------------------------ #
    # Type Validation
    # ------------------------------------------------------------------ #

    def validate_types(
        self,
        config: dict[str, Any],
    ) -> None:
        """
        Validate data types according to EXPECTED_TYPES.
        """

        for path, expected_type in EXPECTED_TYPES.items():

            value = self._get_nested_value(config, path)

            if value is None:
                continue

            if not isinstance(value, expected_type):

                expected = self._type_name(expected_type)

                actual = type(value).__name__

                self.add_error(
                    f"Invalid type for '{path}'. "
                    f"Expected '{expected}', "
                    f"got '{actual}'."
                )

    # ------------------------------------------------------------------ #
    # Allowed Value Validation
    # ------------------------------------------------------------------ #

    def validate_allowed_values(
        self,
        config: dict[str, Any],
    ) -> None:
        """
        Validate values restricted by schema.
        """

        environment = self._get_nested_value(
            config,
            "settings.environment",
        )

        if (
            environment is not None
            and environment not in ALLOWED_ENVIRONMENTS
        ):

            self.add_error(
                f"Invalid environment '{environment}'. "
                f"Allowed values: "
                f"{', '.join(ALLOWED_ENVIRONMENTS)}"
            )

        log_level = self._get_nested_value(
            config,
            "logging.level",
        )

        if (
            log_level is not None
            and log_level not in LOG_LEVELS
        ):

            self.add_error(
                f"Invalid logging level '{log_level}'. "
                f"Allowed values: "
                f"{', '.join(LOG_LEVELS)}"
            )

    # ------------------------------------------------------------------ #
    # Nested Dictionary Helpers
    # ------------------------------------------------------------------ #

    def _get_nested_value(
        self,
        config: dict[str, Any],
        path: str,
    ) -> Any:
        """
        Get nested configuration value.

        Example
        -------
        providers.default_llm
        """

        current: Any = config

        for part in path.split("."):

            if not isinstance(current, dict):
                return None

            if part not in current:
                return None

            current = current[part]

        return current

    # ------------------------------------------------------------------ #

    def _type_name(
        self,
        expected: Any,
    ) -> str:
        """
        Return readable type name.
        """

        if isinstance(expected, tuple):

            return " | ".join(
                t.__name__
                for t in expected
            )

        return expected.__name__

        # ------------------------------------------------------------------ #
    # Apply Default Values
    # ------------------------------------------------------------------ #

    def apply_defaults(
        self,
        config: dict[str, Any],
    ) -> None:
        """
        Apply missing default values defined in schema.py.

        Existing values are never overwritten.
        """

        for path, default_value in DEFAULT_VALUES.items():

            if self.key_exists(config, path):
                continue

            self._set_nested_value(
                config,
                path,
                default_value,
            )

            self.add_warning(
                f"Using default value for '{path}'"
            )

    # ------------------------------------------------------------------ #
    # Nested Dictionary Setter
    # ------------------------------------------------------------------ #

    def _set_nested_value(
        self,
        config: dict[str, Any],
        path: str,
        value: Any,
    ) -> None:
        """
        Set a nested configuration value.

        Example
        -------
        providers.default_llm
        """

        parts = path.split(".")

        current = config

        for part in parts[:-1]:

            if (
                part not in current
                or not isinstance(current[part], dict)
            ):
                current[part] = {}

            current = current[part]

        current[parts[-1]] = value

    # ------------------------------------------------------------------ #
    # Validation State
    # ------------------------------------------------------------------ #

    def has_errors(self) -> bool:
        """
        Returns True if validation failed.
        """

        return len(self.errors) > 0

    # ------------------------------------------------------------------ #

    def has_warnings(self) -> bool:
        """
        Returns True if warnings exist.
        """

        return len(self.warnings) > 0

    # ------------------------------------------------------------------ #

    def error_count(self) -> int:
        """
        Number of validation errors.
        """

        return len(self.errors)

    # ------------------------------------------------------------------ #

    def warning_count(self) -> int:
        """
        Number of validation warnings.
        """

        return len(self.warnings)

    # ------------------------------------------------------------------ #

    def clear(self) -> None:
        """
        Reset validator state.
        """

        self.errors.clear()
        self.warnings.clear()

    # ------------------------------------------------------------------ #

    def get_errors(self) -> list[str]:
        """
        Return all validation errors.
        """

        return self.errors.copy()

    # ------------------------------------------------------------------ #

    def get_warnings(self) -> list[str]:
        """
        Return all validation warnings.
        """

        return self.warnings.copy()

        # ------------------------------------------------------------------ #
    # Validation Report
    # ------------------------------------------------------------------ #

    def report(self) -> str:
        """
        Generate a human-readable validation report.

        Returns
        -------
        str
            Formatted validation summary.
        """

        lines: list[str] = []

        lines.append("=" * 70)
        lines.append("Configuration Validation Report")
        lines.append("=" * 70)

        lines.append("")
        lines.append(f"Errors   : {self.error_count()}")
        lines.append(f"Warnings : {self.warning_count()}")

        # -------------------------------------------------------------- #

        if self.errors:

            lines.append("")
            lines.append("Errors")
            lines.append("-" * 70)

            for index, error in enumerate(self.errors, start=1):

                lines.append(f"{index}. {error}")

        # -------------------------------------------------------------- #

        if self.warnings:

            lines.append("")
            lines.append("Warnings")
            lines.append("-" * 70)

            for index, warning in enumerate(
                self.warnings,
                start=1,
            ):

                lines.append(f"{index}. {warning}")

        # -------------------------------------------------------------- #

        if not self.errors and not self.warnings:

            lines.append("")
            lines.append("Configuration validation successful.")

        lines.append("")
        lines.append("=" * 70)

        return "\n".join(lines)

    # ------------------------------------------------------------------ #

    def is_valid(self) -> bool:
        """
        Returns True if configuration contains no errors.
        """

        return not self.has_errors()

    # ------------------------------------------------------------------ #

    def raise_if_invalid(self) -> None:
        """
        Raise an exception if validation failed.
        """

        if self.has_errors():

            raise ValueError(
                self.report()
            )

    # ------------------------------------------------------------------ #

    def summary(self) -> dict[str, int]:
        """
        Return validation summary.

        Example
        -------
        {
            "errors": 0,
            "warnings": 2
        }
        """

        return {
            "errors": self.error_count(),
            "warnings": self.warning_count(),
        }

    # ------------------------------------------------------------------ #

    def __str__(self) -> str:

        return self.report()

    # ------------------------------------------------------------------ #

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"errors={self.error_count()}, "
            f"warnings={self.warning_count()})"
        )