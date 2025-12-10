# Acumatica ERP & CRM Integration (Illustrative)

> **Tier 2 – Stubbed/Illustrative**: This module demonstrates integration patterns for Acumatica ERP/CRM. It is a demonstration scaffold and not production-certified.

## Overview

This module illustrates integration patterns for connecting EDI processing with Acumatica ERP and CRM systems. It demonstrates how EDI transactions can be synchronized with enterprise systems, but is **not production-ready** and should not be used in production environments without proper certification and testing.

## ERP Functionality (Illustrative Patterns)

- **REST API Integration**: Illustrative Acumatica REST client patterns
- **EDI Transaction Sync**: Demonstrates patterns for syncing EDI 850 (PO) and 810 (Invoice) to Acumatica
- **Sales Orders**: Patterns for creating and managing sales orders
- **Purchase Orders**: Patterns for creating and managing purchase orders
- **Inventory Management**: Patterns for querying inventory items and quantities
- **Customer/Vendor Management**: Patterns for accessing customer and vendor data
- **Financial Transactions**: Patterns for querying AR/AP transactions

## CRM Functionality (Acumatica Built-in CRM)

- **Contacts**: Patterns for creating, reading, and managing contacts
- **Opportunities**: Patterns for opportunity lifecycle management (create, update, pipeline tracking)
- **Activities**: Patterns for logging calls, meetings, tasks, and EDI processing activities
- **Cases**: Patterns for creating and managing support cases
- **Leads**: Patterns for lead management with conversion to opportunities
- **Accounts**: Patterns for account management with 360-degree view
- **Sales Pipeline**: Patterns for pipeline summary and analytics
- **Account 360 View**: Patterns for combining CRM + ERP data for account insights

## CRM Integration Features (Demonstration Patterns)

- **EDI-to-CRM Sync**: Demonstrates patterns for syncing EDI customer data to CRM contacts/accounts
- **Opportunity Creation**: Demonstrates patterns for creating CRM opportunities from EDI 850 Purchase Orders
- **Activity Logging**: Demonstrates patterns for logging EDI processing as CRM activities
- **Account 360 View**: Demonstrates patterns for getting complete account view combining CRM and ERP data

## Configuration

Edit `config/acumatica_config.yaml`:

```yaml
acumatica:
  enabled: true
  base_url: "https://your-acumatica-instance.com"
  username: "your_username"
  password: "your_password"
  auto_sync: true  # Auto-sync EDI transactions (demonstration only)
```

## Important Notes

- This is **illustrative code** demonstrating integration patterns
- **Not production-certified** - requires proper testing and certification for production use
- **Not a replacement** for established Acumatica integration tools
- In production, use certified Acumatica integration solutions and follow Acumatica best practices

## Usage

See `examples/integration_examples.py` for demonstration patterns of how to use the Acumatica connector.

