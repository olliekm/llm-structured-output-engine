import pytest
import json
import csv
import os
import tempfile
from pathlib import Path
from parsec.training import DatasetCollector, CollectedExample

@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname

@pytest.fixture
def sample_example():
    return {
            "prompt": "My name is John, I am 31",
            "json_schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer"}
                }
            },
            "response": '{"name": "John", "age": 31}',  # Valid JSON
            "parsed_output": {"name": "John", "age": 31},  # Parsed result
            "success": True,
            "validation_errors": [],
            "metadata": {
                "retry_count": 0,
                "tokens_used": 150,
                "latency_ms": 342.5
            }
        }

class TestBasicCollection:

    def test_collect_and_write_jsonl(self, temp_dir, sample_example):
        output_path = Path(temp_dir) / "dataset.jsonl"

        collector = DatasetCollector(
            output_path=str(output_path),
            format="jsonl", # Default but being explicit
            buffer_size=10 # Default but being explicit
            )
        
        collector.collect(sample_example)
        collector.close()

        with open(output_path, 'r') as f:
            lines = f.readlines()
            
            assert len(lines) == 1

            data = json.loads(lines[0])
            assert data["prompt"] == sample_example["prompt"]
            assert data["success"] == True

    def test_collect_and_write_json(self, temp_dir, sample_example):
        output_path = Path(temp_dir) / "dataset.json"

        collector = DatasetCollector(
            output_path=str(output_path),
            format="json",
            buffer_size=10 # Default but being explicit
            )
        
        collector.collect(sample_example)
        collector.close()

        with open(output_path, 'r') as f:
            data_array = json.load(f)
            
            assert len(data_array) == 1
            assert data_array[0]["prompt"] == sample_example["prompt"]
            assert data_array[0]["success"] == True
    
    def test_collect_and_write_csv(self, temp_dir, sample_example):
        output_path = Path(temp_dir) / "dataset.csv"

        collector = DatasetCollector(
            output_path=str(output_path),
            format="csv",
            buffer_size=10 # Default but being explicit
            )
        
        collector.collect(sample_example)
        collector.close()

        with open(output_path, 'r') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            rows = list(csv_reader)
                        
            assert len(rows) == 1

            assert rows[0]["prompt"] == sample_example["prompt"]
            assert rows[0]["success"] == "True"

            parsed = json.loads(rows[0]["parsed_output"])
            assert parsed == sample_example["parsed_output"]

class TestBuffering:
    """Test buffer behavior"""
    
    def test_buffer_auto_flush(self, temp_dir, sample_example):
        """Test that buffer flushes when it reaches buffer_size"""
        output_path = Path(temp_dir) / "dataset.jsonl"
        
        collector = DatasetCollector(
            output_path=str(output_path),
            format="jsonl",
            buffer_size=2  # Small buffer
        )
        
        # Add 2 examples - should trigger auto flush
        collector.collect(sample_example)
        collector.collect(sample_example)
        
        # Check file exists and has 2 lines (before close)
        assert output_path.exists()
        with open(output_path) as f:
            assert len(f.readlines()) == 2
        
        collector.close()


class TestFiltering:
    """Test quality filtering"""
    
    def test_filter_only_successful(self, temp_dir, sample_example):
        """Test only_successful filter rejects failed examples"""
        output_path = Path(temp_dir) / "dataset.jsonl"
        
        collector = DatasetCollector(
            output_path=str(output_path),
            format="jsonl",
            filters={"only_successful": True}
        )
        
        # Add successful example
        collector.collect(sample_example)
        
        # Add failed example
        failed_example = sample_example.copy()
        failed_example["success"] = False
        failed_example["validation_errors"] = ["Some error"]
        collector.collect(failed_example)
        
        collector.close()
        
        # Should only have 1 line (the successful one)
        with open(output_path) as f:
            lines = f.readlines()
            assert len(lines) == 1
            data = json.loads(lines[0])
            assert data["success"] == True
    
    def test_filter_max_retries(self, temp_dir, sample_example):
        """Test max_retries filter rejects high-retry examples"""
        output_path = Path(temp_dir) / "dataset.jsonl"
        
        collector = DatasetCollector(
            output_path=str(output_path),
            format="jsonl",
            filters={"max_retries": 1}
        )
        
        # Add example with 0 retries (should pass)
        low_retry = sample_example.copy()
        low_retry["metadata"]["retry_count"] = 0
        collector.collect(low_retry)
        
        # Add example with 2 retries (should be filtered)
        high_retry = sample_example.copy()
        high_retry["metadata"]["retry_count"] = 2
        collector.collect(high_retry)
        
        collector.close()
        
        # Should only have 1 line (the low retry one)
        with open(output_path) as f:
            lines = f.readlines()
            assert len(lines) == 1

