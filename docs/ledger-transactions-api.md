# Ledger Transactions API Documentation

## Overview

The Ledger Transactions API provides access to general ledger transactions from the Pastel Partner accounting system. This endpoint supports extensive filtering options and pagination to efficiently query transaction data.

## Base URL

```
http://[your-server]:[port]/api
```

## Authentication

All requests require an API key in the header:

```
X-API-Key: your-api-key-here
```

## Endpoints

### 1. List Ledger Transactions

Get a paginated list of ledger transactions with optional filters.

**Endpoint:** `GET /api/ledger-transactions`

**Query Parameters:**

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `cursor` | string | Pagination cursor from previous response | `MTc3MDYzMw==` |
| `limit` | integer | Number of records to return (1-100, default: 50) | `25` |
| `gdc` | string | Filter by General/Debit/Credit flag (G/D/C) | `G` |
| `acc_number` | string | Filter by account number | `3200000` |
| `p_period` | integer | Filter by period number | `11` |
| `from_date` | date | Filter transactions from this date (YYYY-MM-DD) | `2024-04-01` |
| `to_date` | date | Filter transactions up to this date (YYYY-MM-DD) | `2024-04-30` |
| `e_type` | integer | Filter by entry type | `27` |
| `refrence` | string | Filter by reference number | `23040014` |
| `min_amount` | float | Filter by minimum amount | `100.00` |
| `max_amount` | float | Filter by maximum amount | `5000.00` |
| `description` | string | Filter by description (partial match) | `invoice` |
| `link_id` | integer | Filter by link ID | `101564` |
| `user_id` | integer | Filter by user ID | `4` |
| `transaction_id` | integer | Filter by transaction ID | `217579` |
| `link_acc` | string | Filter by linked account | `8436000` |

**Example Request:**

```bash
curl -X GET "http://localhost:8000/api/ledger-transactions?limit=10&gdc=G&p_period=11&from_date=2024-04-01&to_date=2024-04-30" \
  -H "X-API-Key: your-api-key-here"
```

**Example Response:**

```json
{
  "data": [
    {
      "auto_number": 1770633,
      "gdc": "G",
      "acc_number": "3200000",
      "disc_flag": "N",
      "curr_code": 0,
      "spare": "",
      "p_period": 11,
      "d_date": "2024-04-23",
      "e_type": 27,
      "refrence": "23040014",
      "job_code": "",
      "amount": 396.77,
      "tax_amt": 59.51,
      "this_curr_tax_amount": 59.51,
      "bank_tax_amount": 59.51,
      "curr_amt": 396.77,
      "bank_curr_amount": 396.77,
      "recon_flag": 107,
      "description": "072159626 R19627,40 14/11",
      "tax_type": 16,
      "country": "",
      "generated": "",
      "pay_based": "N",
      "user_id": 4,
      "which_user_ref": "",
      "link_acc": "8436000",
      "update_recon_flag": 0,
      "cheque_flag": 0,
      "link_id": 101564,
      "in_inv": 0,
      "tax_report_date": "2024-04-23",
      "tax_report_period": 11,
      "batch_id": 38987,
      "transaction_id": 217579,
      "exported": 0,
      "export_ref": null,
      "export_num": 0,
      "cost_sync_done": null
    }
  ],
  "metadata": {
    "page_size": 10,
    "cursor": null,
    "next_cursor": "MTc3MDYzNA==",
    "has_more": true,
    "timestamp": "2024-06-15T14:30:00Z"
  }
}
```

### 2. Get Single Ledger Transaction

Get a specific ledger transaction by its auto number.

**Endpoint:** `GET /api/ledger-transactions/{auto_number}`

**Path Parameters:**

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `auto_number` | integer | The unique auto number of the transaction | `1770633` |

**Example Request:**

```bash
curl -X GET "http://localhost:8000/api/ledger-transactions/1770633" \
  -H "X-API-Key: your-api-key-here"
```

**Example Response:**

```json
{
  "auto_number": 1770633,
  "gdc": "G",
  "acc_number": "3200000",
  "disc_flag": "N",
  "curr_code": 0,
  "spare": "",
  "p_period": 11,
  "d_date": "2024-04-23",
  "e_type": 27,
  "refrence": "23040014",
  "job_code": "",
  "amount": 396.77,
  "tax_amt": 59.51,
  "this_curr_tax_amount": 59.51,
  "bank_tax_amount": 59.51,
  "curr_amt": 396.77,
  "bank_curr_amount": 396.77,
  "recon_flag": 107,
  "description": "072159626 R19627,40 14/11",
  "tax_type": 16,
  "country": "",
  "generated": "",
  "pay_based": "N",
  "user_id": 4,
  "which_user_ref": "",
  "link_acc": "8436000",
  "update_recon_flag": 0,
  "cheque_flag": 0,
  "link_id": 101564,
  "in_inv": 0,
  "tax_report_date": "2024-04-23",
  "tax_report_period": 11,
  "batch_id": 38987,
  "transaction_id": 217579,
  "exported": 0,
  "export_ref": null,
  "export_num": 0,
  "cost_sync_done": null
}
```

## Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `auto_number` | integer | Unique auto-incrementing identifier for the transaction |
| `gdc` | string | General/Debit/Credit flag (G/D/C) |
| `acc_number` | string | General ledger account number |
| `disc_flag` | string | Discount flag |
| `curr_code` | integer | Currency code |
| `spare` | string | Spare field |
| `p_period` | integer | Period number (1-13) |
| `d_date` | date | Transaction date |
| `e_type` | integer | Entry type code |
| `refrence` | string | Reference number |
| `job_code` | string | Job/Project code |
| `amount` | float | Transaction amount |
| `tax_amt` | float | Tax amount |
| `this_curr_tax_amount` | float | Tax amount in transaction currency |
| `bank_tax_amount` | float | Tax amount in bank currency |
| `curr_amt` | float | Amount in transaction currency |
| `bank_curr_amount` | float | Amount in bank currency |
| `recon_flag` | integer | Reconciliation flag |
| `description` | string | Transaction description |
| `tax_type` | integer | Tax type code |
| `country` | string | Country code |
| `generated` | string | Generated flag |
| `pay_based` | string | Payment based flag |
| `user_id` | integer | User ID who created the transaction |
| `which_user_ref` | string | User reference |
| `link_acc` | string | Linked account number |
| `update_recon_flag` | integer | Update reconciliation flag |
| `cheque_flag` | integer | Cheque flag |
| `link_id` | integer | Link ID for related transactions |
| `in_inv` | integer | In invoice flag |
| `tax_report_date` | date | Tax report date |
| `tax_report_period` | integer | Tax report period |
| `batch_id` | integer | Batch ID |
| `transaction_id` | integer | Transaction ID |
| `exported` | integer | Export status flag |
| `export_ref` | string | Export reference |
| `export_num` | integer | Export number |
| `cost_sync_done` | string | Cost sync status |

## Common Use Cases

### 1. Get all transactions for a specific account in a period

```bash
curl -X GET "http://localhost:8000/api/ledger-transactions?acc_number=3200000&p_period=11" \
  -H "X-API-Key: your-api-key-here"
```

### 2. Get all debit transactions above a certain amount

```bash
curl -X GET "http://localhost:8000/api/ledger-transactions?gdc=D&min_amount=1000" \
  -H "X-API-Key: your-api-key-here"
```

### 3. Get transactions by date range

```bash
curl -X GET "http://localhost:8000/api/ledger-transactions?from_date=2024-04-01&to_date=2024-04-30" \
  -H "X-API-Key: your-api-key-here"
```

### 4. Search transactions by description

```bash
curl -X GET "http://localhost:8000/api/ledger-transactions?description=invoice" \
  -H "X-API-Key: your-api-key-here"
```

### 5. Get transactions by user

```bash
curl -X GET "http://localhost:8000/api/ledger-transactions?user_id=4" \
  -H "X-API-Key: your-api-key-here"
```

## Pagination

The API uses cursor-based pagination. To retrieve subsequent pages:

1. Make an initial request
2. Use the `next_cursor` value from the response metadata
3. Include it as the `cursor` parameter in the next request
4. Continue until `has_more` is false

Example:
```bash
# First page
curl -X GET "http://localhost:8000/api/ledger-transactions?limit=50" \
  -H "X-API-Key: your-api-key-here"

# Next page (using next_cursor from previous response)
curl -X GET "http://localhost:8000/api/ledger-transactions?limit=50&cursor=MTc3MDY4Mw==" \
  -H "X-API-Key: your-api-key-here"
```

## Error Responses

| Status Code | Description |
|-------------|-------------|
| 401 | Invalid or missing API key |
| 403 | IP address not whitelisted |
| 404 | Transaction not found (single record endpoint) |
| 422 | Invalid query parameters |
| 429 | Rate limit exceeded |
| 500 | Internal server error |

Example error response:
```json
{
  "detail": "Transaction not found: 999999"
}
```

## Notes

- All string fields are automatically trimmed of whitespace
- Date fields accept YYYY-MM-DD format
- The `description` filter performs a partial match (contains)
- All amount fields are returned as floats
- The API respects rate limiting configured on the server
- Transactions are ordered by `auto_number` for consistent pagination
- Integer fields containing null bytes (`\x00`) or empty values are automatically converted to 0
- This handles database inconsistencies where numeric fields might contain special characters 