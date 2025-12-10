"""
X12 EDI Parser
Parses X12 EDI files and extracts structured data.
Supports common transaction types: 850, 855, 810, 856, etc.
"""

import re
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class X12Segment:
    """Represents an X12 segment."""
    name: str
    elements: List[str] = field(default_factory=list)
    
    def get_element(self, position: int, default: str = "") -> str:
        """Get element at position (1-indexed)."""
        if 1 <= position <= len(self.elements):
            return self.elements[position - 1]
        return default


@dataclass
class X12Transaction:
    """Represents an X12 transaction set."""
    transaction_type: str  # e.g., "850", "855", "810"
    control_number: str
    segments: List[X12Segment] = field(default_factory=list)
    
    def get_segments(self, segment_name: str) -> List[X12Segment]:
        """Get all segments with the given name."""
        return [seg for seg in self.segments if seg.name == segment_name]
    
    def get_segment(self, segment_name: str, index: int = 0) -> Optional[X12Segment]:
        """Get first segment with the given name."""
        segments = self.get_segments(segment_name)
        if segments and index < len(segments):
            return segments[index]
        return None


@dataclass
class X12Envelope:
    """Represents X12 envelope structure (ISA/IEA, GS/GE, ST/SE)."""
    isa_segment: Optional[X12Segment] = None
    iea_segment: Optional[X12Segment] = None
    functional_groups: List[Dict[str, Any]] = field(default_factory=list)
    transactions: List[X12Transaction] = field(default_factory=list)
    
    def get_sender_id(self) -> str:
        """Extract sender ID from ISA segment."""
        if self.isa_segment:
            return self.isa_segment.get_element(6).strip()
        return ""
    
    def get_receiver_id(self) -> str:
        """Extract receiver ID from ISA segment."""
        if self.isa_segment:
            return self.isa_segment.get_element(8).strip()
        return ""


