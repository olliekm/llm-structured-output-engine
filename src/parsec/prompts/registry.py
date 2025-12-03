from .template import PromptTemplate
from typing import Optional, List

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