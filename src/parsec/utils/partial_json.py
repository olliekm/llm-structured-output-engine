"""
Partial JSON parser for streaming responses.

This module provides utilities to parse incomplete JSON strings that may be
generated during streaming LLM responses. It handles truncated objects, arrays,
and strings gracefully.
"""

import json
import re
from typing import Any, Optional, Dict, List, Union


class PartialJSONParser:
    """Parse incomplete JSON strings from streaming responses."""

    @staticmethod
    def parse(text: str) -> Optional[Any]:
        """
        Attempt to parse partial JSON, returning None if unparseable.

        Args:
            text: Potentially incomplete JSON string

        Returns:
            Parsed JSON object or None if parsing fails
        """
        if not text or not text.strip():
            return None

        # Try parsing as-is first
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try to fix common incomplete JSON patterns
        fixed = PartialJSONParser._attempt_fix(text)
        if fixed:
            try:
                return json.loads(fixed)
            except json.JSONDecodeError:
                pass

        return None

    @staticmethod
    def _attempt_fix(text: str) -> Optional[str]:
        """
        Attempt to fix incomplete JSON by closing brackets/braces/quotes.

        Args:
            text: Incomplete JSON string

        Returns:
            Fixed JSON string or None if unfixable
        """
        text = text.strip()
        if not text:
            return None

        # Track what needs to be closed
        stack = []
        in_string = False
        escape_next = False

        for i, char in enumerate(text):
            if escape_next:
                escape_next = False
                continue

            if char == '\\':
                escape_next = True
                continue

            if char == '"' and not in_string:
                in_string = True
                stack.append('"')
            elif char == '"' and in_string:
                in_string = False
                stack.pop()
            elif not in_string:
                if char == '{':
                    stack.append('}')
                elif char == '[':
                    stack.append(']')
                elif char == '}' and stack and stack[-1] == '}':
                    stack.pop()
                elif char == ']' and stack and stack[-1] == ']':
                    stack.pop()

        # Close any unclosed strings, arrays, or objects
        result = text
        if in_string:
            result += '"'
        result += ''.join(reversed(stack))

        return result

    @staticmethod
    def extract_field(text: str, field_name: str) -> Optional[Any]:
        """
        Extract a specific field from partial JSON.

        Args:
            field_name: Name of the field to extract
            text: Partial JSON string

        Returns:
            Value of the field or None if not found/parseable
        """
        parsed = PartialJSONParser.parse(text)
        if parsed and isinstance(parsed, dict):
            return parsed.get(field_name)
        return None

    @staticmethod
    def get_completion_percent(text: str, expected_fields: List[str]) -> float:
        """
        Estimate completion percentage based on expected fields.

        Args:
            text: Partial JSON string
            expected_fields: List of field names expected in the complete JSON

        Returns:
            Completion percentage (0.0 to 1.0)
        """
        if not expected_fields:
            return 0.0

        parsed = PartialJSONParser.parse(text)
        if not parsed or not isinstance(parsed, dict):
            return 0.0

        found_fields = sum(1 for field in expected_fields if field in parsed)
        return found_fields / len(expected_fields)

    @staticmethod
    def is_likely_complete(text: str) -> bool:
        """
        Check if JSON string appears complete (balanced brackets).

        Args:
            text: JSON string to check

        Returns:
            True if brackets/braces appear balanced
        """
        try:
            json.loads(text)
            return True
        except json.JSONDecodeError:
            return False
