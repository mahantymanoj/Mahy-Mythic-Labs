"""
==============================================================================
Mahy Mythic Labs Studio OS

Path Resolver

Resolves project paths and filesystem locations.

Responsibilities
----------------
- Convert relative paths to absolute paths
- Expand ~ and environment variables
- Normalize paths
- Create directories
- Validate file/directory existence

Author : Mahy Mythic Labs
License: MIT
==============================================================================
"""

from __future__ import annotations

import os
from pathlib import Path


class PathResolver:
    """
    Resolve project paths.

    Example
    -------
    >>> resolver = PathResolver(project_root)

    >>> resolver.resolve("projects")
    WindowsPath('D:/Mahy/projects')

    >>> resolver.ensure_directory("output")

    >>> resolver.exists("config/settings.yaml")
    """

    # ------------------------------------------------------------------ #

    def __init__(
        self,
        project_root: Path,
    ) -> None:

        self.project_root = Path(project_root).resolve()

    # ------------------------------------------------------------------ #

    @property
    def root(self) -> Path:
        """
        Return project root.
        """

        return self.project_root

    # ------------------------------------------------------------------ #

    def resolve(
        self,
        path: str | Path,
    ) -> Path:
        """
        Resolve a path.

        Supports

        - Relative paths
        - Absolute paths
        - Environment variables
        - Home directory (~)
        """

        path = Path(
            os.path.expandvars(
                os.path.expanduser(str(path))
            )
        )

        if path.is_absolute():
            return path.resolve()

        return (self.project_root / path).resolve()

    # ------------------------------------------------------------------ #

    def ensure_directory(
        self,
        path: str | Path,
    ) -> Path:
        """
        Create directory if it does not exist.
        """

        directory = self.resolve(path)

        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        return directory

    # ------------------------------------------------------------------ #

    def ensure_parent(
        self,
        file_path: str | Path,
    ) -> Path:
        """
        Create parent directory of a file.
        """

        file_path = self.resolve(file_path)

        file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        return file_path

    # ------------------------------------------------------------------ #

    def exists(
        self,
        path: str | Path,
    ) -> bool:
        """
        Check whether path exists.
        """

        return self.resolve(path).exists()

    # ------------------------------------------------------------------ #

    def is_file(
        self,
        path: str | Path,
    ) -> bool:
        """
        Check whether path is a file.
        """

        return self.resolve(path).is_file()

    # ------------------------------------------------------------------ #

    def is_directory(
        self,
        path: str | Path,
    ) -> bool:
        """
        Check whether path is a directory.
        """

        return self.resolve(path).is_dir()

    # ------------------------------------------------------------------ #

    def relative_to_root(
        self,
        path: str | Path,
    ) -> Path:
        """
        Return path relative to project root.
        """

        return self.resolve(path).relative_to(
            self.project_root
        )

    # ------------------------------------------------------------------ #

    def join(
        self,
        *parts: str,
    ) -> Path:
        """
        Join path parts.

        Example
        -------
        >>> resolver.join("projects","demo","script.md")
        """

        path = self.project_root

        for part in parts:
            path /= part

        return path.resolve()

    # ------------------------------------------------------------------ #

    def delete(
        self,
        path: str | Path,
    ) -> None:
        """
        Delete file if it exists.
        """

        path = self.resolve(path)

        if path.is_file():
            path.unlink()

    # ------------------------------------------------------------------ #

    def touch(
        self,
        path: str | Path,
    ) -> Path:
        """
        Create an empty file.
        """

        file_path = self.ensure_parent(path)

        file_path.touch(
            exist_ok=True,
        )

        return file_path

    # ------------------------------------------------------------------ #

    def project_directory(
        self,
        project_name: str,
    ) -> Path:
        """
        Return project directory.
        """

        return self.join(
            "projects",
            project_name,
        )

    # ------------------------------------------------------------------ #

    def asset_directory(
        self,
        project_name: str,
    ) -> Path:
        """
        Return asset directory.
        """

        return self.join(
            "projects",
            project_name,
            "assets",
        )

    # ------------------------------------------------------------------ #

    def output_directory(
        self,
        project_name: str,
    ) -> Path:
        """
        Return output directory.
        """

        return self.join(
            "projects",
            project_name,
            "output",
        )

    # ------------------------------------------------------------------ #

    def cache_directory(self) -> Path:
        """
        Return cache directory.
        """

        return self.join("cache")

    # ------------------------------------------------------------------ #

    def logs_directory(self) -> Path:
        """
        Return logs directory.
        """

        return self.join("logs")

    # ------------------------------------------------------------------ #

    def config_directory(self) -> Path:
        """
        Return config directory.
        """

        return self.join("config")

    # ------------------------------------------------------------------ #

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"root='{self.project_root}')"
        )