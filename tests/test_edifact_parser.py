"""
Unit tests for EDIFACT parser.
"""

import unittest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from edifact_parser import EdifactParser


class TestEdifactParser(unittest.TestCase):
    """Test cases for EDIFACT parser."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = EdifactParser()
        self.sample_file = Path(__file__).parent / "sample_data" / "sample_855.edifact"
    
    def test_parse_sample_orders(self):
        """Test parsing sample ORDERS message."""
        envelope = self.parser.parse_file(str(self.sample_file))
        
        self.assertIsNotNone(envelope)
        self.assertIsNotNone(envelope.unb_segment)
        self.assertEqual(len(envelope.messages), 1)
        
        message = envelope.messages[0]
        self.assertEqual(message.message_type, "ORDERS")
    
    def test_extract_message_data(self):
        """Test extracting structured data from message."""
        envelope = self.parser.parse_file(str(self.sample_file))
        message = envelope.messages[0]
        
        data = self.parser.extract_message_data(message)
        
        self.assertEqual(data["message_type"], "ORDERS")
        self.assertIn("data", data)
        self.assertIn("order_number", data["data"])
    
    def test_sender_receiver_ids(self):
        """Test extracting sender/receiver IDs."""
        envelope = self.parser.parse_file(str(self.sample_file))
        
        sender_id = envelope.get_sender_id()
        receiver_id = envelope.get_receiver_id()
        
        self.assertIn("SENDER", sender_id)
        self.assertIn("RECEIVER", receiver_id)


if __name__ == "__main__":
    unittest.main()

