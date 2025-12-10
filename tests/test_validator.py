"""
Unit tests for EDI validator.
"""

import unittest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from edi_validator import EDIValidator


class TestEDIValidator(unittest.TestCase):
    """Test cases for EDI validator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = EDIValidator()
        self.sample_x12 = Path(__file__).parent / "sample_data" / "sample_850.x12"
        self.sample_edifact = Path(__file__).parent / "sample_data" / "sample_855.edifact"
    
    def test_validate_x12(self):
        """Test validating X12 file."""
        with open(self.sample_x12, 'r', encoding='utf-8') as f:
            content = f.read()
        
        result = self.validator.validate(content, "X12")
        
        self.assertIsNotNone(result)
        # Sample file should be valid
        self.assertTrue(result.is_valid or len(result.errors) == 0)
    
    def test_validate_edifact(self):
        """Test validating EDIFACT file."""
        with open(self.sample_edifact, 'r', encoding='utf-8') as f:
            content = f.read()
        
        result = self.validator.validate(content, "EDIFACT")
        
        self.assertIsNotNone(result)
        # Sample file should be valid
        self.assertTrue(result.is_valid or len(result.errors) == 0)
    
    def test_validate_invalid_content(self):
        """Test validating invalid content."""
        invalid_content = "This is not valid EDI"
        
        result = self.validator.validate(invalid_content)
        
        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.errors), 0)
    
    def test_validate_empty_content(self):
        """Test validating empty content."""
        result = self.validator.validate("")
        
        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.errors), 0)


if __name__ == "__main__":
    unittest.main()

