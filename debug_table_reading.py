# Debug script to test table name parsing
with open('tablesindb.txt', 'r') as f:
    lines = f.readlines()
    
print(f"Total lines in file: {len(lines)}")
print("\nFirst 5 lines (with repr to show exact characters):")
for i, line in enumerate(lines[:5]):
    print(f"Line {i}: {repr(line)}")

print("\nChecking which lines match the pattern:")
tables = []
for i, line in enumerate(lines):
    if line.startswith('  - '):
        table_name = line[4:].strip()
        tables.append(table_name)
        print(f"Line {i} matches: '{table_name}'")
        
print(f"\nTotal tables found: {len(tables)}")
print(f"First 5 tables: {tables[:5]}") 