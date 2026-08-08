"""
==============================================================================
Application Enums
==============================================================================
"""

from enum import Enum


class ProviderType(str, Enum):

    LLM = "llm"

    IMAGE = "image"

    VIDEO = "video"

    AUDIO = "audio"

    MUSIC = "music"


class WorkflowStatus(str, Enum):

    PENDING = "pending"

    RUNNING = "running"

    SUCCESS = "success"

    FAILED = "failed"

    CANCELLED = "cancelled"


class GenerationStatus(str, Enum):

    CREATED = "created"

    PROCESSING = "processing"

    COMPLETED = "completed"

    FAILED = "failed"


class QualityStatus(str, Enum):

    PASS = "pass"

    WARNING = "warning"

    FAIL = "fail"


class AssetType(str, Enum):

    IMAGE = "image"

    VIDEO = "video"

    AUDIO = "audio"

    SCRIPT = "script"

    STORYBOARD = "storyboard"

    THUMBNAIL = "thumbnail"


class LogLevel(str, Enum):

    DEBUG = "DEBUG"

    INFO = "INFO"

    WARNING = "WARNING"

    ERROR = "ERROR"

    CRITICAL = "CRITICAL"