from .registry import TemplateRegistry
from parsec.enforcement.engine import EnforcementEngine, EnforcedOutput
from typing import Optional, Any
from pathlib import Path

class TemplateManager:
    def __init__(self, registry: TemplateRegistry, engine: EnforcementEngine):
        self.registry = registry
        self.engine = engine

    async def enforce_with_template(self, 
                                    template_name: str, 
                                    variables: dict, 
                                    schema: Any,
                                    version: Optional[str] = None,
                                    **kwargs
                                    ) -> EnforcedOutput:
        """Render template and run enforcement in one call"""
        template = self.registry.get(template_name, version)
        prompt = template.render(**variables)
        return await self.engine.enforce(prompt, schema, **kwargs)
    
    def load_templates_from_directory(self, path: str) -> int:
        """Load all YAML files from directory"""
        dir_path = Path(path)
        if not dir_path.exists():
            raise FileNotFoundError(f"Template file not found: {path}")
        
        if not dir_path.is_dir():
            raise ValueError(f"Directory not found: {path}")
        
        yaml_files = list(dir_path.glob("*.yaml")) + list(dir_path.glob("*.yml"))

        if not yaml_files:
            raise ValueError(f"No YAML files found in directory: {path}")
        
        loaded_count = 0
        for yaml_file in yaml_files:
            try:
                self.registry.load_from_disk(str(yaml_file))
                loaded_count += 1
            except Exception as e:
                print(f"Warning: Failed to load {yaml_file}: {e}")
        
        return loaded_count

    def validate_all_templates(self):
        """Check all templates can be instantiated (checks structure, not rendering)."""
        validation_results = []

        for template_name in self.registry.list_templates():
            for version in self.registry.list_versions(template_name):
                try:
                    template = self.registry.get(template_name, version)
                    
                    if not template.name:
                        raise ValueError("Template missing name")
                    if not template.template:
                        raise ValueError("Template missing template string")
                    if not template.variables:
                        raise ValueError("Template missing variables")

                    validation_results.append({
                        "template": template_name,
                        "version": version,
                        "status": "valid",
                        "error": None
                    })
                    
                except Exception as e:
                    validation_results.append({
                        "template": template_name,
                        "version": version,
                        "status": "invalid",
                        "error": str(e)
                    })
        
        return validation_results
        


        

