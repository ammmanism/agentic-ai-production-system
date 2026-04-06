"""Versioned prompt manager — loads and renders YAML prompt templates."""
from __future__ import annotations

import logging
import os
from pathlib import Path
from string import Template
from typing import Any, Dict, Optional

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None  # type: ignore

logger = logging.getLogger(__name__)

TEMPLATES_DIR = Path(__file__).parent / "templates"


class PromptManager:
    """Load, version, and render YAML prompt templates."""

    def __init__(self, templates_dir: Optional[Path] = None):
        self._dir = templates_dir or TEMPLATES_DIR
        self._cache: Dict[str, Dict[str, Any]] = {}

    def _load(self, name: str) -> Dict[str, Any]:
        if name in self._cache:
            return self._cache[name]

        path = self._dir / f"{name}.yaml"
        if not path.exists():
            raise FileNotFoundError(f"Prompt template not found: {path}")

        if yaml is None:
            raise ImportError("PyYAML is required for PromptManager. Install: pip install pyyaml")

        with open(path, encoding="utf-8") as fh:
            data = yaml.safe_load(fh)

        self._cache[name] = data
        return data

    def render(self, name: str, **variables: Any) -> str:
        """
        Load *name*.yaml and substitute *variables* into the template string.

        Template syntax uses Python's string.Template ($variable or ${variable}).
        """
        data = self._load(name)
        template_str = data.get("template", "")
        return Template(template_str).safe_substitute(**variables)

    def get_system_prompt(self, name: str) -> str:
        data = self._load(name)
        return data.get("system", "")

    def list_templates(self) -> list[str]:
        return [p.stem for p in self._dir.glob("*.yaml")]
