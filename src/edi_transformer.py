"""
EDI Transformer
Transforms EDI data between formats and applies data mappings.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from .x12_parser import X12Parser, X12Transaction
from .edifact_parser import EdifactParser, EdifactMessage

logger = logging.getLogger(__name__)


class EDITransformer:
    """Transformer for EDI data conversion and mapping."""
    
    def __init__(self):
        """Initialize EDI transformer."""
        self.x12_parser = X12Parser()
        self.edifact_parser = EdifactParser()
    
    def transform_x12_to_edifact(self, x12_content: str, 
                                  message_type: str = "ORDERS") -> str:
        """
        Transform X12 EDI to EDIFACT format.
        
        Args:
            x12_content: X12 EDI content
            message_type: Target EDIFACT message type (e.g., "ORDERS", "INVOIC")
            
        Returns:
            EDIFACT formatted string
        """
        try:
            envelope = self.x12_parser.parse(x12_content)
            if not envelope.transactions:
                raise ValueError("No transactions found in X12 content")
            
            transaction = envelope.transactions[0]
            edifact_message = self._convert_x12_transaction_to_edifact(
                transaction, message_type, envelope
            )
            
            # Build EDIFACT envelope
            edifact_content = self._build_edifact_envelope(edifact_message, envelope)
            return edifact_content
            
        except Exception as e:
            logger.error(f"Error transforming X12 to EDIFACT: {e}")
            raise
    
    def transform_edifact_to_x12(self, edifact_content: str,
                                   transaction_type: str = "850") -> str:
        """
        Transform EDIFACT EDI to X12 format.
        
        Args:
            edifact_content: EDIFACT EDI content
            transaction_type: Target X12 transaction type (e.g., "850", "810")
            
        Returns:
            X12 formatted string
        """
        try:
            envelope = self.edifact_parser.parse(edifact_content)
            if not envelope.messages:
                raise ValueError("No messages found in EDIFACT content")
            
            message = envelope.messages[0]
            x12_transaction = self._convert_edifact_message_to_x12(
                message, transaction_type, envelope
            )
            
            # Build X12 envelope
            x12_content = self._build_x12_envelope(x12_transaction, envelope)
            return x12_content
            
        except Exception as e:
            logger.error(f"Error transforming EDIFACT to X12: {e}")
            raise
    
    def _convert_x12_transaction_to_edifact(self, transaction: X12Transaction,
                                            message_type: str,
                                            x12_envelope) -> EdifactMessage:
        """Convert X12 transaction to EDIFACT message structure."""
        # This is a simplified conversion - real implementations would be more complex
        segments = []
        
        # UNH segment
        unh_elements = [
            [f"MSG{datetime.now().strftime('%Y%m%d%H%M%S')}"],  # Message reference
            [message_type, "D", "96A", "UN"]  # Message type, version, release, agency
        ]
        segments.append({"tag": "UNH", "elements": unh_elements})
        
        # BGM segment (Beginning of message)
        if transaction.transaction_type == "850":  # PO
            beg = transaction.get_segment("BEG")
            if beg:
                bgm_elements = [
                    ["220"],  # Document/message name code
                    [beg.get_element(3)],  # Document number
                    ["9"]  # Message function code
                ]
                segments.append({"tag": "BGM", "elements": bgm_elements})
        
        # DTM segments (Date/time)
        dtm_elements = [
            ["137", datetime.now().strftime("%Y%m%d")]  # Document date
        ]
        segments.append({"tag": "DTM", "elements": dtm_elements})
        
        # Convert parties (N1 segments to NAD segments)
        n1_segments = transaction.get_segments("N1")
        for n1 in n1_segments:
            nad_elements = [
                [n1.get_element(1)],  # Party qualifier
                [n1.get_element(2)],  # Party ID
                [n1.get_element(4)]  # Party name
            ]
            segments.append({"tag": "NAD", "elements": nad_elements})
        
        # Convert line items (PO1 to LIN)
        po1_segments = transaction.get_segments("PO1")
        for po1 in po1_segments:
            lin_elements = [
                [po1.get_element(1)],  # Line number
                [],  # Action request
                [po1.get_element(7)]  # Item number
            ]
            segments.append({"tag": "LIN", "elements": lin_elements})
            
            # QTY segment for quantity
            qty_elements = [
                ["21"],  # Quantity qualifier
                [po1.get_element(2)]  # Quantity
            ]
            segments.append({"tag": "QTY", "elements": qty_elements})
        
        # UNT segment (Message trailer)
        unt_elements = [
            [str(len(segments) + 1)],  # Segment count
            [unh_elements[0][0]]  # Message reference
        ]
        segments.append({"tag": "UNT", "elements": unt_elements})
        
        # Create message object (simplified - would need proper EdifactSegment objects)
        # For now, return a structure that can be used to build EDIFACT
        return {"segments": segments, "message_type": message_type}
    
    def _convert_edifact_message_to_x12(self, message: EdifactMessage,
                                        transaction_type: str,
                                        edifact_envelope) -> X12Transaction:
        """Convert EDIFACT message to X12 transaction structure."""
        # This is a simplified conversion
        segments = []
        
        # ST segment
        st_elements = [transaction_type, message.segments[0].get_element(1, component=0) if message.segments else "0001"]
        segments.append({"name": "ST", "elements": st_elements})
        
        # Convert BGM to BEG (for 850)
        if transaction_type == "850":
            bgm = message.get_segment("BGM")
            if bgm:
                beg_elements = ["00", "SA", bgm.get_element(2, component=0), "", bgm.get_element(4, component=0)]
                segments.append({"name": "BEG", "elements": beg_elements})
        
        # Convert NAD to N1
        nad_segments = message.get_segments("NAD")
        for nad in nad_segments:
            n1_elements = [
                nad.get_element(1, component=0),  # Entity identifier
                nad.get_element(2, component=0),  # Name
                "",  # ID code qualifier
                nad.get_element(3, component=0)  # ID code
            ]
            segments.append({"name": "N1", "elements": n1_elements})
        
        # Convert LIN to PO1
        lin_segments = message.get_segments("LIN")
        for lin in lin_segments:
            po1_elements = [
                lin.get_element(1, component=0),  # Line number
                "",  # Quantity (would need QTY segment)
                "",  # Unit of measure
                "",  # Unit price
                "",  # Basis of unit price
                "",  # Product/service ID qualifier
                lin.get_element(3, component=0)  # Product ID
            ]
            segments.append({"name": "PO1", "elements": po1_elements})
        
        # SE segment
        se_elements = [str(len(segments) + 1), st_elements[1]]
        segments.append({"name": "SE", "elements": se_elements})
        
        # Create transaction object (simplified)
        return {"segments": segments, "transaction_type": transaction_type}
    
    def _build_edifact_envelope(self, message_data: Dict, x12_envelope) -> str:
        """Build EDIFACT envelope string."""
        lines = []
        
        # UNA segment (service string advice) - optional but recommended
        lines.append("UNA:+.? '")
        
        # UNB segment (interchange header)
        sender_id = x12_envelope.get_sender_id() or "SENDER"
        receiver_id = x12_envelope.get_receiver_id() or "RECEIVER"
        unb_elements = [
            ["UNOA", "2"],  # Syntax identifier
            [sender_id, ""],  # Sender
            [receiver_id, ""],  # Receiver
            [datetime.now().strftime("%y%m%d"), datetime.now().strftime("%H%M")],  # Date/time
            ["0001"]  # Interchange control reference
        ]
        lines.append(self._format_edifact_segment("UNB", unb_elements))
        
        # Message segments
        for seg_data in message_data.get("segments", []):
            lines.append(self._format_edifact_segment(seg_data["tag"], seg_data["elements"]))
        
        # UNZ segment (interchange trailer)
        unz_elements = [["1"], ["0001"]]
        lines.append(self._format_edifact_segment("UNZ", unz_elements))
        
        return "\n".join(lines)
    
    def _build_x12_envelope(self, transaction_data: Dict, edifact_envelope) -> str:
        """Build X12 envelope string."""
        lines = []
        
        # ISA segment
        sender_id = edifact_envelope.get_sender_id() or "SENDER"
        receiver_id = edifact_envelope.get_receiver_id() or "RECEIVER"
        isa_elements = [
            "00",  # Authorization qualifier
            "",  # Authorization info
            "00",  # Security qualifier
            "",  # Security info
            "ZZ",  # Interchange ID qualifier
            sender_id[:15].ljust(15),  # Interchange sender ID
            "ZZ",  # Interchange ID qualifier
            receiver_id[:15].ljust(15),  # Interchange receiver ID
            datetime.now().strftime("%y%m%d"),  # Date
            datetime.now().strftime("%H%M"),  # Time
            "^",  # Interchange control standards identifier
            "00501",  # Interchange control version number
            "000000001",  # Interchange control number
            "0",  # Acknowledgment requested
            "P",  # Usage indicator
            ":"  # Component element separator
        ]
        lines.append(self._format_x12_segment("ISA", isa_elements))
        
        # GS segment
        gs_elements = [
            "PO",  # Functional identifier code
            "SENDER",  # Application sender's code
            "RECEIVER",  # Application receiver's code
            datetime.now().strftime("%Y%m%d"),  # Date
            datetime.now().strftime("%H%M%S"),  # Time
            "1",  # Group control number
            "X",  # Responsible agency code
            "005010"  # Version/release/industry identifier
        ]
        lines.append(self._format_x12_segment("GS", gs_elements))
        
        # Transaction segments
        for seg_data in transaction_data.get("segments", []):
            lines.append(self._format_x12_segment(seg_data["name"], seg_data["elements"]))
        
        # GE segment
        ge_elements = ["1", "1"]
        lines.append(self._format_x12_segment("GE", ge_elements))
        
        # IEA segment
        iea_elements = ["1", "000000001"]
        lines.append(self._format_x12_segment("IEA", iea_elements))
        
        return "\n".join(lines)
    
    def _format_edifact_segment(self, tag: str, elements: List[List[str]]) -> str:
        """Format EDIFACT segment."""
        parts = [tag]
        for elem in elements:
            if isinstance(elem, list):
                parts.append(":".join(elem))
            else:
                parts.append(str(elem))
        return "+".join(parts) + "'"
    
    def _format_x12_segment(self, name: str, elements: List[str]) -> str:
        """Format X12 segment."""
        return name + "*" + "*".join(str(e) for e in elements) + "~"
    
    def apply_mapping(self, data: Dict[str, Any], mapping_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply data mapping transformation.
        
        Args:
            data: Source data dictionary
            mapping_config: Mapping configuration
            
        Returns:
            Transformed data dictionary
        """
        result = {}
        
        for target_field, mapping in mapping_config.items():
            source_field = mapping.get("source")
            transform = mapping.get("transform")
            default = mapping.get("default")
            
            if source_field:
                value = self._get_nested_value(data, source_field)
            else:
                value = None
            
            if value is None:
                value = default
            
            if transform:
                value = self._apply_transform(value, transform)
            
            self._set_nested_value(result, target_field, value)
        
        return result
    
    def _get_nested_value(self, data: Dict, path: str) -> Any:
        """Get value from nested dictionary using dot notation."""
        keys = path.split(".")
        value = data
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        return value
    
    def _set_nested_value(self, data: Dict, path: str, value: Any):
        """Set value in nested dictionary using dot notation."""
        keys = path.split(".")
        current = data
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value
    
    def _apply_transform(self, value: Any, transform: str) -> Any:
        """Apply transformation function to value."""
        if transform == "uppercase":
            return str(value).upper()
        elif transform == "lowercase":
            return str(value).lower()
        elif transform == "trim":
            return str(value).strip()
        elif transform.startswith("date:"):
            # Date format transformation
            format_str = transform.split(":", 1)[1]
            try:
                dt = datetime.strptime(str(value), format_str)
                return dt.strftime("%Y%m%d")
            except:
                return value
        else:
            return value

