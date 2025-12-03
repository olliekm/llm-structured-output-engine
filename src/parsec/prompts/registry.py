from .template import PromptTemplate
from typing import Optional, List, Dict

class TemplateRegistry:

    def __init__(self):
        # Structure: {name: {version: template}}
        self.registry = {}

    def register(self, template: PromptTemplate, version: str):
        """Add template to the registry"""
        name = template.name

        if name not in self.registry:
            self.registry[name] = {}

        if version in self.registry[name]:
            raise ValueError(f"Template '{name}' version '{version}' already exists")

        self.registry[template.name][version] = template

    def get(self, name: str, version: Optional[str] = None) -> PromptTemplate:
        """Get template by name and optional version (latest if not specified)."""
        pass