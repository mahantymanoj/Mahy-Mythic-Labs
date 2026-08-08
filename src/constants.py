"""
==============================================================================
Application Constants
==============================================================================
"""

from pathlib import Path

###############################################################################
# Directories
###############################################################################

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CONFIG_DIR = PROJECT_ROOT / "config"

OUTPUT_DIR = PROJECT_ROOT / "output"

PROJECTS_DIR = PROJECT_ROOT / "projects"

CACHE_DIR = PROJECT_ROOT / "cache"

LOG_DIR = PROJECT_ROOT / "logs"

###############################################################################
# Defaults
###############################################################################

DEFAULT_LANGUAGE = "en"

DEFAULT_ENCODING = "utf-8"

DEFAULT_TIMEOUT = 120

DEFAULT_RETRIES = 3

DEFAULT_TEMPERATURE = 0.7

DEFAULT_TOP_P = 0.95

###############################################################################
# File Extensions
###############################################################################

VIDEO_EXTENSION = ".mp4"

IMAGE_EXTENSION = ".png"

AUDIO_EXTENSION = ".wav"

JSON_EXTENSION = ".json"

MARKDOWN_EXTENSION = ".md"

###############################################################################
# Supported Formats
###############################################################################

SUPPORTED_IMAGE_FORMATS = (
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
)

SUPPORTED_VIDEO_FORMATS = (
    ".mp4",
    ".mov",
)

SUPPORTED_AUDIO_FORMATS = (
    ".wav",
    ".mp3",
)