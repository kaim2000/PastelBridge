# New API Endpoints Summary

## Updated Endpoints

### Invoices API (HistoryHeader)

The invoices API has been significantly expanded to include all fields from the HistoryHeader table.

**Base path:** `/api/invoices`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/invoices` | List invoices with pagination and filters |
| GET | `/api/invoices/{document_type}/{document_number}` | Get single invoice by type and number |
| GET | `/api/customers/{customer_code}/invoices` | Get all invoices for a customer |

**Key changes:**
- Now includes all 40+ fields from HistoryHeader (previously only 3 fields)
- Added document_type as part of the primary key
- Enhanced filtering options (document_type, document_number, date range, customer)
- Proper cursor-based pagination with composite keys
- Full financial data (totals, tax, discounts, currency)
- Delivery address information
- Contact details (telephone, fax, contact person)
- Status fields (printed, on hold, paid, deleted)

**Example response fields:**
```json
{
  "document_type": 3,
  "document_number": "INV123456",
  "customer_code": "CUST001",
  "document_date": "2024-01-15",
  "total": 11400.00,
  "total_tax": 1400.00,
  "del_address_01": "123 Main Street",
  "telephone": "011-123-4567",
  "contact": "John Doe",
  // ... 35+ more fields
}
```

## New Endpoints

### History Lines API (HistoryLines)

Complete line item details for all documents in the system.

**Base path:** `/api/history-lines`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/history-lines` | List history lines with pagination and filters |
| GET | `/api/history-lines/{document_type}/{document_number}/{link_num}` | Get single line item |
| GET | `/api/invoices/{document_type}/{document_number}/lines` | Get all lines for a specific invoice |

**Features:**
- Access to all 40+ fields from HistoryLines table
- Product/service details (code, description, quantities)
- Complete pricing information (unit price, cost, discounts)
- Tax calculations
- Inventory tracking fields
- Links to related documents (quotes→orders→invoices)
- Multi-store support
- Case/lot tracking

**Example response fields:**
```json
{
  "document_type": 3,
  "document_number": "INV123456",
  "link_num": 1,
  "item_code": "PROD001",
  "description": "Product Description - 1kg",
  "qty": 10.0,
  "unit_price": 100.00,
  "tax_amt": 140.00,
  "discount_amount": 0.00,
  // ... 35+ more fields
}
```

## Quick Integration Guide

### Get a complete invoice with lines:

```bash
# 1. Get invoice header
curl -X GET "https://your-server/api/invoices/3/INV123456" \
  -H "X-API-Key: your-api-key"

# 2. Get invoice lines
curl -X GET "https://your-server/api/invoices/3/INV123456/lines" \
  -H "X-API-Key: your-api-key"
```

### List recent invoices for a customer:

```bash
curl -X GET "https://your-server/api/customers/CUST001/invoices?from_date=2024-01-01" \
  -H "X-API-Key: your-api-key"
```

### Search for specific products across all documents:

```bash
curl -X GET "https://your-server/api/history-lines?item_code=PROD001" \
  -H "X-API-Key: your-api-key"
```

## Document Type Reference

Common document types in the system:
- 1: Quote
- 2: Sales Order
- 3: Invoice
- 4: Credit Note
- 5: Deposit
- 6: Returned Goods
- 8: Purchase Order

## Authentication

All endpoints require the `X-API-Key` header:
```
X-API-Key: your-api-key
```

## Rate Limits

- 30 requests per minute per IP
- 100ms minimum between requests
- Cursor-based pagination (default 50 records, max 100)

## Full Documentation

- [Invoices API Documentation](./invoices-api.md)
- [History Lines API Documentation](./history-lines-api.md)
- [API Implementation Blueprint](./api-endpoint-implementation-blueprint.md) 