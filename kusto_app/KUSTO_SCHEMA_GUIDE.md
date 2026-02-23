# 🔍 Kusto Query Assistant - Schema Configuration

## How to Configure Your Database Schema

The Kusto Assistant needs to know your database structure to give you accurate queries.

### Option 1: Edit the Schema Directly

Open `kusto_assistant.py` and update the `DATABASE_SCHEMA` variable with your actual tables.

### Option 2: Export Schema from Azure Data Explorer

Run this query in Azure Data Explorer to get your schema:

```kql
// Get all tables and their columns
.show database schema as json
```

Or for a specific table:
```kql
.show table YourTableName schema as json
```

### Option 3: Use This Template

Copy this template for each table in your database:

```markdown
### Table: YourTableName
| Column | Type | Description |
|--------|------|-------------|
| ColumnName1 | datetime | Description of what this column contains |
| ColumnName2 | string | Description of what this column contains |
| ColumnName3 | int | Description of what this column contains |
| ColumnName4 | dynamic | JSON field containing... |
```

### Common Kusto Data Types
- `string` - Text values
- `int` / `long` - Integer numbers
- `real` / `double` - Decimal numbers
- `datetime` - Date and time values
- `bool` - True/False values
- `dynamic` - JSON objects or arrays
- `guid` - Unique identifiers
- `timespan` - Duration values

---

## Your Database Schema (FILL THIS IN)

Paste your actual schema below, then copy it into `kusto_assistant.py`:

```markdown
## Database: [YOUR_DATABASE_NAME]

### Table: [TABLE_1_NAME]
| Column | Type | Description |
|--------|------|-------------|
| | | |

### Table: [TABLE_2_NAME]  
| Column | Type | Description |
|--------|------|-------------|
| | | |

### Common Relationships:
- Table1.ColumnX → Table2.ColumnY
```

---

## Tips for Better Results

1. **Include descriptions** - The more context you provide about what each column contains, the better queries the assistant can write.

2. **Document relationships** - Note which columns can be used to join tables.

3. **Add sample values** - If helpful, include example values:
   ```
   | Status | string | Request status: "Success", "Failed", "Pending" |
   ```

4. **Note special patterns** - If columns follow patterns, document them:
   ```
   | ErrorCode | string | Format: "ERR_XXX_NNN" where XXX is category |
   ```
