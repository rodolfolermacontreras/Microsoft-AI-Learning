"""
Kusto Tools for Copilot SDK Agent

These tools allow the AI agent to:
- Explore database schema (tables, columns)
- Execute read-only queries
- Get sample data
- Explain results

All tools enforce read-only access.
"""

from pydantic import BaseModel, Field
from copilot.tools import define_tool
from typing import Optional
import pandas as pd

# This will be set when the app initializes
_kusto_connection = None


def set_kusto_connection(conn):
    """Set the global Kusto connection for tools to use."""
    global _kusto_connection
    _kusto_connection = conn


def get_kusto_connection():
    """Get the current Kusto connection."""
    global _kusto_connection
    return _kusto_connection


# =============================================================================
# TOOL DEFINITIONS
# =============================================================================

class ListTablesParams(BaseModel):
    """No parameters needed"""
    pass


@define_tool(description="List all tables in the Kusto database. Use this first to understand what data is available.")
async def list_tables(params: ListTablesParams) -> dict:
    """List all tables in the database."""
    conn = get_kusto_connection()
    if not conn:
        return {"error": "Not connected to Kusto", "success": False}
    
    df, status = conn.get_tables()
    
    if df is not None:
        tables = df.to_dict('records')
        return {
            "success": True,
            "status": status,
            "tables": tables,
            "count": len(tables)
        }
    else:
        return {"success": False, "error": status}


class GetTableSchemaParams(BaseModel):
    table_name: str = Field(description="Name of the table to get schema for")


@define_tool(description="Get the schema (columns and types) for a specific table. Use this to understand what data a table contains before writing queries.")
async def get_table_schema(params: GetTableSchemaParams) -> dict:
    """Get schema for a specific table."""
    conn = get_kusto_connection()
    if not conn:
        return {"error": "Not connected to Kusto", "success": False}
    
    df, status = conn.get_table_columns(params.table_name)
    
    if df is not None:
        columns = df.to_dict('records')
        return {
            "success": True,
            "status": status,
            "table_name": params.table_name,
            "columns": columns,
            "column_count": len(columns)
        }
    else:
        return {"success": False, "error": status}


class GetSampleDataParams(BaseModel):
    table_name: str = Field(description="Name of the table to sample")
    rows: int = Field(default=5, description="Number of rows to return (max 100)")


@define_tool(description="Get sample rows from a table to understand the data format and values. Limited to 100 rows for safety.")
async def get_sample_data(params: GetSampleDataParams) -> dict:
    """Get sample data from a table."""
    conn = get_kusto_connection()
    if not conn:
        return {"error": "Not connected to Kusto", "success": False}
    
    rows = min(params.rows, 100)
    df, status = conn.get_sample_data(params.table_name, rows)
    
    if df is not None:
        # Convert to records, handling datetime serialization
        sample = df.head(rows).to_dict('records')
        return {
            "success": True,
            "status": status,
            "table_name": params.table_name,
            "sample_data": sample,
            "columns": list(df.columns),
            "row_count": len(sample)
        }
    else:
        return {"success": False, "error": status}


class GetRowCountParams(BaseModel):
    table_name: str = Field(description="Name of the table to count")


@define_tool(description="Get the approximate row count for a table. Useful for understanding data volume.")
async def get_row_count(params: GetRowCountParams) -> dict:
    """Get row count for a table."""
    conn = get_kusto_connection()
    if not conn:
        return {"error": "Not connected to Kusto", "success": False}
    
    count, status = conn.get_row_count(params.table_name)
    
    if count is not None:
        return {
            "success": True,
            "status": status,
            "table_name": params.table_name,
            "row_count": count
        }
    else:
        return {"success": False, "error": status}


class ExecuteQueryParams(BaseModel):
    query: str = Field(description="The KQL query to execute. Must be read-only (no DROP, DELETE, CREATE, etc.)")
    max_rows: int = Field(default=1000, description="Maximum rows to return (default 1000, max 10000)")


@define_tool(description="Execute a read-only KQL query and return results. ONLY read operations are allowed - any modification commands will be blocked. Always explain what the query does before executing.")
async def execute_query(params: ExecuteQueryParams) -> dict:
    """Execute a KQL query (read-only)."""
    conn = get_kusto_connection()
    if not conn:
        return {"error": "Not connected to Kusto", "success": False}
    
    # Safety check first
    is_safe, reason = conn.is_safe_query(params.query)
    if not is_safe:
        return {
            "success": False,
            "error": reason,
            "blocked": True,
            "query": params.query
        }
    
    max_rows = min(params.max_rows, 10000)
    df, status = conn.execute_query(params.query, max_rows=max_rows)
    
    if df is not None:
        # For large results, summarize
        if len(df) > 50:
            preview = df.head(20).to_dict('records')
            return {
                "success": True,
                "status": status,
                "total_rows": len(df),
                "columns": list(df.columns),
                "preview_rows": 20,
                "data_preview": preview,
                "note": f"Showing first 20 of {len(df)} rows. Full data available."
            }
        else:
            return {
                "success": True,
                "status": status,
                "total_rows": len(df),
                "columns": list(df.columns),
                "data": df.to_dict('records')
            }
    else:
        return {"success": False, "error": status}


class ValidateQueryParams(BaseModel):
    query: str = Field(description="The KQL query to validate")


@define_tool(description="Validate a KQL query without executing it. Checks if the query is safe (read-only) and has valid syntax.")
async def validate_query(params: ValidateQueryParams) -> dict:
    """Validate a query without executing."""
    conn = get_kusto_connection()
    if not conn:
        return {"error": "Not connected to Kusto", "success": False}
    
    is_safe, reason = conn.is_safe_query(params.query)
    
    return {
        "query": params.query,
        "is_safe": is_safe,
        "validation_message": reason,
        "ready_to_execute": is_safe
    }


# =============================================================================
# EXPORT ALL TOOLS
# =============================================================================
ALL_KUSTO_TOOLS = [
    list_tables,
    get_table_schema,
    get_sample_data,
    get_row_count,
    execute_query,
    validate_query,
]
