"""
EDIFACT Parser
Parses EDIFACT EDI files and extracts structured data.
Supports common message types: ORDERS, DESADV, INVOIC, etc.
"""

import re
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class EdifactSegment:
    """Represents an EDIFACT segment."""
    tag: str
    elements: List[List[str]] = field(default_factory=list)  # Elements can be composite
    
    def get_element(self, position: int, component: int = 0, default: str = "") -> str:
        """
        Get element at position (1-indexed).
        
        Args:
            position: Element position (1-indexed)
            component: Component position within composite element (0-indexed)
            default: Default value if not found
        """
        if 1 <= position <= len(self.elements):
            element = self.elements[position - 1]
            if isinstance(element, list):
                if component < len(element):
                    return element[component]
            else:
                if component == 0:
                    return element
        return default


@dataclass
class EdifactMessage:
    """Represents an EDIFACT message."""
    message_type: str  # e.g., "ORDERS", "DESADV", "INVOIC"
    message_version: str
    segments: List[EdifactSegment] = field(default_factory=list)
    
    def get_segments(self, tag: str) -> List[EdifactSegment]:
        """Get all segments with the given tag."""
        return [seg for seg in self.segments if seg.tag == tag]
    
    def get_segment(self, tag: str, index: int = 0) -> Optional[EdifactSegment]:
        """Get first segment with the given tag."""
        segments = self.get_segments(tag)
        if segments and index < len(segments):
            return segments[index]
        return None


@dataclass
class EdifactEnvelope:
    """Represents EDIFACT envelope structure (UNB/UNZ, UNH/UNT)."""
    unb_segment: Optional[EdifactSegment] = None
    unz_segment: Optional[EdifactSegment] = None
    messages: List[EdifactMessage] = field(default_factory=list)
    
    def get_sender_id(self) -> str:
        """Extract sender ID from UNB segment."""
        if self.unb_segment:
            return self.unb_segment.get_element(2, component=0)
        return ""
    
    def get_receiver_id(self) -> str:
        """Extract receiver ID from UNB segment."""
        if self.unb_segment:
            return self.unb_segment.get_element(3, component=0)
        return ""


