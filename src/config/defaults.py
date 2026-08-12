"""
==============================================================================
Mahy Mythic Labs Studio OS

Configuration Defaults

Centralized default configuration values used by the configuration system.

Author: Mahy Mythic Labs
License: MIT
==============================================================================
"""

from __future__ import annotations

###############################################################################
# Application
###############################################################################

APP_NAME = "Mahy Mythic Labs Studio OS"

APP_VERSION = "1.0.0"

###############################################################################
# Configuration
###############################################################################

DEFAULT_CONFIG_DIRECTORY = "config"

DEFAULT_ENV_FILE = ".env"

DEFAULT_ENCODING = "utf-8"

DEFAULT_YAML_EXTENSION = ".yaml"

###############################################################################
# Configuration Files
###############################################################################

DEFAULT_CONFIG_FILES = (
    "settings.yaml",
    "providers.yaml",
    "models.yaml",
    "paths.yaml",
    "logging.yaml",
)

###############################################################################
# Logging
###############################################################################

DEFAULT_LOG_LEVEL = "INFO"

DEFAULT_LOG_FORMAT = (
    "%(asctime)s | "
    "%(levelname)-8s | "
    "%(name)s | "
    "%(message)s"
)

DEFAULT_LOG_FILE = "studio.log"

###############################################################################
# Provider Defaults
###############################################################################

DEFAULT_PROVIDER = "openai"

DEFAULT_LLM_MODEL = "gpt-4o"

DEFAULT_IMAGE_PROVIDER = "gemini"

DEFAULT_VIDEO_PROVIDER = "veo"

DEFAULT_AUDIO_PROVIDER = "edge-tts"

###############################################################################
# Generation Defaults
###############################################################################

DEFAULT_LANGUAGE = "en"

DEFAULT_TEMPERATURE = 0.7

DEFAULT_TOP_P = 0.95

DEFAULT_MAX_TOKENS = 4096

DEFAULT_TIMEOUT = 120

DEFAULT_RETRY_COUNT = 3

###############################################################################
# Cache
###############################################################################

CACHE_ENABLED = True

CACHE_DIRECTORY = "cache"

CACHE_EXPIRY_SECONDS = 86400  # 24 hours

###############################################################################
# Project
###############################################################################

DEFAULT_PROJECT_DIRECTORY = "projects"

DEFAULT_OUTPUT_DIRECTORY = "output"

DEFAULT_ASSET_DIRECTORY = "assets"

###############################################################################
# Research
###############################################################################

DEFAULT_RESEARCH_DEPTH = "standard"

DEFAULT_USE_WEB = True

DEFAULT_USE_LOCAL_KNOWLEDGE = True

DEFAULT_USE_LLM = True

###############################################################################
# Storyboard
###############################################################################

DEFAULT_SCENE_DURATION = 5

DEFAULT_FRAME_RATE = 30

###############################################################################
# Video
###############################################################################

DEFAULT_VIDEO_WIDTH = 1920

DEFAULT_VIDEO_HEIGHT = 1080

DEFAULT_VIDEO_FPS = 30

###############################################################################
# Audio
###############################################################################

DEFAULT_SAMPLE_RATE = 44100

DEFAULT_AUDIO_FORMAT = "wav"

###############################################################################
# Image
###############################################################################

DEFAULT_IMAGE_FORMAT = "png"

###############################################################################
# Supported File Extensions
###############################################################################

SUPPORTED_IMAGE_EXTENSIONS = (
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
)

SUPPORTED_VIDEO_EXTENSIONS = (
    ".mp4",
    ".mov",
)

SUPPORTED_AUDIO_EXTENSIONS = (
    ".wav",
    ".mp3",
)

SUPPORTED_DOCUMENT_EXTENSIONS = (
    ".json",
    ".yaml",
    ".yml",
    ".md",
    ".txt",
)

###############################################################################
# Environment Variables
###############################################################################

ENV_OPENAI_API_KEY = "OPENAI_API_KEY"

ENV_ANTHROPIC_API_KEY = "ANTHROPIC_API_KEY"

ENV_GOOGLE_API_KEY = "GOOGLE_API_KEY"

ENV_XAI_API_KEY = "XAI_API_KEY"

###############################################################################
# Miscellaneous
###############################################################################

EMPTY_STRING = ""

EMPTY_LIST = []

EMPTY_DICT = {}

TRUE_VALUES = {
    "true",
    "1",
    "yes",
    "on",
}

FALSE_VALUES = {
    "false",
    "0",
    "no",
    "off",
}