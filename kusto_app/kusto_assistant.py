"""
🔍 Kusto Query Assistant
An AI-powered agent that helps you write KQL queries for your database.

Features:
- Understands Kusto Query Language (KQL) syntax
- Knows your database schema (tables, columns, types)
- Translates natural language to KQL
- Explains query results and suggests optimizations
"""
import asyncio
import os
import sys
from copilot import CopilotClient
from copilot.generated.session_events import SessionEventType

# Full path to Copilot CLI (set COPILOT_CLI_PATH env var or update this default)
COPILOT_CLI_PATH = os.getenv("COPILOT_CLI_PATH", "copilot.exe")

# =============================================================================
# DATABASE SCHEMA - Add your actual tables here!
# =============================================================================
# This is a sample schema - REPLACE with your actual Kusto database schema
# You can export this from Azure Data Explorer or ask your team

DATABASE_SCHEMA = """
## Database: YourDatabaseName

### Table: Events
| Column | Type | Description |
|--------|------|-------------|
| Timestamp | datetime | When the event occurred |
| EventType | string | Type of event (Error, Warning, Info) |
| Source | string | Source system or component |
| Message | string | Event message/description |
| UserId | string | User identifier |
| SessionId | string | Session identifier |
| Properties | dynamic | Additional JSON properties |

### Table: Users
| Column | Type | Description |
|--------|------|-------------|
| UserId | string | Unique user identifier |
| Email | string | User email |
| Department | string | Department name |
| CreatedDate | datetime | Account creation date |
| IsActive | bool | Whether user is active |

### Table: Metrics
| Column | Type | Description |
|--------|------|-------------|
| Timestamp | datetime | Metric timestamp |
| MetricName | string | Name of the metric |
| Value | real | Metric value |
| Dimensions | dynamic | Dimension key-value pairs |
| Source | string | Source of the metric |

### Table: Requests
| Column | Type | Description |
|--------|------|-------------|
| Timestamp | datetime | Request timestamp |
| RequestId | string | Unique request ID |
| Endpoint | string | API endpoint called |
| Method | string | HTTP method (GET, POST, etc.) |
| StatusCode | int | HTTP response status code |
| DurationMs | real | Request duration in milliseconds |
| UserId | string | User who made the request |
| ResponseSize | long | Response size in bytes |

### Common Relationships:
- Events.UserId → Users.UserId
- Requests.UserId → Users.UserId
- Events and Requests can be correlated by Timestamp ranges
"""

# =============================================================================
# KQL KNOWLEDGE BASE
# =============================================================================
KQL_KNOWLEDGE = """
## Kusto Query Language (KQL) Quick Reference

### Basic Query Structure
```kql
TableName
| where Condition
| project Column1, Column2
| order by Column desc
| take 100
```

### Time Filters (MOST COMMON)
```kql
| where Timestamp > ago(1h)      // Last hour
| where Timestamp > ago(1d)      // Last day  
| where Timestamp > ago(7d)      // Last week
| where Timestamp > ago(30d)     // Last month
| where Timestamp between (datetime(2024-01-01) .. datetime(2024-01-31))
```

### Common Operators
```kql
| where Column == "value"           // Exact match
| where Column != "value"           // Not equal
| where Column contains "text"      // Contains (case-insensitive)
| where Column has "word"           // Contains word
| where Column startswith "prefix"  // Starts with
| where Column matches regex "pattern"
| where Column in ("val1", "val2")  // In list
| where isnotempty(Column)          // Not null/empty
```

### Aggregations
```kql
| summarize count() by Column                    // Count by group
| summarize sum(Value) by Column                 // Sum by group
| summarize avg(Value), min(Value), max(Value)   // Statistics
| summarize dcount(UserId)                       // Distinct count
| summarize percentile(DurationMs, 95)           // Percentiles
| summarize CountByHour=count() by bin(Timestamp, 1h)  // Time buckets
```

### Joins
```kql
Table1
| join kind=inner (Table2) on UserId
| join kind=leftouter (Table2) on $left.Id == $right.UserId
```

### Useful Functions
```kql
| extend NewColumn = Expression           // Add column
| project Column1, Column2                // Select columns
| project-away UnwantedColumn             // Remove column
| distinct Column                         // Unique values
| top 10 by Value desc                    // Top N
| order by Timestamp desc                 // Sort
| take 100                                // Limit rows
| parse Message with * "error:" ErrorMsg  // Parse strings
| mv-expand Properties                    // Expand arrays
```

### Dynamic/JSON Columns
```kql
| extend Value = Properties.fieldName        // Access JSON field
| extend Value = Properties["field-name"]    // Field with special chars
| mv-expand Properties                       // Expand array
```

### Best Practices
1. Always filter by time FIRST - it's the most efficient filter
2. Use 'has' instead of 'contains' when possible (faster)
3. Avoid 'select *' - use 'project' to select only needed columns
4. Use 'take' during development to limit results
5. Put most selective filters first
"""

# =============================================================================
# SYSTEM PROMPT FOR THE AGENT
# =============================================================================
KUSTO_AGENT_PROMPT = f"""You are an expert Kusto Query Language (KQL) assistant for a Data Scientist at Microsoft.

Your role is to:
1. Help translate natural language requests into KQL queries
2. Explain KQL syntax and functions
3. Optimize queries for performance
4. Help understand query results

## USER'S DATABASE SCHEMA
{DATABASE_SCHEMA}

## KQL REFERENCE
{KQL_KNOWLEDGE}

## GUIDELINES
- When writing queries, ALWAYS include comments explaining each step
- Start with time filters when dealing with timestamped data
- Suggest query optimizations when relevant
- If the user's request is ambiguous, ask clarifying questions
- Provide example output format when helpful
- If you don't know a specific table/column, ask the user to describe their schema

## RESPONSE FORMAT
When providing a query:
1. First, explain what the query will do
2. Provide the KQL query in a code block
3. Explain any important parts
4. Suggest variations or optimizations if relevant
"""


async def main():
    print("=" * 60)
    print("🔍 KUSTO QUERY ASSISTANT")
    print("=" * 60)
    print("\nI'm your KQL expert! I can help you:")
    print("  • Write Kusto queries from natural language")
    print("  • Explain KQL syntax and functions")
    print("  • Optimize your queries")
    print("  • Understand your database schema")
    print("\nType 'exit' to quit, 'schema' to see the database schema")
    print("=" * 60)
    
    client = CopilotClient({"cli_path": COPILOT_CLI_PATH})
    await client.start()
    
    session = await client.create_session({
        "model": "gpt-4.1",
        "streaming": True,
        "system_message": {
            "mode": "replace",
            "content": KUSTO_AGENT_PROMPT,
        },
    })
    
    # Handle streaming output
    def handle_event(event):
        if event.type == SessionEventType.ASSISTANT_MESSAGE_DELTA:
            sys.stdout.write(event.data.delta_content)
            sys.stdout.flush()
        elif event.type == SessionEventType.SESSION_IDLE:
            print("\n")
    
    session.on(handle_event)
    
    # Interactive loop
    while True:
        try:
            print("-" * 60)
            user_input = input("📝 Your question: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == 'exit':
                print("\n👋 Goodbye! Happy querying!")
                break
            
            if user_input.lower() == 'schema':
                print("\n📊 Current Database Schema:")
                print(DATABASE_SCHEMA)
                continue
            
            print("\n🤖 Assistant:\n")
            await session.send_and_wait({"prompt": user_input})
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!")
            break
        except EOFError:
            break
    
    await session.destroy()
    await client.stop()


if __name__ == "__main__":
    asyncio.run(main())
