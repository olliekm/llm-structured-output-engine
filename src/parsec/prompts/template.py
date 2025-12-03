from typing import Dict, Any, List

class PromptTemplate:

    def __init__(self, 
                 name: str, 
                 template: str, 
                 variables: Dict[str, type],
                 required: List[str],
                 defaults: Dict[str, Any] = None
                 ):
    
        self.name = name
        self.template = template
        self.variables = variables
        self.required = required
        self.defaults = defaults or {}

        for req in required:
            if req not in variables:
                raise ValueError(f"Required variable '{req}' not defined in variables")
    
    def render(self, **kwargs):
        values = {**self.defaults, **kwargs}

        missing = [var for var in self.required if var not in values] # get all missing values
        if missing:
            raise ValueError(f"Missing required variables: {missing}")
        
        for var_name, var_type in self.variables.items():
            if var_name in values and not isinstance(values[var_name], var_type):
                raise TypeError(
                    f"Variable '{var_name}' expected {var_type.__name__}, "
                    f"got {type(values[var_name]).__name__}"
                )

        try:
            rendered = self.template.format(**values)
        except KeyError as e:
            raise ValueError(f"Template references undefined variables: {e}")


        return rendered

    def to_dict(self) -> Dict[str, Any]:
        """Serialize template to dictionary."""
        return {
            "name": self.name,
            "template": self.template,
            "variables": {k: v.__name__ for k, v in self.variables.items()},
            "required": self.required,
            "defaults": self.defaults
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PromptTemplate':
        """Deserialize template from dictionary."""
        type_map = {
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "list": list,
            "dict": dict
        }
        
        variables = {
            k: type_map.get(v, str) 
            for k, v in data["variables"].items()
        }
        
        return cls(
            name=data["name"],
            template=data["template"],
            variables=variables,
            required=data["required"],
            defaults=data.get("defaults")
        )
    