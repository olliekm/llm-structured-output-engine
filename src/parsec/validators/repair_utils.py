"""Shared JSON repair utilities for validators."""
import re


class JSONRepairUtils:
    """Utility class for common JSON repair operations."""

    @staticmethod
    def repair(output: str) -> str:
        """
        Repair common JSON formatting issues.

        Args:
            output: Raw JSON string that may have formatting issues

        Returns:
            str: Repaired JSON string

        Repairs applied:
            - Remove markdown code blocks (```json ... ```)
            - Remove trailing commas before ] or }
            - Fix smart quotes to regular quotes
            - Extract JSON from surrounding text
        """
        repaired = output

        # Remove markdown code blocks
        if repaired.startswith("```"):
            repaired = repaired.split("```")[1]
            if repaired.startswith("json"):
                repaired = repaired[4:]

        # Remove trailing commas
        repaired = JSONRepairUtils._remove_trailing_commas(repaired)

        # Fix common quote issues
        repaired = JSONRepairUtils._fix_quotes(repaired)

        # Try to extract JSON from text
        if not repaired.strip().startswith("{"):
            repaired = JSONRepairUtils._extract_json(repaired)

        return repaired

    @staticmethod
    def _remove_trailing_commas(text: str) -> str:
        """
        Remove trailing commas before closing brackets.

        Args:
            text: JSON string with potential trailing commas

        Returns:
            str: JSON string with trailing commas removed
        """
        return re.sub(r',(\s*[}\]])', r'\1', text)

    @staticmethod
    def _fix_quotes(text: str) -> str:
        """
        Fix smart quotes and other quote issues.

        Args:
            text: JSON string with potential quote issues

        Returns:
            str: JSON string with normalized quotes
        """
        # Replace smart quotes with regular quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace("'", "'").replace("'", "'")
        return text

    @staticmethod
    def _extract_json(text: str) -> str:
        """
        Try to find and extract JSON from surrounding text.

        Args:
            text: Text that may contain JSON

        Returns:
            str: Extracted JSON or original text if no JSON found
        """
        # Look for {...} or [...]
        match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
        return match.group(1) if match else text
