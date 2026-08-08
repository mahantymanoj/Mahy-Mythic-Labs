"""
==============================================================================
Mahy Mythic Labs Studio OS

Configuration Schema

Defines the expected configuration structure for the application.

This module contains NO validation logic.
It only defines the schema used by validator.py.

Author : Mahy Mythic Labs
License: MIT
==============================================================================
"""

from __future__ import annotations

from typing import Any

###############################################################################
# Required Configuration Files
###############################################################################

REQUIRED_CONFIG_FILES = (
    "settings.yaml",
    "providers.yaml",
    "models.yaml",
    "paths.yaml",
    "logging.yaml",
)

###############################################################################
# Required Top-Level Sections
###############################################################################

REQUIRED_SECTIONS = (
    "settings",
    "providers",
    "models",
    "paths",
    "logging",
)

###############################################################################
# Optional Sections
###############################################################################

OPTIONAL_SECTIONS = (
    "generation",
    "research",
    "video",
    "image",
    "audio",
    "cache",
    "storage",
)

###############################################################################
# Required Keys Per Section
###############################################################################

REQUIRED_KEYS: dict[str, tuple[str, ...]] = {

    "settings": (
        "application_name",
        "environment",
        "debug",
    ),

    "providers": (
        "default_llm",
        "default_image",
        "default_video",
        "default_audio",
    ),

    "models": (
        "llm",
        "image",
        "video",
        "audio",
    ),

    "paths": (
        "projects",
        "output",
        "cache",
        "logs",
        "assets",
    ),

    "logging": (
        "level",
        "format",
        "file",
    ),
}

###############################################################################
# Expected Data Types
###############################################################################

EXPECTED_TYPES: dict[str, type | tuple[type, ...]] = {

    # settings

    "settings.application_name": str,
    "settings.environment": str,
    "settings.debug": bool,

    # providers

    "providers.default_llm": str,
    "providers.default_image": str,
    "providers.default_video": str,
    "providers.default_audio": str,

    # logging

    "logging.level": str,
    "logging.format": str,
    "logging.file": str,

    # paths

    "paths.projects": str,
    "paths.output": str,
    "paths.cache": str,
    "paths.logs": str,
    "paths.assets": str,
}

###############################################################################
# Default Values
###############################################################################

DEFAULT_VALUES: dict[str, Any] = {

    "settings.environment": "development",

    "settings.debug": False,

    "logging.level": "INFO",

    "providers.default_llm": "openai",

    "providers.default_image": "gemini",

    "providers.default_video": "veo",

    "providers.default_audio": "edge-tts",
}

###############################################################################
# Allowed Values
###############################################################################

ALLOWED_ENVIRONMENTS = (

    "development",

    "testing",

    "staging",

    "production",
)

LOG_LEVELS = (

    "DEBUG",

    "INFO",

    "WARNING",

    "ERROR",

    "CRITICAL",
)

###############################################################################
# Path Keys
###############################################################################

PATH_KEYS = (

    "projects",

    "output",

    "cache",

    "logs",

    "assets",
)

###############################################################################
# Provider Categories
###############################################################################

PROVIDER_CATEGORIES = (

    "llm",

    "image",

    "video",

    "audio",

    "music",
)

###############################################################################
# Required Provider Configuration
###############################################################################

REQUIRED_PROVIDER_FIELDS = (

    "enabled",

    "priority",

    "models",
)

###############################################################################
# Supported Configuration Extensions
###############################################################################

SUPPORTED_CONFIG_EXTENSIONS = (

    ".yaml",

    ".yml",
)

###############################################################################
# Immutable Configuration Keys
###############################################################################

READ_ONLY_KEYS = (

    "application_name",

    "environment",
)

###############################################################################
# Schema Version
###############################################################################

SCHEMA_VERSION = "1.0.0"