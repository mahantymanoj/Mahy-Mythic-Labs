"""
==============================================================================
Common Type Aliases
==============================================================================
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Mapping, MutableMapping, Sequence

JSON = Dict[str, Any]

JSONObject = Dict[str, Any]

JSONList = List[Any]

ConfigDict = Dict[str, Any]

Metadata = Dict[str, Any]

Context = Dict[str, Any]

ResearchResult = Dict[str, Any]

ScriptResult = Dict[str, Any]

StoryboardResult = Dict[str, Any]

GenerationResult = Dict[str, Any]

ProviderResponse = Dict[str, Any]

WorkflowContext = Dict[str, Any]

PathLike = str | Path

Headers = Mapping[str, str]

MutableHeaders = MutableMapping[str, str]

StringList = List[str]

AnyList = List[Any]

AnySequence = Sequence[Any]