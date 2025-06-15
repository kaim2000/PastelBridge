#!/usr/bin/env python3
"""Test field name conversion to identify the mismatch issue"""

# Test the current conversion logic
test_fields = [
    "BalanceThis01",
    "BalanceThis02", 
    "PostAddress01",
    "PostAddress02",
    "SalesThis01",
    "CurrBalanceThis01",
    "UserDefined01",
    "Ageing01"
]

print("Testing current conversion logic:")
print("=" * 60)

for field in test_fields:
    # Current conversion logic from customers.py
    snake_case = ''.join(['_' + c.lower() if c.isupper() else c for c in field]).lstrip('_')
    print(f"{field:20} -> {snake_case}")

print("\n" + "=" * 60)
print("\nExpected field names in the Pydantic model:")
print("balance_this_01, balance_this_02, post_address_01, etc.")
print("\nThe issue: Numbers are not getting underscores before them!")

# Let's create a better conversion function
def to_snake_case(name):
    """Convert CamelCase with numbers to snake_case properly"""
    import re
    # Insert underscore before uppercase letters
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    # Insert underscore before numbers
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
    # Insert underscore between letter and number
    s3 = re.sub('([a-zA-Z])(\d)', r'\1_\2', s2)
    return s3.lower()

print("\n" + "=" * 60)
print("\nTesting improved conversion logic:")
print("=" * 60)

for field in test_fields:
    snake_case = to_snake_case(field)
    print(f"{field:20} -> {snake_case}") 