class TestAutoSplit:
    """Test auto-splitting functionality"""
    
    def test_auto_split_creates_files(self, temp_dir, sample_example):
        """Test that auto_split creates train/val/test files"""
        output_path = Path(temp_dir) / "dataset.jsonl"
        
        collector = DatasetCollector(
            output_path=str(output_path),
            format="jsonl",
            auto_split=True,
            split_ratios={"train": 0.8, "val": 0.1, "test": 0.1}
        )
        
        # Add multiple examples to ensure all splits get some data
        for _ in range(20):
            collector.collect(sample_example)
        
        collector.close()
        
        # Check that split files exist
        train_path = Path(temp_dir) / "dataset_train.jsonl"
        val_path = Path(temp_dir) / "dataset_val.jsonl"
        test_path = Path(temp_dir) / "dataset_test.jsonl"
        
        # At least one of them should exist (probabilistic)
        split_files = [train_path, val_path, test_path]
        existing_files = [f for f in split_files if f.exists()]
        assert len(existing_files) > 0

class TestVersioning:
    """Test versioning functionality"""
    
    def test_versioning_explicit(self, temp_dir, sample_example):
        """Test explicit version number"""
        output_path = Path(temp_dir) / "dataset.jsonl"
        
        collector = DatasetCollector(
            output_path=str(output_path),
            format="jsonl",
            versioning=True,
            version="2"
        )
        
        collector.collect(sample_example)
        collector.close()
        
        # Check versioned file exists
        versioned_path = Path(temp_dir) / "dataset_v2.jsonl"
        assert versioned_path.exists()
        assert not output_path.exists()  # Original path shouldn't exist
    
    def test_versioning_auto_increment(self, temp_dir, sample_example):
        """Test auto-incrementing version"""
        output_path = Path(temp_dir) / "dataset.jsonl"
        
        # Create v1 first
        collector1 = DatasetCollector(
            output_path=str(output_path),
            format="jsonl",
            versioning=True
        )
        collector1.collect(sample_example)
        collector1.close()
        
        # Create v2 (should auto-increment)
        collector2 = DatasetCollector(
            output_path=str(output_path),
            format="jsonl",
            versioning=True
        )
        collector2.collect(sample_example)
        collector2.close()
        
        # Check both versions exist
        v1_path = Path(temp_dir) / "dataset_v1.jsonl"
        v2_path = Path(temp_dir) / "dataset_v2.jsonl"
        assert v1_path.exists()
        assert v2_path.exists()

class TestCSVReadingAndExport:
    """Test CSV reading functionality"""

    def test_read_csv_examples(self, temp_dir, sample_example):
        """Test that CSV files can be read back correctly"""
        output_path = Path(temp_dir) / "dataset.csv"

        # Write CSV data
        collector = DatasetCollector(
            output_path=str(output_path),
            format="csv",
            buffer_size=5
        )

        collector.collect(sample_example)
        collector.close()

        # Read it back
        examples = collector._read_all_examples()

        assert len(examples) == 1
        assert examples[0].prompt == sample_example["prompt"]
        assert examples[0].success == sample_example["success"]
        assert examples[0].parsed_output == sample_example["parsed_output"]
        assert examples[0].json_schema == sample_example["json_schema"]
        assert examples[0].metadata == sample_example["metadata"]
        assert examples[0].validation_errors == sample_example["validation_errors"]

    def test_export_csv_to_json(self, temp_dir, sample_example):
        """Test exporting from CSV to JSON format"""
        csv_path = Path(temp_dir) / "dataset.csv"
        json_path = Path(temp_dir) / "dataset_exported.json"

        # Write CSV data
        collector = DatasetCollector(
            output_path=str(csv_path),
            format="csv",
            buffer_size=5
        )

        collector.collect(sample_example)
        collector.close()

        # Export to JSON
        collector.export(str(json_path), format="json")

        # Verify JSON file
        assert json_path.exists()
        with open(json_path, 'r') as f:
            data = json.load(f)
            assert len(data) == 1
            assert data[0]["prompt"] == sample_example["prompt"]
            assert data[0]["success"] == sample_example["success"]

    def test_export_csv_to_jsonl(self, temp_dir, sample_example):
        """Test exporting from CSV to JSONL format"""
        csv_path = Path(temp_dir) / "dataset.csv"
        jsonl_path = Path(temp_dir) / "dataset_exported.jsonl"

        # Write CSV data
        collector = DatasetCollector(
            output_path=str(csv_path),
            format="csv",
            buffer_size=5
        )

        collector.collect(sample_example)
        collector.close()

        # Export to JSONL
        collector.export(str(jsonl_path), format="jsonl")

        # Verify JSONL file
        assert jsonl_path.exists()
        with open(jsonl_path, 'r') as f:
            lines = f.readlines()
            assert len(lines) == 1
            data = json.loads(lines[0])
            assert data["prompt"] == sample_example["prompt"]
            assert data["success"] == sample_example["success"]