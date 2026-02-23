# 🔍 Kusto Query Assistant

An AI-powered assistant that helps you explore and query your Kusto (Azure Data Explorer) database using natural language.

## Features

- ✅ **Natural Language to KQL** - Describe what you need, get working queries
- ✅ **Schema Exploration** - Discover tables and understand your data
- ✅ **Query Execution** - Run queries and see results instantly
- ✅ **Read-Only Safety** - All modification commands are blocked
- ✅ **Interactive Learning** - Get explanations and best practices

## Setup

### 1. Install Dependencies

```powershell
cd C:\Training\Microsoft\Copilot
.\.venv\Scripts\Activate.ps1
pip install -r kusto_app\requirements.txt
```

### 2. Configure Your Database

Edit `kusto_app\main.py` and update:

```python
KUSTO_CLUSTER = "https://your-cluster.kusto.windows.net"  # Your cluster URL
KUSTO_DATABASE = "YourDatabase"  # Your database name
```

### 3. Run the Assistant

```powershell
cd kusto_app
python main.py
```

On first run, a browser window will open for Azure AD authentication.

## Usage Examples

### Explore Your Database
```
📝 You: What tables do I have?
📝 You: Show me the schema for the Events table
📝 You: Give me 5 sample rows from Metrics
```

### Write Queries
```
📝 You: Show me all errors from the last 24 hours
📝 You: Count requests by endpoint for this week
📝 You: Find the top 10 slowest API calls today
📝 You: Compare error rates between Monday and Tuesday
```

### Analyze Data
```
📝 You: What's the 95th percentile response time?
📝 You: Which users had the most failed requests?
📝 You: Show me a breakdown by department
```

## Safety Features

This assistant has **read-only access**. The following commands are blocked:
- `.drop` / `.delete` / `.purge`
- `.create` / `.alter`
- `.set` / `.append` / `.ingest`
- All data modification operations

## Quick Commands

| Command | Description |
|---------|-------------|
| `tables` | Quick list of all tables |
| `schema` | Show database connection info |
| `exit` | Quit the assistant |

## Architecture

```
┌─────────────────────────────────────┐
│         You (Natural Language)      │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│    Copilot SDK + Custom Tools       │
│    - list_tables                    │
│    - get_table_schema               │
│    - get_sample_data                │
│    - execute_query (read-only)      │
│    - validate_query                 │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│    Azure Data Explorer (Kusto)      │
│    READ-ONLY Connection             │
└─────────────────────────────────────┘
```

## Troubleshooting

### Authentication Issues
- Make sure you're logged into Azure (`az login`)
- Check you have access to the Kusto cluster
- Try interactive auth (browser popup)

### Connection Issues
- Verify cluster URL is correct
- Check network connectivity
- Ensure database name is correct

### Query Errors
- Ask the assistant to explain the error
- Check column names in schema first
- Use `validate_query` before executing