class EdifactParser:
    """Parser for EDIFACT EDI files."""
    
    def __init__(self, 
                 element_separator: str = "+",
                 component_separator: str = ":",
                 segment_separator: str = "'",
                 release_character: str = "?"):
        """
        Initialize EDIFACT parser.
        
        Args:
            element_separator: Character separating elements (default: +)
            component_separator: Character separating components (default: :)
            segment_separator: Character separating segments (default: ')
            release_character: Release character for escaping (default: ?)
        """
        self.element_separator = element_separator
        self.component_separator = component_separator
        self.segment_separator = segment_separator
        self.release_character = release_character
    
    def detect_separators(self, content: str) -> tuple:
        """
        Detect separators from UNA segment if present.
        
        Args:
            content: EDI file content
            
        Returns:
            Tuple of (element_sep, component_sep, segment_sep, release_char)
        """
        # UNA segment defines service string advice
        una_match = re.search(r'UNA([^'']{6})', content[:20])
        if una_match:
            una_data = una_match.group(1)
            if len(una_data) >= 6:
                component_sep = una_data[0]
                data_sep = una_data[1]
                decimal_mark = una_data[2]
                release_char = una_data[3]
                element_sep = una_data[4]
                segment_sep = una_data[5]
                
                self.component_separator = component_sep
                self.element_separator = element_sep
                self.segment_separator = segment_sep
                self.release_character = release_char
                
                logger.info(f"Detected separators from UNA: element='{element_sep}', "
                          f"component='{component_sep}', segment='{segment_sep}', release='{release_char}'")
        
        return (self.element_separator, self.component_separator, 
                self.segment_separator, self.release_character)
    
    def parse(self, content: str) -> EdifactEnvelope:
        """
        Parse EDIFACT EDI content.
        
        Args:
            content: EDI file content as string
            
        Returns:
            EdifactEnvelope object with parsed data
        """
        if not content or not content.strip():
            raise ValueError("Empty EDI content")
        
        # Detect separators
        self.detect_separators(content)
        
        # Remove UNA segment if present (it's just metadata)
        content = re.sub(r'^UNA[^'']*' + re.escape(self.segment_separator), '', content)
        
        # Remove release characters
        content = self._remove_release_characters(content)
        
        # Split into segments
        segments_raw = content.split(self.segment_separator)
        segments = []
        
        for seg_raw in segments_raw:
            seg_raw = seg_raw.strip()
            if not seg_raw:
                continue
            
            # Extract tag (first 3 characters)
            if len(seg_raw) < 3:
                continue
            
            tag = seg_raw[:3]
            seg_data = seg_raw[3:]
            
            # Split into elements
            elements = []
            if seg_data:
                element_parts = seg_data.split(self.element_separator)
                for elem_part in element_parts:
                    if self.component_separator in elem_part:
                        # Composite element
                        components = elem_part.split(self.component_separator)
                        elements.append(components)
                    else:
                        # Simple element
                        elements.append([elem_part] if elem_part else [""])
            
            segments.append(EdifactSegment(tag=tag, elements=elements))
        
        # Build envelope structure
        envelope = EdifactEnvelope()
        
        # Find UNB/UNZ
        for seg in segments:
            if seg.tag == "UNB":
                envelope.unb_segment = seg
            elif seg.tag == "UNZ":
                envelope.unz_segment = seg
        
        # Parse messages
        current_message = None
        
        for seg in segments:
            if seg.tag == "UNH":
                # Start of message
                message_ref = seg.get_element(1)
                message_type_elem = seg.get_element(2, component=0)
                message_version = seg.get_element(2, component=1)
                
                current_message = EdifactMessage(
                    message_type=message_type_elem,
                    message_version=message_version or "D"
                )
            elif seg.tag == "UNT":
                # End of message
                if current_message:
                    envelope.messages.append(current_message)
                    current_message = None
            elif current_message:
                current_message.segments.append(seg)
        
        logger.info(f"Parsed {len(envelope.messages)} message(s)")
        return envelope
    
    def _remove_release_characters(self, content: str) -> str:
        """Remove release characters from content."""
        if not self.release_character:
            return content
        
        # Release character escapes special characters
        # Pattern: release_char + (any separator or release_char)
        special_chars = re.escape(self.element_separator) + \
                       re.escape(self.component_separator) + \
                       re.escape(self.segment_separator) + \
                       re.escape(self.release_character)
        pattern = re.escape(self.release_character) + f"([{special_chars}])"
        return re.sub(pattern, r'\1', content)
    
    def parse_file(self, filepath: str) -> EdifactEnvelope:
        """
        Parse EDIFACT EDI file.
        
        Args:
            filepath: Path to EDI file
            
        Returns:
            EdifactEnvelope object with parsed data
        """
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return self.parse(content)
        except Exception as e:
            logger.error(f"Error parsing EDIFACT file {filepath}: {e}")
            raise
    
    def extract_message_data(self, message: EdifactMessage) -> Dict[str, Any]:
        """
        Extract structured data from a message.
        
        Args:
            message: EdifactMessage object
            
        Returns:
            Dictionary with extracted data
        """
        data = {
            "message_type": message.message_type,
            "message_version": message.message_version,
            "data": {}
        }
        
        # Extract data based on message type
        if message.message_type == "ORDERS":
            data["data"] = self._extract_orders_data(message)
        elif message.message_type == "DESADV":
            data["data"] = self._extract_desadv_data(message)
        elif message.message_type == "INVOIC":
            data["data"] = self._extract_invoic_data(message)
        
        return data
    
    def _extract_orders_data(self, message: EdifactMessage) -> Dict[str, Any]:
        """Extract data from ORDERS message."""
        data = {}
        
        # BGM segment - Beginning of message
        bgm = message.get_segment("BGM")
        if bgm:
            data["order_number"] = bgm.get_element(2, component=0)
            data["order_type"] = bgm.get_element(1, component=0)
            data["order_date"] = bgm.get_element(4, component=0)
        
        # DTM segments - Date/time
        dtm_segments = message.get_segments("DTM")
        dates = {}
        for dtm in dtm_segments:
            qualifier = dtm.get_element(1, component=0)
            date_value = dtm.get_element(1, component=1)
            dates[qualifier] = date_value
        data["dates"] = dates
        
        # NAD segments - Name and address
        nad_segments = message.get_segments("NAD")
        parties = []
        for nad in nad_segments:
            party = {
                "qualifier": nad.get_element(1, component=0),
                "id": nad.get_element(2, component=0),
                "name": nad.get_element(3, component=0)
            }
            parties.append(party)
        data["parties"] = parties
        
        # LIN segments - Line items
        lin_segments = message.get_segments("LIN")
        line_items = []
        for lin in lin_segments:
            item = {
                "line_number": lin.get_element(1, component=0),
                "product_id": lin.get_element(3, component=0)
            }
            # QTY segments for quantities
            # PRI segments for prices
            line_items.append(item)
        data["line_items"] = line_items
        
        return data
    
    def _extract_desadv_data(self, message: EdifactMessage) -> Dict[str, Any]:
        """Extract data from DESADV (Despatch Advice) message."""
        data = {}
        
        # BGM segment
        bgm = message.get_segment("BGM")
        if bgm:
            data["despatch_number"] = bgm.get_element(2, component=0)
            data["despatch_type"] = bgm.get_element(1, component=0)
        
        # DTM segments
        dtm_segments = message.get_segments("DTM")
        dates = {}
        for dtm in dtm_segments:
            qualifier = dtm.get_element(1, component=0)
            date_value = dtm.get_element(1, component=1)
            dates[qualifier] = date_value
        data["dates"] = dates
        
        return data
    
    def _extract_invoic_data(self, message: EdifactMessage) -> Dict[str, Any]:
        """Extract data from INVOIC (Invoice) message."""
        data = {}
        
        # BGM segment
        bgm = message.get_segment("BGM")
        if bgm:
            data["invoice_number"] = bgm.get_element(2, component=0)
            data["invoice_type"] = bgm.get_element(1, component=0)
            data["invoice_date"] = bgm.get_element(4, component=0)
        
        # DTM segments
        dtm_segments = message.get_segments("DTM")
        dates = {}
        for dtm in dtm_segments:
            qualifier = dtm.get_element(1, component=0)
            date_value = dtm.get_element(1, component=1)
            dates[qualifier] = date_value
        data["dates"] = dates
        
        # LIN segments - Line items
        lin_segments = message.get_segments("LIN")
        line_items = []
        for lin in lin_segments:
            item = {
                "line_number": lin.get_element(1, component=0),
                "product_id": lin.get_element(3, component=0)
            }
            line_items.append(item)
        data["line_items"] = line_items
        
        return data

