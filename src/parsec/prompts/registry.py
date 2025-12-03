from .template import PromptTemplate
from typing import Optional, List, Dict, Any
import yaml
from pathlib import Path

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
        if name not in self.registry:
            raise KeyError(f"Template '{name}' not found")
        
        versions = self.registry[name]
        if version is not None:
            if version not in versions:
                raise KeyError(f"Template '{name}' version '{version}' not found")
            return versions[version]
        
        latest_version = self._get_latest_version(list(versions.keys()))
        return versions[latest_version]

    def list_templates(self) -> List[str]:
        """List all template names."""
        return list(self.registry.keys())
    
    def list_versions(self, name: str) -> List[str]:
        """List all versions of a specific template."""
        if name not in self.registry:
            raise KeyError(f"Template '{name}' not found")
        return sorted(self.registry[name].keys(), key=self._version_sort_key, reverse=True)

    def exists(self, name: str, version: Optional[str] = None) -> bool:
        """Checks if template by name exists"""
        if name not in self.registry:
            return False
        if version is None:
            return True
        return version in self.registry[name]

    def delete(self, name: str, version: Optional[str] = None) -> None:
        """Delete a template or specific version"""
        if name not in self.registry:
            raise KeyError(f"Template '{name}' not found")
        
        if version is None:
            # Delete all versions
            del self.registry[name]
        else:
            # Delete specific version
            if version not in self.registry[name]:
                raise KeyError(f"Template '{name}' version '{version}' not found")
            del self.registry[name][version]
            
            # If no versions left, remove the template name
            if not self.registry[name]:
                del self.registry[name]
    

    def save_to_disk(self, path: str) -> None:
        """Save all templates to YAML file."""
        data = {}
        for name, versions in self.registry.items():
            data[name] = {}
            for version, template in versions.items():
                data[name][version] = template.to_dict()
        
        with open(path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    def load_from_disk(self, path: str) -> None:
        """Load templates from YAML file."""
        if not Path(path).exists():
            raise FileNotFoundError(f"Template file not found: {path}")

        with open(path, 'r') as f:
            data = yaml.safe_load(f)

        if not data:
            return
        
        for name, versions in data.items():
            for version, template_data in versions.items():
                template = PromptTemplate.from_dict(template_data)
                self.register(template, version)

    def _get_latest_version(self, versions: List[str]) -> str:
        """Get the latest version from a list of version strings."""
        return sorted(versions, key=self._version_sort_key, reverse=True)[0]
    
    def _version_sort_key(self, version: str):
        """Convert version string to tuple for proper sorting."""
        # Handles semantic versioning like "1.2.3"
        try:
            return tuple(map(int, version.split('.')))
        except ValueError:
            # If not numeric, fall back to string comparison
            return (0, 0, 0, version)