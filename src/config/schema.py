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
# Required Top-Level Sections (must be dicts in merged config)
###############################################################################

REQUIRED_SECTIONS = (
    "application",
    "repository",
    "episode",
    "workflow",
    "generation",
    "logging",
    "cache",
    "quality",
    "assets",
    "youtube",
    "documentation",
    "security",
    "performance",
    "experimental",
    "features",
    "metadata",
    "global",
    "openai",
    "anthropic",
    "google",
    "xai",
    "elevenlabs",
    "stability",
    "replicate",
    "runway",
    "pika",
    "kling",
    "default_models",
    "providers",
    "image_generation",
    "video_generation",
    "voice_generation",
    "routing",
    "cost_control",
    "root",
    "docs",
    "production_bible",
    "prompts",
    "templates",
    "projects",
    "assets",
    "output",
    "config",
    "logs",
    "cache",
    "temp",
    "archive",
    "reports",
    "metadata",
    "environment",
    "root_files",
)

###############################################################################
# Optional Sections
###############################################################################

OPTIONAL_SECTIONS = (
    "research",
    "video",
    "image",
    "audio",
    "storage",
)

###############################################################################
# Required Keys Per Section
###############################################################################

REQUIRED_KEYS: dict[str, tuple[str, ...]] = {

    "application": (
        "name",
        "environment",
        "debug",
    ),

    "repository": (
        "root",
    ),

    "logging": (
        "enabled",
        "level",
        "log_to_file",
        "log_directory",
    ),

    # Top-level string keys (not dicts)
    "default_llm": (),
    "default_image": (),
    "default_video": (),
    "default_audio": (),
}

###############################################################################
# Expected Data Types
###############################################################################

EXPECTED_TYPES: dict[str, type | tuple[type, ...]] = {

    # application

    "application.name": str,
    "application.environment": str,
    "application.debug": bool,

    # repository

    "repository.root": str,

    # logging

    "logging.enabled": bool,
    "logging.level": str,
    "logging.log_to_file": bool,
    "logging.log_directory": str,

    # providers (top-level string keys from providers.yaml)

    "default_llm": str,
    "default_image": str,
    "default_video": str,
    "default_audio": str,

    # paths (top-level dict keys from paths.yaml)

    "projects.root": str,
    "projects.images": str,
    "projects.generated_images": str,
    "projects.thumbnails": str,
    "projects.reference_images": str,
    "projects.videos": str,
    "projects.audio": str,
    "projects.music": str,
    "projects.sfx": str,
    "projects.fonts": str,
    "projects.logos": str,

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

    "application.environment": "development",

    "application.debug": False,

    "logging.enabled": True,
    "logging.level": "INFO",
    "logging.log_to_file": True,
    "logging.log_directory": "./logs",

    "default_llm": "openai",

    "default_image": "gemini",

    "default_video": "veo",

    "default_audio": "edge-tts",
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

    "application.name",

    "application.environment",
)

###############################################################################
# Schema Version
###############################################################################

SCHEMA_VERSION = "1.0.0"