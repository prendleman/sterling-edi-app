"""
EDI Validator
Validates EDI files for syntax errors and business rule compliance.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

from .x12_parser import X12Parser, X12Envelope, X12Transaction
from .edifact_parser import EdifactParser, EdifactEnvelope, EdifactMessage

logger = logging.getLogger(__name__)


class ValidationLevel(Enum):
    """Validation severity levels."""
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class ValidationError:
    """Represents a validation error."""
    level: ValidationLevel
    message: str
    segment: Optional[str] = None
    position: Optional[int] = None
    rule: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of EDI validation."""
    is_valid: bool
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)
    
    def add_error(self, message: str, segment: Optional[str] = None, 
                  position: Optional[int] = None, rule: Optional[str] = None):
        """Add an error to the result."""
        error = ValidationError(
            level=ValidationLevel.ERROR,
            message=message,
            segment=segment,
            position=position,
            rule=rule
        )
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, message: str, segment: Optional[str] = None,
                    position: Optional[int] = None, rule: Optional[str] = None):
        """Add a warning to the result."""
        warning = ValidationError(
            level=ValidationLevel.WARNING,
            message=message,
            segment=segment,
            position=position,
            rule=rule
        )
        self.warnings.append(warning)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get validation summary."""
        return {
            "is_valid": self.is_valid,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": [
                {
                    "level": e.level.value,
                    "message": e.message,
                    "segment": e.segment,
                    "position": e.position,
                    "rule": e.rule
                }
                for e in self.errors
            ],
            "warnings": [
                {
                    "level": w.level.value,
                    "message": w.message,
                    "segment": w.segment,
                    "position": w.position,
                    "rule": w.rule
                }
                for w in self.warnings
            ]
        }


class EDIValidator:
    """Validator for EDI files."""
    
    def __init__(self):
        """Initialize EDI validator."""
        self.x12_parser = X12Parser()
        self.edifact_parser = EdifactParser()
    
    def validate(self, content: str, edi_type: Optional[str] = None) -> ValidationResult:
        """
        Validate EDI content.
        
        Args:
            content: EDI file content
            edi_type: EDI type ('X12' or 'EDIFACT'), auto-detected if None
            
        Returns:
            ValidationResult object
        """
        result = ValidationResult(is_valid=True)
        
        if not content or not content.strip():
            result.add_error("Empty EDI content")
            return result
        
        # Detect EDI type
        if not edi_type:
            edi_type = self._detect_edi_type(content)
        
        if edi_type == "X12":
            return self._validate_x12(content)
        elif edi_type == "EDIFACT":
            return self._validate_edifact(content)
        else:
            result.add_error(f"Unknown or unsupported EDI type: {edi_type}")
            return result
    
    def _detect_edi_type(self, content: str) -> str:
        """Detect EDI type from content."""
        content_stripped = content.strip()
        if content_stripped.startswith("ISA"):
            return "X12"
        elif content_stripped.startswith("UNB") or content_stripped.startswith("UNA"):
            return "EDIFACT"
        else:
            return "UNKNOWN"
    
    def _validate_x12(self, content: str) -> ValidationResult:
        """Validate X12 EDI content."""
        result = ValidationResult(is_valid=True)
        
        try:
            envelope = self.x12_parser.parse(content)
        except Exception as e:
            result.add_error(f"Parse error: {str(e)}")
            return result
        
        # Validate envelope structure
        if not envelope.isa_segment:
            result.add_error("Missing ISA segment (interchange header)")
        else:
            # Validate ISA segment
            if len(envelope.isa_segment.elements) < 16:
                result.add_error("ISA segment has insufficient elements (expected 16)", 
                               segment="ISA")
            
            # Check sender/receiver IDs
            sender_id = envelope.isa_segment.get_element(6).strip()
            receiver_id = envelope.isa_segment.get_element(8).strip()
            if not sender_id:
                result.add_error("Missing sender ID in ISA segment", segment="ISA")
            if not receiver_id:
                result.add_error("Missing receiver ID in ISA segment", segment="ISA")
        
        if not envelope.iea_segment:
            result.add_warning("Missing IEA segment (interchange trailer)")
        
        # Validate functional groups
        if not envelope.functional_groups:
            result.add_warning("No functional groups found")
        else:
            for group in envelope.functional_groups:
                if not group.get("gs_segment"):
                    result.add_error("Functional group missing GS segment")
                if not group.get("ge_segment"):
                    result.add_warning("Functional group missing GE segment")
        
        # Validate transactions
        if not envelope.transactions:
            result.add_warning("No transactions found")
        else:
            for transaction in envelope.transactions:
                self._validate_x12_transaction(transaction, result)
        
        return result
    
    def _validate_x12_transaction(self, transaction: X12Transaction, result: ValidationResult):
        """Validate an X12 transaction."""
        # Check for ST/SE envelope
        st_segment = transaction.get_segment("ST")
        se_segment = transaction.get_segment("SE")
        
        if not st_segment:
            result.add_error("Transaction missing ST segment", 
                           rule="ST_SE_REQUIRED")
        else:
            # Validate transaction type matches
            st_type = st_segment.get_element(1)
            if st_type != transaction.transaction_type:
                result.add_error(
                    f"Transaction type mismatch: ST segment has {st_type}, "
                    f"expected {transaction.transaction_type}",
                    segment="ST"
                )
        
        if not se_segment:
            result.add_error("Transaction missing SE segment", 
                           rule="ST_SE_REQUIRED")
        else:
            # Validate segment count in SE matches actual count
            expected_count = se_segment.get_element(1)
            actual_count = len(transaction.segments)
            if expected_count and int(expected_count) != actual_count:
                result.add_warning(
                    f"Segment count mismatch: SE indicates {expected_count}, "
                    f"actual count is {actual_count}",
                    segment="SE"
                )
        
        # Transaction-specific validations
        if transaction.transaction_type == "850":  # Purchase Order
            self._validate_850(transaction, result)
        elif transaction.transaction_type == "855":  # PO Acknowledgment
            self._validate_855(transaction, result)
        elif transaction.transaction_type == "810":  # Invoice
            self._validate_810(transaction, result)
    
    def _validate_850(self, transaction: X12Transaction, result: ValidationResult):
        """Validate 850 (Purchase Order) transaction."""
        beg = transaction.get_segment("BEG")
        if not beg:
            result.add_error("850 transaction missing BEG segment", 
                           rule="BEG_REQUIRED_850")
        else:
            po_number = beg.get_element(3)
            if not po_number:
                result.add_error("BEG segment missing purchase order number", 
                               segment="BEG")
        
        # Check for at least one line item
        po1_segments = transaction.get_segments("PO1")
        if not po1_segments:
            result.add_warning("850 transaction has no line items (PO1 segments)")
    
    def _validate_855(self, transaction: X12Transaction, result: ValidationResult):
        """Validate 855 (PO Acknowledgment) transaction."""
        bak = transaction.get_segment("BAK")
        if not bak:
            result.add_error("855 transaction missing BAK segment",
                           rule="BAK_REQUIRED_855")
    
    def _validate_810(self, transaction: X12Transaction, result: ValidationResult):
        """Validate 810 (Invoice) transaction."""
        big = transaction.get_segment("BIG")
        if not big:
            result.add_error("810 transaction missing BIG segment",
                           rule="BIG_REQUIRED_810")
        else:
            invoice_number = big.get_element(2)
            if not invoice_number:
                result.add_error("BIG segment missing invoice number",
                               segment="BIG")
    
    def _validate_edifact(self, content: str) -> ValidationResult:
        """Validate EDIFACT EDI content."""
        result = ValidationResult(is_valid=True)
        
        try:
            envelope = self.edifact_parser.parse(content)
        except Exception as e:
            result.add_error(f"Parse error: {str(e)}")
            return result
        
        # Validate envelope structure
        if not envelope.unb_segment:
            result.add_error("Missing UNB segment (interchange header)")
        else:
            # Validate UNB segment
            sender_id = envelope.unb_segment.get_element(2, component=0)
            receiver_id = envelope.unb_segment.get_element(3, component=0)
            if not sender_id:
                result.add_error("Missing sender ID in UNB segment", segment="UNB")
            if not receiver_id:
                result.add_error("Missing receiver ID in UNB segment", segment="UNB")
        
        if not envelope.unz_segment:
            result.add_warning("Missing UNZ segment (interchange trailer)")
        
        # Validate messages
        if not envelope.messages:
            result.add_warning("No messages found")
        else:
            for message in envelope.messages:
                self._validate_edifact_message(message, result)
        
        return result
    
    def _validate_edifact_message(self, message: EdifactMessage, result: ValidationResult):
        """Validate an EDIFACT message."""
        # Check for UNH/UNT envelope
        unh_segment = message.get_segment("UNH")
        unt_segment = message.get_segment("UNT")
        
        if not unh_segment:
            result.add_error("Message missing UNH segment",
                           rule="UNH_UNT_REQUIRED")
        else:
            # Validate message type
            msg_type = unh_segment.get_element(2, component=0)
            if msg_type != message.message_type:
                result.add_error(
                    f"Message type mismatch: UNH has {msg_type}, "
                    f"expected {message.message_type}",
                    segment="UNH"
                )
        
        if not unt_segment:
            result.add_error("Message missing UNT segment",
                           rule="UNH_UNT_REQUIRED")
        else:
            # Validate segment count
            expected_count = unt_segment.get_element(1, component=0)
            actual_count = len(message.segments)
            if expected_count and int(expected_count) != actual_count:
                result.add_warning(
                    f"Segment count mismatch: UNT indicates {expected_count}, "
                    f"actual count is {actual_count}",
                    segment="UNT"
                )
        
        # Message-specific validations
        if message.message_type == "ORDERS":
            self._validate_orders(message, result)
        elif message.message_type == "DESADV":
            self._validate_desadv(message, result)
        elif message.message_type == "INVOIC":
            self._validate_invoic(message, result)
    
    def _validate_orders(self, message: EdifactMessage, result: ValidationResult):
        """Validate ORDERS message."""
        bgm = message.get_segment("BGM")
        if not bgm:
            result.add_error("ORDERS message missing BGM segment",
                           rule="BGM_REQUIRED_ORDERS")
        else:
            order_number = bgm.get_element(2, component=0)
            if not order_number:
                result.add_warning("BGM segment missing order number", segment="BGM")
    
    def _validate_desadv(self, message: EdifactMessage, result: ValidationResult):
        """Validate DESADV message."""
        bgm = message.get_segment("BGM")
        if not bgm:
            result.add_error("DESADV message missing BGM segment",
                           rule="BGM_REQUIRED_DESADV")
    
    def _validate_invoic(self, message: EdifactMessage, result: ValidationResult):
        """Validate INVOIC message."""
        bgm = message.get_segment("BGM")
        if not bgm:
            result.add_error("INVOIC message missing BGM segment",
                           rule="BGM_REQUIRED_INVOIC")
        else:
            invoice_number = bgm.get_element(2, component=0)
            if not invoice_number:
                result.add_error("BGM segment missing invoice number", segment="BGM")

