# Dummy Data

This directory contains sample EDI files for testing and demonstration purposes.

## Files Included

### X12 Files

- **sample_850_2.x12** - Purchase Order (PO-2025-002)
  - 2 line items
  - Supplier: SUPPLIER001
  - Customer: FEDERATED001

- **sample_850_3.x12** - Purchase Order (PO-2025-003)
  - 3 line items
  - Supplier: SUPPLIER002
  - Customer: FEDERATED001

- **sample_855.x12** - Purchase Order Acknowledgment
  - Acknowledges PO-2025-002
  - 2 line items acknowledged

- **sample_810.x12** - Invoice
  - Invoice for PO-2025-002
  - Invoice number: INV-2025-001
  - 2 line items

- **sample_856.x12** - Ship Notice/Manifest
  - Shipment for PO-2025-002
  - Shipment number: SHIP-2025-001
  - 2 line items

### EDIFACT Files

- **sample_orders.edifact** - Purchase Order (ORDERS message)
  - PO-2025-004
  - 2 line items
  - UN/EDIFACT format

## Usage

These files can be used for:

1. **Testing the EDI processor:**
   ```bash
   python main.py process --file data/dummy/sample_850_2.x12
   ```

2. **Generating sample metrics:**
   ```bash
   python main.py dashboard --generate-sample-metrics
   ```

3. **Testing validation:**
   ```bash
   python main.py validate --file data/dummy/sample_850_2.x12
   ```

4. **Integration testing:**
   - Test Acumatica integration
   - Test eCommerce connector
   - Test SQL Server storage

## Data Characteristics

- **Trading Partners:** Multiple suppliers and Federated Group
- **Transaction Types:** 850, 855, 810, 856 (X12) and ORDERS (EDIFACT)
- **Line Items:** 1-3 items per transaction
- **Dates:** January 2025
- **Amounts:** Realistic pricing ($8.75 - $15.00 per unit)

## Notes

- All data is fictional and for demonstration purposes only
- File names follow the pattern: `sample_[transaction_type]_[number].[format]`
- Files are valid EDI format and can be processed by the application

