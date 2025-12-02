import random
from pathlib import Path
import csv
import json
import re
from typing import Optional, Dict, Any, List

from .schemas import CollectedExample


class DatasetCollector:
    """Data collection for gathering training data"""

    def __init__(self, 
                 output_path: str,
                 format: str ="jsonl",
                 buffer_size: int = 10,
                 filters: Optional[Dict[str, Any]] = None,
                 auto_split: bool = False,
                 split_ratios: Optional[Dict[str, float]] = None,
                 versioning: bool = False,
                 version: Optional[str] = None
                 ):
        self.output_path = output_path
        self.format = format
        self.filters = filters
        self.auto_split = auto_split
        self.buffer_size = buffer_size
        self.versioning = versioning
        self.version = version
        self.examples_written = 0
        self.buffer = []

        if split_ratios is None:
            self.split_ratios = {"train": 0.8, "val": 0.1, "test": 0.1}
        else:
            self.split_ratios = split_ratios

        if auto_split:
            total = sum(self.split_ratios.values())
            if not (0.99 <= total <= 1.01):
                raise ValueError(f"Split ratios must sum to 1.0, got {total}")

    def collect(self, example_data: Dict[str, Any]) -> None:
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
    
    def __assign_split(self) -> str:
        rand = random.random()
        cumulative = 0.0

        for split_name, ratio in self.split_ratios.items():
            cumulative += ratio
            if rand < cumulative:
                return split_name
            
        # Fall back? Statistically impossible?
        return "train"
    
    def _get_split_path(self, split: str) -> Path:
        base_path = Path(self.output_path)

        versioned_path = self._get_versioned_path(base_path)

        if self.auto_split:
            stem = versioned_path.stem
            suffix = versioned_path.suffix
            return versioned_path.parent / f"{stem}_{split}{suffix}"
        else:
            return versioned_path

    def _write_batch(self) -> None:
        if not self.buffer:
            return
                
        if self.auto_split:
            split_groups: Dict[str, List[CollectedExample]] = {}

            for example in self.buffer:
                split = self.__assign_split()
                if split not in split_groups:
                    split_groups[split] = []
                split_groups[split].append(example)
            
            for split, examples in split_groups.items():
                output_path = self._get_split_path(split)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Temporarily replace buffer with split examples
                old_buffer = self.buffer
                self.buffer = examples
                
                if self.format == "jsonl":
                    self._write_jsonl(output_path)
                elif self.format == "json":
                    self._write_json(output_path)
                elif self.format == "csv":
                    self._write_csv(output_path)
                
                self.buffer = old_buffer
        else:
            base_path = Path(self.output_path)
            output_path = self._get_versioned_path(base_path)
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

    def _write_jsonl(self, path: Path) -> None:
        """Append examples to JSONL file"""
        mode = 'a' if path.exists() else 'w'
        with open(path, mode) as f:
            for example in self.buffer:
                # Convert to dict and write as JSON line
                json_line = example.model_dump_json()
                f.write(json_line + '\n')

    def _write_json(self, path: Path) -> None:
        """Write/update JSON file with all examples"""
        # Load existing examples if file exists
        existing = []
        if path.exists():
            with open(path, 'r') as f:
                existing = json.load(f)
        
        # Add new examples
        new_examples = [example.model_dump() for example in self.buffer]
        all_examples = existing + new_examples
        
        # Write back
        with open(path, 'w') as f:
            json.dump(all_examples, f, indent=2, default=str)

    def _write_csv(self, path: Path) -> None:
        """Append examples to CSV file"""
        # Flatten the examples for CSV
        rows = []
        for example in self.buffer:
            row = {
                'request_id': example.request_id,
                'timestamp': example.timestamp.isoformat(),
                'prompt': example.prompt,
                'schema': json.dumps(example.schema),
                'response': example.response,
                'parsed_output': json.dumps(example.parsed_output) if example.parsed_output else '',
                'success': example.success,
                'validation_errors': json.dumps(example.validation_errors),
                'metadata': json.dumps(example.metadata)
            }
            rows.append(row)
        
        # Write (append mode if exists)
        mode = 'a' if path.exists() else 'w'
        write_header = not path.exists()
        
        with open(path, mode, newline='') as f:
            if rows:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                if write_header:
                    writer.writeheader()
                writer.writerows(rows)

    def _read_all_examples(self) -> List[CollectedExample]:
        """Read all examples from current file"""
        path = Path(self.output_path)
        if not path.exists():
            return []
        
        examples = []
        
        if self.format == "jsonl":
            with open(path, 'r') as f:
                for line in f:
                    data = json.loads(line)
                    examples.append(CollectedExample(**data))
        
        elif self.format == "json":
            with open(path, 'r') as f:
                data = json.load(f)
                for item in data:
                    examples.append(CollectedExample(**item))
        
        # CSV reading is more complex, skip for now
        
        return examples

    def _get_versioned_path(self, base_path: Path) -> Path:
        if not self.versioning:
            return base_path
        
        if self.version:
            stem = base_path.stem
            suffix = base_path.suffix
            return base_path.parent / f"{stem}_v{self.version}{suffix}"
        else:
            stem = base_path.stem
            suffix = base_path.suffix
            parent = base_path.parent
            
            existing = list(parent.glob(f"{stem}_v*{suffix}"))
            if not existing:
                version_num = 1
            else:
                versions = []
                for p in existing:
                    match = re.search(rf"{stem}_v(\d+){suffix}", p.name)
                    if match:
                        versions.append(int(match.group(1)))
                version_num = max(versions) + 1 if versions else 1
            return base_path.parent / f"{stem}_v{version_num}{suffix}"

    def close(self):
        self._write_batch()
        if self.auto_split:
            print(f"Dataset collection complete: {self.examples_written} examples written (split into train/val/test)")
        else:
            print(f"Dataset collection complete: {self.examples_written} examples written to {self.output_path}")

    def export(self, output_path: str, format: str):
        examples = self._read_all_examples()

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


        