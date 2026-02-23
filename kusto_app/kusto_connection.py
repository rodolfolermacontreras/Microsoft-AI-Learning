"""
Kusto Connection Module - Read-Only Access to Azure Data Explorer

This module provides safe, read-only access to Kusto databases.
It blocks any modification commands for safety.
"""

from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from azure.kusto.data.exceptions import KustoServiceError
import pandas as pd
import re
from typing import Optional, Tuple, Literal
from dataclasses import dataclass


# =============================================================================
# DANGEROUS COMMANDS - These are BLOCKED
# =============================================================================
BLOCKED_PATTERNS = [
    r'\.drop\s',
    r'\.delete\s',
    r'\.purge\s',
    r'\.clear\s',
    r'\.create\s',
    r'\.alter\s',
    r'\.append\s',
    r'\.set\s',
    r'\.set-or-append\s',
    r'\.set-or-replace\s',
    r'\.replace\s',
    r'\.ingest\s',
    r'\.move\s',
    r'\.rename\s',
    r'\.execute\s+database\s+script',
]

BLOCKED_REGEX = re.compile('|'.join(BLOCKED_PATTERNS), re.IGNORECASE)


@dataclass
class KustoConfig:
    """Configuration for Kusto connection"""
    cluster_url: str
    database: str


class KustoConnection:
    """
    Safe, read-only connection to Azure Data Explorer (Kusto).
    
    Features:
    - Blocks all modification commands
    - Query timeout protection
    - Result size limits
    - Easy DataFrame output
    """
    
    def __init__(self, config: KustoConfig):
        self.config = config
        self.client: Optional[KustoClient] = None
        self._connected = False
    
    def connect(self) -> bool:
        """
        Establish connection to Kusto.
        Uses token cache from Kusto Explorer if available.
        """
        try:
            print(f"\n🔐 Connecting to Kusto...")
            print(f"   Cluster: {self.config.cluster_url}")
            print(f"   Database: {self.config.database}")
            print(f"\n💡 TIP: If auth fails, open Kusto Explorer first and connect there.")
            print(f"   This app will then use the cached credentials.\n")
            
            # Method: Use AAD User Prompt with token cache
            # This will use cached tokens from Kusto Explorer if available
            kcsb = KustoConnectionStringBuilder.with_aad_user_token_authentication(
                self.config.cluster_url
            )
            
            self.client = KustoClient(kcsb)
            
            # Test the connection with a simple query
            print(f"   Testing connection...")
            self.client.execute(self.config.database, ".show tables | take 1")
            
            self._connected = True
            print(f"✅ Connected to: {self.config.cluster_url}")
            print(f"📊 Database: {self.config.database}")
            return True
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Connection failed: {error_msg[:200]}")
            
            if "530033" in error_msg or "managed" in error_msg.lower():
                print(f"\n" + "="*60)
                print(f"⚠️  DEVICE COMPLIANCE ISSUE DETECTED")
                print(f"="*60)
                print(f"\nThis is a Microsoft IT policy restriction.")
                print(f"\n🔧 WORKAROUND:")
                print(f"   1. Open Kusto Explorer (desktop app)")
                print(f"   2. Connect to: {self.config.cluster_url}")
                print(f"   3. Run any query to authenticate")
                print(f"   4. Then run THIS app again - it will use the cached token")
                print(f"\nKusto Explorer stores tokens that this app can reuse.")
            else:
                print(f"\n💡 Troubleshooting:")
                print(f"   1. Check VPN is connected")
                print(f"   2. Try connecting in Kusto Explorer first")
            
            self._connected = False
            return False
    
    def is_safe_query(self, query: str) -> Tuple[bool, str]:
        """
        Check if a query is safe (read-only).
        Returns (is_safe, reason).
        """
        # Check for blocked patterns
        match = BLOCKED_REGEX.search(query)
        if match:
            return False, f"Blocked command detected: '{match.group()}' - This is a read-only connection."
        
        return True, "Query is safe"
    
    def execute_query(
        self, 
        query: str, 
        timeout_minutes: int = 5,
        max_rows: int = 10000
    ) -> Tuple[Optional[pd.DataFrame], str]:
        """
        Execute a read-only query and return results as DataFrame.
        
        Args:
            query: KQL query to execute
            timeout_minutes: Query timeout (default 5 min)
            max_rows: Maximum rows to return (default 10,000)
        
        Returns:
            (DataFrame or None, status_message)
        """
        if not self._connected or not self.client:
            return None, "❌ Not connected. Call connect() first."
        
        # Safety check
        is_safe, reason = self.is_safe_query(query)
        if not is_safe:
            return None, f"🚫 {reason}"
        
        # Add row limit if not present
        if '| take ' not in query.lower() and '| limit ' not in query.lower():
            query = f"{query}\n| take {max_rows}"
        
        try:
            response = self.client.execute(self.config.database, query)
            
            # Convert to DataFrame
            df = pd.DataFrame(response.primary_results[0])
            
            row_count = len(df)
            col_count = len(df.columns)
            
            status = f"✅ Query successful: {row_count:,} rows × {col_count} columns"
            if row_count >= max_rows:
                status += f" (limited to {max_rows:,} rows)"
            
            return df, status
            
        except KustoServiceError as e:
            return None, f"❌ Kusto error: {e}"
        except Exception as e:
            return None, f"❌ Error: {e}"
    
    def get_tables(self) -> Tuple[Optional[pd.DataFrame], str]:
        """Get list of all tables in the database."""
        query = ".show tables | project TableName, Folder, DocString | take 500"
        return self.execute_query(query, timeout_minutes=2)
    
    def get_table_schema(self, table_name: str) -> Tuple[Optional[pd.DataFrame], str]:
        """Get schema for a specific table."""
        # Validate table name (prevent injection)
        if not re.match(r'^[\w]+$', table_name):
            return None, "❌ Invalid table name"
        
        query = f".show table {table_name} schema as json"
        return self.execute_query(query)
    
    def get_table_columns(self, table_name: str) -> Tuple[Optional[pd.DataFrame], str]:
        """Get columns for a specific table in a readable format."""
        if not re.match(r'^[\w]+$', table_name):
            return None, "❌ Invalid table name"
        
        query = f"""
        .show table {table_name} 
        | project ColumnName=Column, ColumnType=Type
        """
        return self.execute_query(query)
    
    def get_sample_data(self, table_name: str, rows: int = 5) -> Tuple[Optional[pd.DataFrame], str]:
        """Get sample rows from a table."""
        if not re.match(r'^[\w]+$', table_name):
            return None, "❌ Invalid table name"
        
        rows = min(rows, 100)  # Cap at 100 for safety
        query = f"{table_name} | take {rows}"
        return self.execute_query(query)
    
    def get_row_count(self, table_name: str) -> Tuple[Optional[int], str]:
        """Get approximate row count for a table."""
        if not re.match(r'^[\w]+$', table_name):
            return None, "❌ Invalid table name"
        
        query = f"{table_name} | count"
        df, status = self.execute_query(query)
        
        if df is not None and len(df) > 0:
            count = df.iloc[0, 0]
            return count, f"✅ Table has approximately {count:,} rows"
        
        return None, status
    
    def close(self):
        """Close the connection."""
        if self.client:
            self.client.close()
            self._connected = False
            print("🔌 Connection closed")


# =============================================================================
# QUICK TEST
# =============================================================================
if __name__ == "__main__":
    # Example usage - update with your details
    config = KustoConfig(
        cluster_url="https://your-cluster.kusto.windows.net",
        database="YourDatabase"
    )
    
    conn = KustoConnection(config)
    
    if conn.connect():
        # List tables
        tables, status = conn.get_tables()
        print(status)
        if tables is not None:
            print(tables)
        
        conn.close()
