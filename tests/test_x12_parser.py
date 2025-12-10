"""
Unit tests for X12 parser.
"""

import unittest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from x12_parser import X12Parser


class TestX12Parser(unittest.TestCase):
    """Test cases for X12 parser."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = X12Parser()
        self.sample_file = Path(__file__).parent / "sample_data" / "sample_850.x12"
    
    def test_parse_sample_850(self):
        """Test parsing sample 850 file."""
        envelope = self.parser.parse_file(str(self.sample_file))
        
        self.assertIsNotNone(envelope)
        self.assertIsNotNone(envelope.isa_segment)
        self.assertEqual(len(envelope.transactions), 1)
        
        transaction = envelope.transactions[0]
        self.assertEqual(transaction.transaction_type, "850")
        
        # Check BEG segment
        beg = transaction.get_segment("BEG")
        self.assertIsNotNone(beg)
        self.assertEqual(beg.get_element(3), "PO123456")
    
    def test_extract_transaction_data(self):
        """Test extracting structured data from transaction."""
        envelope = self.parser.parse_file(str(self.sample_file))
        transaction = envelope.transactions[0]
        
        data = self.parser.extract_transaction_data(transaction)
        
        self.assertEqual(data["transaction_type"], "850")
        self.assertIn("data", data)
        self.assertIn("po_number", data["data"])
        self.assertEqual(data["data"]["po_number"], "PO123456")
    
    def test_sender_receiver_ids(self):
        """Test extracting sender/receiver IDs."""
        envelope = self.parser.parse_file(str(self.sample_file))
        
        sender_id = envelope.get_sender_id()
        receiver_id = envelope.get_receiver_id()
        
        self.assertIn("SENDERID", sender_id)
        self.assertIn("RECEIVERID", receiver_id)


if __name__ == "__main__":
    unittest.main()

