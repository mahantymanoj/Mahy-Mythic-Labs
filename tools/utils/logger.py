"""Consistent logging configuration for Mahy Mythic Labs tools."""

from __future__ import annotations

import logging
from pathlib import Path


def get_logger(
    name: str,
    *,
    log_directory: str | Path = "logs",
    level: int = logging.INFO,
) -> logging.Logger:
    """Return a named logger with console and UTF-8 file output."""
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(level)
    logger.propagate = False

    log_path = Path(log_directory)
    log_path.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(
        log_path / f"{name.replace('.', '-')}.log",
        encoding="utf-8",
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger