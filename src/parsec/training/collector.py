from .schemas import CollectedExample
from typing import Optional, Dict, Any

class DatasetCollector:
    """Data collection for gathering training data"""

    def __init__(self, 
                 output_path: str,
                 format: str ="jsonl",
                 buffer_size: int = 10,
                 filters: Optional[Dict[str, Any]] = None,
                 auto_split: bool = False
                 ):
        self.output_path = output_path
        self.format = format
        self.filters = filters
        self.auto_split = auto_split
        self.buffer_size = buffer_size
        self.buffer = []

    def collect(self, example_data: Dict[str, Any]):
        self.buffer.append(example_data)
        example = CollectedExample(**example_data)

        if not self._should_save(example):
            return
        
        self.buffer.append(example)
        
        if len(self.buffer) >= self.buffer_size:
            self._write_batch()

    def _should_save(self, example: CollectedExample):
        if self.filters is None:
            return True
        
        if self.filters.get("only_successful", False):
            if not example.success:
                return False
        
        max_retries = self.filters.get("max_retries")
        if max_retries is not None:
            retries = example.metadata.get("retry_count",0)
            if retries > max_retries:
                return False
        
        return True
    
    async def _write_batch(self):
        if not self.buffer:
            return
        
        output_path = Path(self.output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if self.format == "jsonl":
            self._write_jsonl(output_path)
        elif self.format == "json":
            self._write_json(output_path)
        elif self.format == "csv":
            self._write_csv(output_path)
        else:
            raise ValueError(f"Unsupported format: {self.format}")
        
        self.examples_written += len(self.buffer)
        self.buffer.clear()

    async def close(self):
        self._write_batch()
        print(f"Dataset collection complete: {self.examples_written} exmaples written to {self.output_path}")

    def export(self, output_path: str, format: str):
        examples = self._read_all_exmaples()

        old_buffer = self.buffer
        old_path = self.output_path
        old_format = self.format

        self.buffer = examples
        self.output_path = output_path
        self.format = format

        self._write_batch()

        self.buffer = old_buffer
        self.output_path = old_path
        self.format = old_format

        