class X12Parser:
    """Parser for X12 EDI files."""
    
    def __init__(self, element_separator: str = "*", segment_separator: str = "~"):
        """
        Initialize X12 parser.
        
        Args:
            element_separator: Character separating elements (default: *)
            segment_separator: Character separating segments (default: ~)
        """
        self.element_separator = element_separator
        self.segment_separator = segment_separator
        self.release_character = "?"
    
    def detect_separators(self, content: str) -> tuple:
        """
        Detect element and segment separators from ISA segment.
        
        Args:
            content: EDI file content
            
        Returns:
            Tuple of (element_separator, segment_separator)
        """
        # ISA segment is always 106 characters and starts with "ISA"
        isa_match = re.search(r'ISA([^*~]{103})', content[:200])
        if isa_match:
            isa_data = isa_match.group(1)
            # Element separator is at position 0
            # Segment separator is at position 105 (after ISA + 103 chars)
            element_sep = isa_data[0] if len(isa_data) > 0 else "*"
            # Find segment separator after ISA
            segment_pos = content.find("ISA") + 3 + 103
            if segment_pos < len(content):
                segment_sep = content[segment_pos]
            else:
                segment_sep = "~"
            
            # Check for release character (usually at position 104)
            if len(isa_data) > 104:
                release_char = isa_data[104]
                if release_char and release_char not in [element_sep, segment_sep]:
                    self.release_character = release_char
            
            return element_sep, segment_sep
        
        return self.element_separator, self.segment_separator
    
    def parse(self, content: str) -> X12Envelope:
        """
        Parse X12 EDI content.
        
        Args:
            content: EDI file content as string
            
        Returns:
            X12Envelope object with parsed data
        """
        if not content or not content.strip():
            raise ValueError("Empty EDI content")
        
        # Detect separators from ISA segment
        self.element_separator, self.segment_separator = self.detect_separators(content)
        logger.info(f"Detected separators: element='{self.element_separator}', segment='{self.segment_separator}'")
        
        # Remove release characters
        content = self._remove_release_characters(content)
        
        # Split into segments
        segments_raw = content.split(self.segment_separator)
        segments = []
        
        for seg_raw in segments_raw:
            seg_raw = seg_raw.strip()
            if not seg_raw:
                continue
            
            # Split into elements
            elements = seg_raw.split(self.element_separator)
            if elements:
                segment_name = elements[0]
                segment_elements = elements[1:] if len(elements) > 1 else []
                segments.append(X12Segment(name=segment_name, elements=segment_elements))
        
        # Build envelope structure
        envelope = X12Envelope()
        
        # Find ISA/IEA
        for seg in segments:
            if seg.name == "ISA":
                envelope.isa_segment = seg
            elif seg.name == "IEA":
                envelope.iea_segment = seg
        
        # Parse functional groups and transactions
        current_group = None
        current_transaction = None
        
        for seg in segments:
            if seg.name == "GS":
                # Start of functional group
                current_group = {
                    "gs_segment": seg,
                    "ge_segment": None,
                    "transactions": []
                }
            elif seg.name == "GE":
                if current_group:
                    current_group["ge_segment"] = seg
                    envelope.functional_groups.append(current_group)
                    current_group = None
            elif seg.name == "ST":
                # Start of transaction set
                transaction_type = seg.get_element(1, "")
                control_number = seg.get_element(2, "")
                current_transaction = X12Transaction(
                    transaction_type=transaction_type,
                    control_number=control_number
                )
            elif seg.name == "SE":
                # End of transaction set
                if current_transaction:
                    envelope.transactions.append(current_transaction)
                    if current_group:
                        current_group["transactions"].append(current_transaction)
                    current_transaction = None
            elif current_transaction:
                current_transaction.segments.append(seg)
        
        logger.info(f"Parsed {len(envelope.transactions)} transaction(s)")
        return envelope
    
    def _remove_release_characters(self, content: str) -> str:
        """Remove release characters from content."""
        if not self.release_character or self.release_character == "?":
            return content
        
        # Release character escapes special characters
        # Pattern: release_char + (element_sep | segment_separator | release_char)
        pattern = re.escape(self.release_character) + f"([{re.escape(self.element_separator)}{re.escape(self.segment_separator)}{re.escape(self.release_character)}])"
        return re.sub(pattern, r'\1', content)
    
    def parse_file(self, filepath: str) -> X12Envelope:
        """
        Parse X12 EDI file.
        
        Args:
            filepath: Path to EDI file
            
        Returns:
            X12Envelope object with parsed data
        """
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return self.parse(content)
        except Exception as e:
            logger.error(f"Error parsing X12 file {filepath}: {e}")
            raise
    
    def extract_transaction_data(self, transaction: X12Transaction) -> Dict[str, Any]:
        """
        Extract structured data from a transaction.
        
        Args:
            transaction: X12Transaction object
            
        Returns:
            Dictionary with extracted data
        """
        data = {
            "transaction_type": transaction.transaction_type,
            "control_number": transaction.control_number,
            "data": {}
        }
        
        # Extract common segments based on transaction type
        if transaction.transaction_type == "850":  # Purchase Order
            data["data"] = self._extract_850_data(transaction)
        elif transaction.transaction_type == "855":  # Purchase Order Acknowledgment
            data["data"] = self._extract_855_data(transaction)
        elif transaction.transaction_type == "810":  # Invoice
            data["data"] = self._extract_810_data(transaction)
        elif transaction.transaction_type == "856":  # Ship Notice
            data["data"] = self._extract_856_data(transaction)
        
        return data
    
    def _extract_850_data(self, transaction: X12Transaction) -> Dict[str, Any]:
        """Extract data from 850 (Purchase Order) transaction."""
        data = {}
        
        # BEG segment - Beginning segment
        beg = transaction.get_segment("BEG")
        if beg:
            data["po_number"] = beg.get_element(3)
            data["po_date"] = beg.get_element(5)
            data["po_type"] = beg.get_element(2)
        
        # N1 segments - Name/Address
        n1_segments = transaction.get_segments("N1")
        parties = []
        for n1 in n1_segments:
            party = {
                "entity_id": n1.get_element(1),
                "name": n1.get_element(2)
            }
            # N2 - Additional name info
            # N3 - Address line
            # N4 - City, State, ZIP
            parties.append(party)
        data["parties"] = parties
        
        # PO1 segments - Line items
        po1_segments = transaction.get_segments("PO1")
        line_items = []
        for po1 in po1_segments:
            item = {
                "line_number": po1.get_element(1),
                "quantity": po1.get_element(2),
                "unit_price": po1.get_element(4),
                "product_id": po1.get_element(7)
            }
            line_items.append(item)
        data["line_items"] = line_items
        
        return data
    
    def _extract_855_data(self, transaction: X12Transaction) -> Dict[str, Any]:
        """Extract data from 855 (Purchase Order Acknowledgment) transaction."""
        data = {}
        
        # BAK segment - Beginning Acknowledgment
        bak = transaction.get_segment("BAK")
        if bak:
            data["po_number"] = bak.get_element(3)
            data["ack_date"] = bak.get_element(4)
            data["ack_type"] = bak.get_element(2)
        
        return data
    
    def _extract_810_data(self, transaction: X12Transaction) -> Dict[str, Any]:
        """Extract data from 810 (Invoice) transaction."""
        data = {}
        
        # BIG segment - Beginning Invoice
        big = transaction.get_segment("BIG")
        if big:
            data["invoice_number"] = big.get_element(2)
            data["invoice_date"] = big.get_element(3)
            data["po_number"] = big.get_element(4)
        
        # ITD segments - Invoice Terms
        # IT1 segments - Line items
        it1_segments = transaction.get_segments("IT1")
        line_items = []
        for it1 in it1_segments:
            item = {
                "line_number": it1.get_element(1),
                "quantity": it1.get_element(2),
                "unit_price": it1.get_element(4),
                "product_id": it1.get_element(7)
            }
            line_items.append(item)
        data["line_items"] = line_items
        
        return data
    
    def _extract_856_data(self, transaction: X12Transaction) -> Dict[str, Any]:
        """Extract data from 856 (Ship Notice) transaction."""
        data = {}
        
        # BSN segment - Beginning Ship Notice
        bsn = transaction.get_segment("BSN")
        if bsn:
            data["shipment_id"] = bsn.get_element(2)
            data["ship_date"] = bsn.get_element(3)
        
        # HL segments - Hierarchical levels
        # TD1, TD5 segments - Carrier details
        # MAN segments - Marks and numbers
        
        return data

