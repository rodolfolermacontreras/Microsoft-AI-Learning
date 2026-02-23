"""
═══════════════════════════════════════════════════════════════════════════════
 WORKPLACE DOCUMENTATION TOOL - UNIFIED VERSION
═══════════════════════════════════════════════════════════════════════════════
 
 A complete solution for documenting workplace interactions:
 • Beautiful web interface (one-click start)
 • AI-powered pattern detection (auto-categorizes incidents)
 • Cross-incident analysis (finds patterns across ALL your data)
 • Team data import (combine exports from coworkers)
 • HR narrative generation (professional documentation)
 • Knowledge graph (visualize relationships)
 • 100% local storage (your data never leaves your machine)
 
 Built with GitHub Copilot SDK for intelligent analysis.
═══════════════════════════════════════════════════════════════════════════════
"""

import json
import os
import http.server
import socketserver
import webbrowser
import asyncio
import threading
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs
from typing import Optional
import traceback

# Copilot SDK imports
from copilot import CopilotClient
from copilot.generated.session_events import SessionEventType

# =============================================================================
# CONFIGURATION
# =============================================================================

def find_copilot_cli():
    """Find the Copilot CLI executable."""
    paths = [
        Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Packages",
    ]
    for base in paths:
        if base.exists():
            for p in base.glob("GitHub.Copilot*/copilot.exe"):
                return str(p)
    return "copilot"

COPILOT_CLI_PATH = find_copilot_cli()
PORT = 8765

# Data storage - local to each user's machine
DATA_DIR = Path.home() / ".workplace_docs"
DATA_FILE = DATA_DIR / "incidents.json"
GRAPH_FILE = DATA_DIR / "knowledge_graph.json"

def ensure_data_dir():
    DATA_DIR.mkdir(exist_ok=True)
    if not DATA_FILE.exists():
        DATA_FILE.write_text("[]")
    if not GRAPH_FILE.exists():
        GRAPH_FILE.write_text('{"nodes": [], "edges": []}')

def load_incidents():
    ensure_data_dir()
    try:
        return json.loads(DATA_FILE.read_text())
    except:
        return []

def save_incidents(incidents):
    ensure_data_dir()
    DATA_FILE.write_text(json.dumps(incidents, indent=2, default=str))

def load_graph():
    ensure_data_dir()
    try:
        graph = json.loads(GRAPH_FILE.read_text())
        # Ensure proper structure
        if not isinstance(graph.get('nodes'), list):
            graph['nodes'] = []
        if not isinstance(graph.get('edges'), list):
            graph['edges'] = []
        return graph
    except:
        return {"nodes": [], "edges": []}

def save_graph(graph):
    ensure_data_dir()
    GRAPH_FILE.write_text(json.dumps(graph, indent=2, default=str))

# =============================================================================
# AI ANALYZER (Copilot SDK)
# =============================================================================

class AIAnalyzer:
    """Singleton AI analyzer using Copilot SDK with dedicated event loop."""
    _instance = None
    _lock = threading.Lock()
    
    def __init__(self):
        self.client = None
        self.session = None
        self.ready = False
        self._loop = None
        self._thread = None
        self._start_loop_thread()
    
    def _start_loop_thread(self):
        """Start a dedicated thread with its own event loop for AI operations."""
        def run_loop():
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            self._loop.run_forever()
        
        self._thread = threading.Thread(target=run_loop, daemon=True)
        self._thread.start()
        # Wait for loop to be ready
        import time
        while self._loop is None:
            time.sleep(0.01)
    
    def _run_async(self, coro, timeout=90):
        """Run an async coroutine on the dedicated event loop."""
        if self._loop is None or not self._loop.is_running():
            self._start_loop_thread()
        
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        try:
            return future.result(timeout=timeout)
        except Exception as e:
            print(f"Async operation error: {e}")
            raise
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    def initialize_sync(self):
        """Synchronous initialization wrapper."""
        return self._run_async(self.initialize())
    
    async def initialize(self):
        """Initialize Copilot connection."""
        if self.ready:
            return True
        
        try:
            self.client = CopilotClient({"cli_path": COPILOT_CLI_PATH})
            await self.client.start()
            self.session = await self.client.create_session({"streaming": True})
            
            # Prime with specialized context
            setup_prompt = """You are an expert workplace documentation analyst specializing in identifying 
toxic management patterns. Your role is to:

1. ANALYZE workplace conversations for concerning patterns:
   - gaslighting (denying previous statements, rewriting history)
   - unclear_expectations (vague instructions, moving goalposts)  
   - blame_shifting (making others responsible for systemic issues)
   - pressure_tactics (unreasonable deadlines, threats)
   - micromanagement (excessive control, lack of trust)
   - contradicting_requests (saying one thing, expecting another)
   - lack_of_support (no resources, no backup)
   - shifting_priorities (constant changes without acknowledgment)

2. Be objective and factual - cite specific text
3. Extract key quotes that demonstrate patterns
4. Suggest what additional documentation would help

Respond "Ready" to acknowledge."""

            await self._ask(setup_prompt)
            self.ready = True
            return True
        except Exception as e:
            print(f"AI initialization failed: {e}")
            return False
    
    async def _ask(self, prompt: str, timeout: int = 60) -> str:
        """Send prompt and get response with timeout."""
        if not self.session:
            # Try to reinitialize if session is lost
            if not await self._reinitialize_session():
                return "Session unavailable"
        
        response_text = ""
        
        def handle_event(event):
            nonlocal response_text
            if event.type == SessionEventType.ASSISTANT_MESSAGE:
                if hasattr(event.data, 'content'):
                    response_text = event.data.content
            elif event.type == SessionEventType.ASSISTANT_MESSAGE_DELTA:
                if hasattr(event.data, 'delta_content'):
                    response_text += event.data.delta_content
        
        unsubscribe = self.session.on(handle_event)
        try:
            await asyncio.wait_for(
                self.session.send_and_wait({"prompt": prompt}, timeout=timeout),
                timeout=timeout + 5
            )
        except asyncio.TimeoutError:
            print(f"AI request timed out after {timeout}s")
            return response_text if response_text else "Analysis timed out"
        except Exception as e:
            print(f"AI request error: {e}")
            # Mark as needing reinitialization
            self.ready = False
            return f"Error: {str(e)}"
        finally:
            unsubscribe()
        
        return response_text
    
    async def _reinitialize_session(self) -> bool:
        """Reinitialize the session if needed."""
        self.ready = False
        self.session = None
        return await self.initialize()
    
    async def analyze_incident(self, content: str, user_notes: str = "") -> dict:
        """Analyze a single incident."""
        if not self.ready:
            await self.initialize()
        
        if not self.ready:
            return {"error": "AI not available", "detected_patterns": [], "severity": "unknown"}
        
        notes_context = f"\n\nUser's notes/context: {user_notes}" if user_notes else ""
        
        prompt = f"""Analyze this workplace interaction and return ONLY valid JSON:
{{
    "detected_patterns": ["pattern1", "pattern2"],
    "severity": "low/medium/high",
    "key_quotes": ["quote1", "quote2"],
    "people_involved": ["person1", "person2"],
    "factual_summary": "2-3 sentence objective summary",
    "red_flags": ["flag1", "flag2"],
    "documentation_tips": "what else to document"
}}

INTERACTION:
{content[:3000]}{notes_context}

Return ONLY the JSON object, no other text."""

        response = await self._ask(prompt)
        
        try:
            # Clean up response
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            if response.endswith("```"):
                response = response[:-3]
            return json.loads(response.strip())
        except:
            return {
                "detected_patterns": ["analysis_error"],
                "severity": "unknown",
                "key_quotes": [],
                "people_involved": [],
                "factual_summary": response[:500] if response else "Analysis failed",
                "red_flags": [],
                "documentation_tips": "Manual review recommended"
            }
    
    async def analyze_all_patterns(self, incidents: list) -> dict:
        """Analyze patterns across ALL incidents."""
        if not incidents:
            return {"error": "No incidents to analyze"}
        
        if not self.ready:
            await self.initialize()
        
        # Build summary of all incidents
        summaries = []
        for i, inc in enumerate(incidents[:20], 1):  # Limit to 20 for context
            s = f"#{i} [{inc.get('date', 'unknown')}] People: {', '.join(inc.get('people', []))}\n"
            s += f"Patterns: {', '.join(inc.get('categories', inc.get('ai_analysis', {}).get('detected_patterns', [])))}\n"
            s += f"Content: {inc.get('content', '')[:200]}...\n"
            summaries.append(s)
        
        prompt = f"""You have {len(incidents)} documented workplace incidents. Analyze patterns ACROSS ALL and return ONLY valid JSON:
{{
    "total_incidents": {len(incidents)},
    "date_range": "earliest to latest",
    "recurring_patterns": [
        {{"pattern": "name", "frequency": N, "trend": "increasing/stable/decreasing"}}
    ],
    "escalation_assessment": "getting worse / stable / improving - with explanation",
    "key_people": [
        {{"person": "name", "incident_count": N, "typical_behaviors": ["behavior1"]}}
    ],
    "strongest_evidence": ["top 3 most documented concerning behaviors with dates"],
    "documentation_gaps": ["what's missing"],
    "hr_readiness_score": N,
    "hr_readiness_explanation": "why this score",
    "recommended_actions": ["action1", "action2"]
}}

INCIDENTS:
{chr(10).join(summaries)}

Return ONLY the JSON object."""

        response = await self._ask(prompt)
        
        try:
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            return json.loads(response.strip())
        except:
            return {"raw_analysis": response}
    
    async def generate_hr_narrative(self, incidents: list, focus_person: str = None) -> str:
        """Generate HR-ready narrative."""
        if not self.ready:
            await self.initialize()
        
        filtered = incidents
        if focus_person:
            filtered = [i for i in incidents if focus_person.lower() in str(i.get('people', [])).lower()]
        
        details = []
        for inc in filtered[:15]:
            d = f"[{inc.get('date', 'unknown')}]\n"
            d += f"People: {', '.join(inc.get('people', []))}\n"
            d += f"Content: {inc.get('content', '')[:400]}\n"
            if inc.get('user_notes'):
                d += f"Context: {inc.get('user_notes')}\n"
            details.append(d)
        
        prompt = f"""Based on these documented workplace incidents, write a professional HR narrative.

GUIDELINES:
- Professional, objective language
- Focus on documented behaviors and impact
- Include specific dates and quotes
- Structure: Executive Summary → Timeline → Pattern Analysis → Impact → Requested Action
{f"- Focus on interactions involving: {focus_person}" if focus_person else ""}

INCIDENTS:
{chr(10).join(details)}

Write the narrative:"""

        return await self._ask(prompt)
    
    async def suggest_questions(self, incidents: list) -> list:
        """Suggest protective questions for future meetings."""
        if not self.ready:
            await self.initialize()
        
        patterns = []
        for inc in incidents:
            patterns.extend(inc.get('categories', []))
            if inc.get('ai_analysis'):
                patterns.extend(inc['ai_analysis'].get('detected_patterns', []))
        
        from collections import Counter
        top = Counter(patterns).most_common(5)
        
        prompt = f"""Based on documented patterns of {', '.join([p[0] for p in top])}, 
suggest 5 professional questions to ask in future meetings that will:
1. Get clarity on expectations
2. Create documentation of the response
3. Be non-confrontational

Return as JSON array of strings only."""

        response = await self._ask(prompt)
        try:
            return json.loads(response.strip())
        except:
            return [response]
    
    async def close(self):
        if self.session:
            try:
                await self.session.destroy()
            except:
                pass
        if self.client:
            try:
                await self.client.stop()
            except:
                pass

# =============================================================================
# KNOWLEDGE GRAPH
# =============================================================================

def update_knowledge_graph(incident: dict):
    """Update the knowledge graph with a new incident."""
    graph = load_graph()
    
    # Ensure proper structure
    if not isinstance(graph.get('nodes'), list):
        graph['nodes'] = []
    if not isinstance(graph.get('edges'), list):
        graph['edges'] = []
    
    inc_id = incident.get('id', len(graph['nodes']) + 1)
    date = incident.get('date', 'unknown')
    people = incident.get('people', [])
    patterns = incident.get('categories', [])
    if incident.get('ai_analysis'):
        patterns = incident['ai_analysis'].get('detected_patterns', patterns)
    
    # Add incident node
    graph['nodes'].append({
        "id": f"inc_{inc_id}",
        "type": "incident",
        "label": f"Incident {inc_id}",
        "date": date
    })
    
    # Add/update person nodes and edges
    for person in people:
        if not person:
            continue
        person_id = f"person_{person.lower().replace(' ', '_')}"
        if not any(n.get('id') == person_id for n in graph['nodes'] if isinstance(n, dict)):
            graph['nodes'].append({
                "id": person_id,
                "type": "person",
                "label": person
            })
        graph['edges'].append({
            "source": person_id,
            "target": f"inc_{inc_id}",
            "relation": "involved_in"
        })
    
    # Add/update pattern nodes and edges
    for pattern in patterns:
        if not pattern:
            continue
        pattern_id = f"pattern_{pattern}"
        if not any(n.get('id') == pattern_id for n in graph['nodes'] if isinstance(n, dict)):
            graph['nodes'].append({
                "id": pattern_id,
                "type": "pattern",
                "label": pattern.replace('_', ' ').title()
            })
        graph['edges'].append({
            "source": f"inc_{inc_id}",
            "target": pattern_id,
            "relation": "exhibits"
        })
    
    save_graph(graph)
    return graph

def rebuild_graph_from_incidents():
    """Rebuild the entire knowledge graph from saved incidents."""
    # Reset graph
    graph = {"nodes": [], "edges": []}
    save_graph(graph)
    
    # Rebuild from all incidents
    incidents = load_incidents()
    for incident in incidents:
        update_knowledge_graph(incident)
    
    print(f"📊 Rebuilt knowledge graph from {len(incidents)} incidents")
    return load_graph()

# =============================================================================
# HTML TEMPLATE - BEAUTIFUL UI
# =============================================================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📝 Workplace Documentation Tool</title>
    <style>
        :root {
            --bg-primary: #0f0f1a;
            --bg-secondary: #1a1a2e;
            --bg-card: #252540;
            --accent: #667eea;
            --accent-hover: #764ba2;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --text-primary: #e0e0e0;
            --text-secondary: #888;
            --border: #3a3a5a;
        }
        
        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        body {
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
        }
        
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        
        header {
            text-align: center;
            padding: 30px 0;
            border-bottom: 1px solid var(--border);
            margin-bottom: 30px;
        }
        
        header h1 { font-size: 2.2em; margin-bottom: 10px; }
        header p { color: var(--text-secondary); }
        
        .ai-status {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            background: var(--bg-secondary);
            border-radius: 20px;
            font-size: 0.85em;
            margin-top: 15px;
        }
        .ai-status.ready { border: 1px solid var(--success); color: var(--success); }
        .ai-status.loading { border: 1px solid var(--warning); color: var(--warning); }
        .ai-status.error { border: 1px solid var(--danger); color: var(--danger); }
        
        .warning-banner {
            background: linear-gradient(135deg, #2d2d44 0%, #1a1a2e 100%);
            border-left: 4px solid var(--warning);
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 25px;
        }
        .warning-banner h3 { color: var(--warning); margin-bottom: 5px; font-size: 0.95em; }
        .warning-banner p { font-size: 0.85em; color: var(--text-secondary); }
        
        /* Navigation */
        .nav-tabs {
            display: flex;
            gap: 5px;
            background: var(--bg-secondary);
            padding: 8px;
            border-radius: 12px;
            margin-bottom: 25px;
            flex-wrap: wrap;
        }
        
        .nav-tab {
            padding: 12px 20px;
            background: transparent;
            border: none;
            color: var(--text-secondary);
            cursor: pointer;
            border-radius: 8px;
            font-size: 0.9em;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .nav-tab:hover { background: var(--bg-card); color: var(--text-primary); }
        .nav-tab.active { background: var(--accent); color: white; }
        
        /* Panels */
        .panel { display: none; }
        .panel.active { display: block; }
        
        .card {
            background: var(--bg-card);
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 20px;
        }
        
        .card h3 { margin-bottom: 20px; display: flex; align-items: center; gap: 10px; }
        
        /* Form elements */
        label {
            display: block;
            margin-bottom: 8px;
            color: var(--text-secondary);
            font-size: 0.9em;
        }
        
        textarea, input[type="text"], input[type="date"], select {
            width: 100%;
            padding: 12px 15px;
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text-primary);
            font-family: inherit;
            font-size: 0.95em;
            margin-bottom: 15px;
            transition: border-color 0.2s;
        }
        
        textarea { min-height: 180px; resize: vertical; }
        textarea:focus, input:focus, select:focus {
            outline: none;
            border-color: var(--accent);
        }
        
        /* Categories */
        .categories {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 20px;
        }
        
        .cat-btn {
            padding: 8px 14px;
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 20px;
            color: var(--text-secondary);
            cursor: pointer;
            font-size: 0.8em;
            transition: all 0.2s;
        }
        .cat-btn:hover { border-color: var(--accent); color: var(--text-primary); }
        .cat-btn.selected { background: var(--accent); color: white; border-color: var(--accent); }
        .cat-btn.ai-detected { 
            background: rgba(16, 185, 129, 0.2); 
            border-color: var(--success); 
            color: var(--success);
        }
        
        /* Buttons */
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.95em;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, var(--accent) 0%, var(--accent-hover) 100%);
            color: white;
        }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 5px 20px rgba(102, 126, 234, 0.3); }
        
        .btn-secondary { background: var(--bg-secondary); color: var(--text-primary); border: 1px solid var(--border); }
        .btn-secondary:hover { border-color: var(--accent); }
        
        .btn-success { background: var(--success); color: white; }
        .btn-danger { background: var(--danger); color: white; }
        
        .btn-group { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 20px; }
        
        /* Incident cards */
        .incident-card {
            background: var(--bg-secondary);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 15px;
            border-left: 4px solid var(--accent);
            transition: transform 0.2s;
        }
        .incident-card:hover { transform: translateX(5px); }
        
        .incident-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 12px;
        }
        
        .incident-id { font-weight: bold; color: var(--accent); }
        .incident-date { color: var(--text-secondary); font-size: 0.85em; }
        .incident-severity {
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.75em;
            text-transform: uppercase;
        }
        .severity-high { background: rgba(239, 68, 68, 0.2); color: var(--danger); }
        .severity-medium { background: rgba(245, 158, 11, 0.2); color: var(--warning); }
        .severity-low { background: rgba(16, 185, 129, 0.2); color: var(--success); }
        
        .incident-content {
            color: var(--text-secondary);
            font-size: 0.9em;
            line-height: 1.6;
            max-height: 150px;
            overflow-y: auto;
            white-space: pre-wrap;
            margin-bottom: 12px;
        }
        
        .incident-tags { display: flex; flex-wrap: wrap; gap: 6px; }
        .tag {
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.75em;
        }
        .tag-person { background: rgba(102, 126, 234, 0.2); color: var(--accent); }
        .tag-pattern { background: rgba(118, 75, 162, 0.2); color: #bb6bd9; }
        
        .incident-notes {
            margin-top: 12px;
            padding: 10px;
            background: var(--bg-card);
            border-radius: 6px;
            font-size: 0.85em;
            color: var(--text-secondary);
            border-left: 2px solid var(--warning);
        }
        
        /* AI Analysis Box */
        .ai-analysis {
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
        }
        .ai-analysis h4 { color: var(--success); margin-bottom: 15px; }
        .ai-analysis .field { margin-bottom: 12px; }
        .ai-analysis .field-label { font-size: 0.8em; color: var(--text-secondary); margin-bottom: 4px; }
        .ai-analysis .field-value { font-size: 0.9em; }
        
        /* Stats grid */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 15px;
            margin-bottom: 25px;
        }
        
        .stat-card {
            background: var(--bg-secondary);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .stat-card .number { font-size: 2.5em; font-weight: bold; color: var(--accent); }
        .stat-card .label { color: var(--text-secondary); font-size: 0.85em; }
        
        /* Progress bar */
        .progress-bar {
            display: flex;
            align-items: center;
            margin-bottom: 12px;
        }
        .progress-bar .label { width: 150px; font-size: 0.85em; }
        .progress-bar .bar {
            flex: 1;
            height: 20px;
            background: var(--bg-secondary);
            border-radius: 10px;
            overflow: hidden;
            margin: 0 15px;
        }
        .progress-bar .fill {
            height: 100%;
            background: linear-gradient(90deg, var(--accent), var(--accent-hover));
            border-radius: 10px;
            transition: width 0.5s;
        }
        .progress-bar .count { width: 40px; text-align: right; font-size: 0.85em; }
        
        /* HR Narrative */
        .narrative-box {
            background: var(--bg-secondary);
            padding: 25px;
            border-radius: 10px;
            white-space: pre-wrap;
            line-height: 1.8;
            font-size: 0.95em;
            max-height: 500px;
            overflow-y: auto;
        }
        
        /* Knowledge Graph */
        #graph-container {
            background: var(--bg-secondary);
            border-radius: 10px;
            height: 400px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--text-secondary);
        }
        
        /* Messages */
        .message {
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 15px;
            display: none;
        }
        .message.success { display: block; background: rgba(16, 185, 129, 0.2); border: 1px solid var(--success); color: var(--success); }
        .message.error { display: block; background: rgba(239, 68, 68, 0.2); border: 1px solid var(--danger); color: var(--danger); }
        
        /* Loading spinner */
        .spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 2px solid var(--border);
            border-top-color: var(--accent);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        
        /* Import section */
        .import-zone {
            border: 2px dashed var(--border);
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s;
        }
        .import-zone:hover { border-color: var(--accent); background: rgba(102, 126, 234, 0.05); }
        .import-zone input { display: none; }
        
        /* Questions list */
        .questions-list { list-style: none; }
        .questions-list li {
            padding: 15px;
            background: var(--bg-secondary);
            border-radius: 8px;
            margin-bottom: 10px;
            display: flex;
            gap: 12px;
        }
        .questions-list .num {
            background: var(--accent);
            color: white;
            width: 28px;
            height: 28px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.85em;
            flex-shrink: 0;
        }
        
        /* Privacy note */
        .privacy-note {
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.2);
            padding: 12px 15px;
            border-radius: 8px;
            font-size: 0.85em;
            color: var(--success);
            margin-top: 20px;
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .nav-tabs { flex-direction: column; }
            .nav-tab { justify-content: center; }
            .btn-group { flex-direction: column; }
            .btn { width: 100%; justify-content: center; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📝 Workplace Documentation Tool</h1>
            <p>Document interactions • AI-powered analysis • Build your case</p>
            <div id="ai-status" class="ai-status loading">
                <span class="spinner"></span>
                <span>Connecting to AI...</span>
            </div>
        </header>
        
        <div class="warning-banner">
            <h3>⚠️ Important Disclaimer</h3>
            <p>This tool is for personal documentation only. Not legal advice. Consult HR or legal counsel for workplace issues. All data stored locally on YOUR computer.</p>
        </div>
        
        <nav class="nav-tabs">
            <button class="nav-tab active" onclick="showTab('add')">➕ Add Incident</button>
            <button class="nav-tab" onclick="showTab('timeline')">📅 Timeline</button>
            <button class="nav-tab" onclick="showTab('patterns')">🔍 AI Analysis</button>
            <button class="nav-tab" onclick="showTab('narrative')">📄 HR Narrative</button>
            <button class="nav-tab" onclick="showTab('graph')">🕸️ Knowledge Graph</button>
            <button class="nav-tab" onclick="showTab('import')">📥 Team Import</button>
            <button class="nav-tab" onclick="showTab('export')">📤 Export</button>
        </nav>
        
        <!-- ADD INCIDENT -->
        <div id="add-panel" class="panel active">
            <div class="card">
                <h3>📝 Document New Incident</h3>
                
                <label>Paste conversation, email, or describe what happened:</label>
                <textarea id="content" placeholder="Paste Teams chat, email thread, or describe the interaction...

Example:
Manager: I need this done by tomorrow
You: That timeline seems challenging given the scope
Manager: Other team members would have it done already
You: Can you clarify the specific requirements?
Manager: You should know this by now"></textarea>
                
                <label>📝 Your Notes (context, observations, how it made you feel):</label>
                <textarea id="user-notes" style="min-height: 80px;" placeholder="Add context that helps explain the situation...

Example: This is the third time this week expectations changed without warning. The 'other team members' comment felt like a comparison designed to make me feel inadequate."></textarea>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                    <div>
                        <label>📅 When did this happen?</label>
                        <input type="date" id="date">
                    </div>
                    <div>
                        <label>👤 People involved (comma-separated):</label>
                        <input type="text" id="people" placeholder="e.g., Manager Name, HR, Coworker">
                    </div>
                </div>
                
                <label>🏷️ Categories (AI will auto-detect, or select manually):</label>
                <div class="categories" id="categories">
                    <button class="cat-btn" data-cat="unclear_expectations">Unclear Expectations</button>
                    <button class="cat-btn" data-cat="shifting_priorities">Shifting Priorities</button>
                    <button class="cat-btn" data-cat="gaslighting">Gaslighting</button>
                    <button class="cat-btn" data-cat="pressure_tactics">Pressure Tactics</button>
                    <button class="cat-btn" data-cat="blame_shifting">Blame Shifting</button>
                    <button class="cat-btn" data-cat="unreasonable_deadlines">Unreasonable Deadlines</button>
                    <button class="cat-btn" data-cat="contradicting_requests">Contradicting Requests</button>
                    <button class="cat-btn" data-cat="micromanagement">Micromanagement</button>
                    <button class="cat-btn" data-cat="lack_of_support">Lack of Support</button>
                    <button class="cat-btn" data-cat="intimidation">Intimidation</button>
                </div>
                
                <div class="btn-group">
                    <button class="btn btn-primary" onclick="saveIncident(true)">
                        🤖 Save & Analyze with AI
                    </button>
                    <button class="btn btn-secondary" onclick="saveIncident(false)">
                        💾 Quick Save (No AI)
                    </button>
                </div>
                
                <div id="save-message" class="message"></div>
                
                <div id="ai-analysis-result" class="ai-analysis" style="display: none;">
                    <h4>🤖 AI Analysis</h4>
                    <div id="ai-result-content"></div>
                </div>
                
                <div class="privacy-note">
                    🔒 <strong>Privacy:</strong> All data stored locally at: <code>%USERPROFILE%\\.workplace_docs</code>
                </div>
            </div>
        </div>
        
        <!-- TIMELINE -->
        <div id="timeline-panel" class="panel">
            <div class="card">
                <h3>📅 Incident Timeline</h3>
                <div id="timeline-stats" class="stats-grid"></div>
                <div id="timeline-content"></div>
            </div>
        </div>
        
        <!-- AI PATTERNS ANALYSIS -->
        <div id="patterns-panel" class="panel">
            <div class="card">
                <h3>🔍 AI Pattern Analysis</h3>
                <p style="color: var(--text-secondary); margin-bottom: 20px;">
                    Analyzes patterns across ALL your documented incidents to identify trends and build your case.
                </p>
                <button class="btn btn-primary" onclick="runPatternAnalysis()">
                    🤖 Run Cross-Incident Analysis
                </button>
                <div id="patterns-result" style="margin-top: 20px;"></div>
            </div>
            
            <div class="card">
                <h3>❓ Suggested Questions</h3>
                <p style="color: var(--text-secondary); margin-bottom: 20px;">
                    AI-generated questions to ask in future meetings that help document and clarify expectations.
                </p>
                <button class="btn btn-secondary" onclick="getQuestions()">
                    💡 Generate Questions
                </button>
                <ul id="questions-list" class="questions-list" style="margin-top: 20px;"></ul>
            </div>
        </div>
        
        <!-- HR NARRATIVE -->
        <div id="narrative-panel" class="panel">
            <div class="card">
                <h3>📄 Generate HR Narrative</h3>
                <p style="color: var(--text-secondary); margin-bottom: 20px;">
                    Creates a professional, factual narrative suitable for HR documentation or legal review.
                </p>
                
                <label>Focus on specific person (optional):</label>
                <input type="text" id="narrative-focus" placeholder="Leave blank for all incidents, or enter a name">
                
                <button class="btn btn-primary" onclick="generateNarrative()" style="margin-top: 10px;">
                    📝 Generate HR Narrative
                </button>
                
                <div id="narrative-result" style="margin-top: 20px;"></div>
                
                <div class="btn-group" id="narrative-actions" style="display: none;">
                    <button class="btn btn-secondary" onclick="copyNarrative()">📋 Copy to Clipboard</button>
                    <button class="btn btn-secondary" onclick="downloadNarrative()">📥 Download as Text</button>
                </div>
            </div>
        </div>
        
        <!-- KNOWLEDGE GRAPH -->
        <div id="graph-panel" class="panel">
            <div class="card">
                <h3>🕸️ Knowledge Graph</h3>
                <p style="color: var(--text-secondary); margin-bottom: 20px;">
                    Visual representation of people, incidents, and patterns.
                </p>
                <div id="graph-container">
                    <div id="graph-placeholder">Loading graph data...</div>
                </div>
                <div id="graph-stats" style="margin-top: 20px;"></div>
            </div>
        </div>
        
        <!-- TEAM IMPORT -->
        <div id="import-panel" class="panel">
            <div class="card">
                <h3>📥 Import Team Data</h3>
                <p style="color: var(--text-secondary); margin-bottom: 20px;">
                    Import exported JSON files from coworkers to analyze patterns across the team.
                </p>
                
                <div class="import-zone" onclick="document.getElementById('import-file').click()">
                    <input type="file" id="import-file" accept=".json" onchange="importData(event)">
                    <p>📁 Click to select JSON file or drag & drop</p>
                    <p style="font-size: 0.85em; color: var(--text-secondary); margin-top: 10px;">
                        Supports exports from this tool
                    </p>
                </div>
                
                <div id="import-message" class="message" style="margin-top: 20px;"></div>
                
                <div class="privacy-note">
                    🔒 Imported data is merged with your local data and stays on YOUR computer.
                </div>
            </div>
        </div>
        
        <!-- EXPORT -->
        <div id="export-panel" class="panel">
            <div class="card">
                <h3>📤 Export Your Data</h3>
                <p style="color: var(--text-secondary); margin-bottom: 20px;">
                    Download your documented incidents for backup, sharing with coworkers, or HR/legal review.
                </p>
                
                <div class="btn-group">
                    <button class="btn btn-primary" onclick="exportJSON()">
                        📥 Download JSON (For sharing)
                    </button>
                    <button class="btn btn-secondary" onclick="exportText()">
                        📄 Download Text (For reading)
                    </button>
                    <button class="btn btn-secondary" onclick="copyAllData()">
                        📋 Copy to Clipboard
                    </button>
                </div>
                
                <div class="privacy-note" style="margin-top: 30px;">
                    <strong>📁 Data Location:</strong><br>
                    <code id="data-path">%USERPROFILE%\\.workplace_docs\\incidents.json</code><br><br>
                    <strong>💡 To share with coworkers:</strong><br>
                    1. Export your JSON<br>
                    2. Send to them via Teams/email<br>
                    3. They import it using the "Team Import" tab<br>
                    4. Run cross-incident analysis to find team-wide patterns
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Initialize
        document.getElementById('date').value = new Date().toISOString().split('T')[0];
        let aiReady = false;
        let currentNarrative = '';
        
        // Check AI status
        async function checkAI() {
            try {
                const response = await fetch('/api/ai-status');
                const data = await response.json();
                const status = document.getElementById('ai-status');
                if (data.ready) {
                    status.className = 'ai-status ready';
                    status.innerHTML = '✅ AI Ready';
                    aiReady = true;
                } else {
                    status.className = 'ai-status loading';
                    status.innerHTML = '<span class="spinner"></span> Initializing AI...';
                    setTimeout(checkAI, 2000);
                }
            } catch (e) {
                document.getElementById('ai-status').className = 'ai-status error';
                document.getElementById('ai-status').innerHTML = '⚠️ AI Unavailable (offline mode)';
            }
        }
        checkAI();
        
        // Tab navigation
        function showTab(name) {
            document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
            document.querySelector(`[onclick="showTab('${name}')"]`).classList.add('active');
            document.getElementById(name + '-panel').classList.add('active');
            
            if (name === 'timeline') loadTimeline();
            if (name === 'graph') loadGraph();
        }
        
        // Category buttons
        document.querySelectorAll('.cat-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                btn.classList.toggle('selected');
                btn.classList.remove('ai-detected');
            });
        });
        
        // Save incident
        async function saveIncident(useAI) {
            const content = document.getElementById('content').value.trim();
            const userNotes = document.getElementById('user-notes').value.trim();
            const date = document.getElementById('date').value;
            const people = document.getElementById('people').value.split(',').map(p => p.trim()).filter(p => p);
            const categories = Array.from(document.querySelectorAll('.cat-btn.selected')).map(b => b.dataset.cat);
            
            if (!content) {
                showMessage('save-message', 'Please enter the incident content.', 'error');
                return;
            }
            
            const saveBtn = event.target;
            const originalText = saveBtn.innerHTML;
            saveBtn.innerHTML = '<span class="spinner"></span> Analyzing...';
            saveBtn.disabled = true;
            
            try {
                const response = await fetch('/api/save', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ content, userNotes, date, people, categories, useAI })
                });
                const result = await response.json();
                
                showMessage('save-message', '✅ Incident saved successfully!', 'success');
                
                // Show AI analysis if available
                if (result.ai_analysis && !result.ai_analysis.error) {
                    displayAIAnalysis(result.ai_analysis);
                    
                    // Highlight AI-detected categories
                    const detected = result.ai_analysis.detected_patterns || [];
                    document.querySelectorAll('.cat-btn').forEach(btn => {
                        btn.classList.remove('ai-detected');
                        if (detected.includes(btn.dataset.cat)) {
                            btn.classList.add('ai-detected');
                        }
                    });
                }
                
                // Clear form
                document.getElementById('content').value = '';
                document.getElementById('user-notes').value = '';
                document.getElementById('people').value = '';
                document.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('selected'));
                
            } catch (err) {
                showMessage('save-message', 'Error saving: ' + err.message, 'error');
            } finally {
                saveBtn.innerHTML = originalText;
                saveBtn.disabled = false;
            }
        }
        
        function displayAIAnalysis(analysis) {
            const container = document.getElementById('ai-result-content');
            container.innerHTML = `
                <div class="field">
                    <div class="field-label">Detected Patterns</div>
                    <div class="field-value">${(analysis.detected_patterns || []).join(', ') || 'None detected'}</div>
                </div>
                <div class="field">
                    <div class="field-label">Severity</div>
                    <div class="field-value"><span class="incident-severity severity-${analysis.severity || 'unknown'}">${analysis.severity || 'Unknown'}</span></div>
                </div>
                <div class="field">
                    <div class="field-label">Key Quotes</div>
                    <div class="field-value">${(analysis.key_quotes || []).map(q => `"${q}"`).join('<br>') || 'None extracted'}</div>
                </div>
                <div class="field">
                    <div class="field-label">Red Flags</div>
                    <div class="field-value">${(analysis.red_flags || []).join(', ') || 'None identified'}</div>
                </div>
                <div class="field">
                    <div class="field-label">Summary</div>
                    <div class="field-value">${analysis.factual_summary || 'N/A'}</div>
                </div>
                <div class="field">
                    <div class="field-label">💡 Documentation Tip</div>
                    <div class="field-value">${analysis.documentation_tips || 'N/A'}</div>
                </div>
            `;
            document.getElementById('ai-analysis-result').style.display = 'block';
        }
        
        // Load timeline
        async function loadTimeline() {
            try {
                const response = await fetch('/api/incidents');
                const incidents = await response.json();
                
                // Stats
                const statsHtml = `
                    <div class="stat-card"><div class="number">${incidents.length}</div><div class="label">Total Incidents</div></div>
                    <div class="stat-card"><div class="number">${new Set(incidents.flatMap(i => i.people || [])).size}</div><div class="label">People Involved</div></div>
                    <div class="stat-card"><div class="number">${new Set(incidents.flatMap(i => i.categories || (i.ai_analysis?.detected_patterns || []))).size}</div><div class="label">Pattern Types</div></div>
                `;
                document.getElementById('timeline-stats').innerHTML = statsHtml;
                
                // Timeline
                if (incidents.length === 0) {
                    document.getElementById('timeline-content').innerHTML = '<p style="text-align: center; color: var(--text-secondary); padding: 40px;">No incidents documented yet. Start by adding your first incident.</p>';
                    return;
                }
                
                incidents.sort((a, b) => new Date(b.date) - new Date(a.date));
                
                const html = incidents.map(inc => {
                    const patterns = inc.categories || (inc.ai_analysis?.detected_patterns || []);
                    const severity = inc.ai_analysis?.severity || 'unknown';
                    return `
                        <div class="incident-card">
                            <div class="incident-header">
                                <div>
                                    <span class="incident-id">Incident #${inc.id}</span>
                                    <span class="incident-date">📅 ${inc.date}</span>
                                </div>
                                <span class="incident-severity severity-${severity}">${severity}</span>
                            </div>
                            <div class="incident-content">${escapeHtml(inc.content)}</div>
                            ${inc.user_notes ? `<div class="incident-notes">📝 ${escapeHtml(inc.user_notes)}</div>` : ''}
                            <div class="incident-tags">
                                ${(inc.people || []).map(p => `<span class="tag tag-person">👤 ${escapeHtml(p)}</span>`).join('')}
                                ${patterns.map(c => `<span class="tag tag-pattern">${c.replace(/_/g, ' ')}</span>`).join('')}
                            </div>
                        </div>
                    `;
                }).join('');
                
                document.getElementById('timeline-content').innerHTML = html;
            } catch (e) {
                document.getElementById('timeline-content').innerHTML = '<p style="color: var(--danger);">Error loading timeline.</p>';
            }
        }
        
        // Pattern analysis
        async function runPatternAnalysis() {
            const btn = event.target;
            btn.innerHTML = '<span class="spinner"></span> Analyzing all incidents...';
            btn.disabled = true;
            
            try {
                const response = await fetch('/api/analyze-patterns');
                const analysis = await response.json();
                
                let html = '';
                
                if (analysis.error) {
                    html = `<p style="color: var(--warning);">${analysis.error}</p>`;
                } else {
                    html = `
                        <div class="stats-grid">
                            <div class="stat-card"><div class="number">${analysis.total_incidents || 0}</div><div class="label">Incidents Analyzed</div></div>
                            <div class="stat-card"><div class="number">${analysis.hr_readiness_score || '?'}/10</div><div class="label">HR Readiness</div></div>
                        </div>
                        
                        <h4 style="margin: 20px 0 15px;">📊 Recurring Patterns</h4>
                        ${(analysis.recurring_patterns || []).map(p => `
                            <div class="progress-bar">
                                <span class="label">${p.pattern?.replace(/_/g, ' ') || 'Unknown'}</span>
                                <div class="bar"><div class="fill" style="width: ${Math.min((p.frequency || 0) / (analysis.total_incidents || 1) * 100, 100)}%"></div></div>
                                <span class="count">${p.frequency || 0}x</span>
                            </div>
                        `).join('')}
                        
                        <h4 style="margin: 25px 0 15px;">📈 Escalation Assessment</h4>
                        <p style="background: var(--bg-secondary); padding: 15px; border-radius: 8px;">${analysis.escalation_assessment || 'Unable to assess'}</p>
                        
                        <h4 style="margin: 25px 0 15px;">🎯 Strongest Evidence</h4>
                        <ul style="list-style: none;">
                            ${(analysis.strongest_evidence || []).map(e => `<li style="padding: 8px 0; border-bottom: 1px solid var(--border);">• ${e}</li>`).join('')}
                        </ul>
                        
                        <h4 style="margin: 25px 0 15px;">📋 Documentation Gaps</h4>
                        <ul style="list-style: none;">
                            ${(analysis.documentation_gaps || []).map(g => `<li style="padding: 8px 0; color: var(--warning);">⚠️ ${g}</li>`).join('')}
                        </ul>
                        
                        <h4 style="margin: 25px 0 15px;">✅ Recommended Actions</h4>
                        <ul style="list-style: none;">
                            ${(analysis.recommended_actions || []).map(a => `<li style="padding: 8px 0;">→ ${a}</li>`).join('')}
                        </ul>
                        
                        <div style="background: var(--bg-secondary); padding: 15px; border-radius: 8px; margin-top: 20px;">
                            <strong>HR Readiness:</strong> ${analysis.hr_readiness_explanation || 'N/A'}
                        </div>
                    `;
                }
                
                document.getElementById('patterns-result').innerHTML = html;
            } catch (e) {
                document.getElementById('patterns-result').innerHTML = `<p style="color: var(--danger);">Error: ${e.message}</p>`;
            } finally {
                btn.innerHTML = '🤖 Run Cross-Incident Analysis';
                btn.disabled = false;
            }
        }
        
        // Get questions
        async function getQuestions() {
            const btn = event.target;
            btn.innerHTML = '<span class="spinner"></span> Generating...';
            btn.disabled = true;
            
            try {
                const response = await fetch('/api/suggest-questions');
                const questions = await response.json();
                
                const html = questions.map((q, i) => `
                    <li><span class="num">${i + 1}</span><span>${q}</span></li>
                `).join('');
                
                document.getElementById('questions-list').innerHTML = html;
            } catch (e) {
                document.getElementById('questions-list').innerHTML = `<li style="color: var(--danger);">Error: ${e.message}</li>`;
            } finally {
                btn.innerHTML = '💡 Generate Questions';
                btn.disabled = false;
            }
        }
        
        // Generate narrative
        async function generateNarrative() {
            const btn = event.target;
            const focus = document.getElementById('narrative-focus').value.trim();
            btn.innerHTML = '<span class="spinner"></span> Generating narrative...';
            btn.disabled = true;
            
            try {
                const response = await fetch('/api/generate-narrative', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ focus })
                });
                const data = await response.json();
                
                currentNarrative = data.narrative || 'No narrative generated.';
                document.getElementById('narrative-result').innerHTML = `<div class="narrative-box">${escapeHtml(currentNarrative)}</div>`;
                document.getElementById('narrative-actions').style.display = 'flex';
            } catch (e) {
                document.getElementById('narrative-result').innerHTML = `<p style="color: var(--danger);">Error: ${e.message}</p>`;
            } finally {
                btn.innerHTML = '📝 Generate HR Narrative';
                btn.disabled = false;
            }
        }
        
        function copyNarrative() {
            navigator.clipboard.writeText(currentNarrative);
            alert('Narrative copied to clipboard!');
        }
        
        function downloadNarrative() {
            const blob = new Blob([currentNarrative], { type: 'text/plain' });
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = `hr_narrative_${new Date().toISOString().split('T')[0]}.txt`;
            a.click();
        }
        
        // Load knowledge graph with visual network
        async function loadGraph() {
            try {
                const response = await fetch('/api/graph');
                const graph = await response.json();
                
                const nodes = graph.nodes || [];
                const edges = graph.edges || [];
                
                if (nodes.length === 0) {
                    document.getElementById('graph-container').innerHTML = '<div style="display:flex;align-items:center;justify-content:center;height:100%;color:var(--text-secondary);">No data yet. Add incidents to build the knowledge graph.</div>';
                    return;
                }
                
                // Group by type
                const people = nodes.filter(n => n.type === 'person');
                const patterns = nodes.filter(n => n.type === 'pattern');
                const incidents = nodes.filter(n => n.type === 'incident');
                
                // Create SVG-based network visualization
                const width = 800;
                const height = 400;
                const centerX = width / 2;
                const centerY = height / 2;
                
                // Position nodes in circles by type
                const positionedNodes = [];
                
                // Incidents in center
                incidents.forEach((n, i) => {
                    const angle = (2 * Math.PI * i) / Math.max(incidents.length, 1);
                    const radius = 60;
                    positionedNodes.push({
                        ...n,
                        x: centerX + radius * Math.cos(angle),
                        y: centerY + radius * Math.sin(angle),
                        color: '#667eea'
                    });
                });
                
                // People on left
                people.forEach((n, i) => {
                    const startY = (height - people.length * 50) / 2;
                    positionedNodes.push({
                        ...n,
                        x: 100,
                        y: startY + i * 50 + 25,
                        color: '#10b981'
                    });
                });
                
                // Patterns on right
                patterns.forEach((n, i) => {
                    const startY = (height - patterns.length * 40) / 2;
                    positionedNodes.push({
                        ...n,
                        x: width - 100,
                        y: startY + i * 40 + 20,
                        color: '#f59e0b'
                    });
                });
                
                // Build node lookup
                const nodeMap = {};
                positionedNodes.forEach(n => nodeMap[n.id] = n);
                
                // Create SVG
                let svg = `<svg viewBox="0 0 ${width} ${height}" style="width:100%;height:100%;background:var(--bg-secondary);border-radius:10px;">`;
                
                // Draw edges first (behind nodes)
                edges.forEach(e => {
                    const source = nodeMap[e.source];
                    const target = nodeMap[e.target];
                    if (source && target) {
                        svg += `<line x1="${source.x}" y1="${source.y}" x2="${target.x}" y2="${target.y}" stroke="#3a3a5a" stroke-width="1" opacity="0.5"/>`;
                    }
                });
                
                // Draw nodes
                positionedNodes.forEach(n => {
                    const radius = n.type === 'incident' ? 20 : 12;
                    svg += `<circle cx="${n.x}" cy="${n.y}" r="${radius}" fill="${n.color}" opacity="0.8"/>`;
                    
                    // Labels
                    const labelX = n.type === 'person' ? n.x - 80 : (n.type === 'pattern' ? n.x + 20 : n.x);
                    const anchor = n.type === 'person' ? 'end' : 'start';
                    const label = n.label.length > 15 ? n.label.substring(0, 15) + '...' : n.label;
                    
                    if (n.type !== 'incident') {
                        svg += `<text x="${labelX}" y="${n.y + 4}" fill="#e0e0e0" font-size="11" text-anchor="${anchor}">${label}</text>`;
                    }
                });
                
                // Legend
                svg += `
                    <rect x="10" y="10" width="120" height="80" fill="var(--bg-card)" rx="5" opacity="0.9"/>
                    <circle cx="25" cy="30" r="8" fill="#10b981"/>
                    <text x="40" y="34" fill="#e0e0e0" font-size="10">People (${people.length})</text>
                    <circle cx="25" cy="50" r="8" fill="#667eea"/>
                    <text x="40" y="54" fill="#e0e0e0" font-size="10">Incidents (${incidents.length})</text>
                    <circle cx="25" cy="70" r="8" fill="#f59e0b"/>
                    <text x="40" y="74" fill="#e0e0e0" font-size="10">Patterns (${patterns.length})</text>
                `;
                
                svg += '</svg>';
                
                document.getElementById('graph-container').innerHTML = svg;
                
                document.getElementById('graph-stats').innerHTML = `
                    <div style="margin-top:15px; display:grid; grid-template-columns:repeat(3,1fr); gap:10px; font-size:0.85em;">
                        <div style="background:var(--bg-secondary);padding:12px;border-radius:8px;text-align:center;">
                            <div style="color:#10b981;font-weight:bold;">${people.length}</div>
                            <div style="color:var(--text-secondary);">People</div>
                        </div>
                        <div style="background:var(--bg-secondary);padding:12px;border-radius:8px;text-align:center;">
                            <div style="color:#667eea;font-weight:bold;">${incidents.length}</div>
                            <div style="color:var(--text-secondary);">Incidents</div>
                        </div>
                        <div style="background:var(--bg-secondary);padding:12px;border-radius:8px;text-align:center;">
                            <div style="color:#f59e0b;font-weight:bold;">${patterns.length}</div>
                            <div style="color:var(--text-secondary);">Patterns</div>
                        </div>
                    </div>
                    <p style="color: var(--text-secondary); margin-top:10px; font-size:0.85em;">
                        ${edges.length} connections showing relationships between people, incidents, and patterns.
                    </p>
                `;
            } catch (e) {
                document.getElementById('graph-container').innerHTML = '<div style="color:var(--danger);padding:20px;">Error loading graph: ' + e.message + '</div>';
            }
        }
        
        // Import data
        async function importData(event) {
            const file = event.target.files[0];
            if (!file) return;
            
            try {
                const text = await file.text();
                const data = JSON.parse(text);
                
                const response = await fetch('/api/import', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ data })
                });
                const result = await response.json();
                
                showMessage('import-message', `✅ Imported ${result.imported} incidents successfully!`, 'success');
            } catch (e) {
                showMessage('import-message', `Error importing: ${e.message}`, 'error');
            }
            
            event.target.value = '';
        }
        
        // Export functions
        async function exportJSON() {
            const response = await fetch('/api/incidents');
            const data = await response.json();
            const exportData = {
                exported_at: new Date().toISOString(),
                exported_by: 'Workplace Documentation Tool',
                incidents: data
            };
            const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = `workplace_docs_${new Date().toISOString().split('T')[0]}.json`;
            a.click();
        }
        
        async function exportText() {
            const response = await fetch('/api/incidents');
            const incidents = await response.json();
            
            let text = 'WORKPLACE DOCUMENTATION RECORD\\n';
            text += 'Generated: ' + new Date().toLocaleString() + '\\n';
            text += '='.repeat(70) + '\\n\\n';
            
            incidents.forEach(inc => {
                text += `INCIDENT #${inc.id}\\n`;
                text += `Date: ${inc.date}\\n`;
                text += `People: ${(inc.people || []).join(', ')}\\n`;
                text += `Patterns: ${(inc.categories || inc.ai_analysis?.detected_patterns || []).join(', ')}\\n`;
                if (inc.ai_analysis?.severity) text += `Severity: ${inc.ai_analysis.severity}\\n`;
                text += `\\nContent:\\n${inc.content}\\n`;
                if (inc.user_notes) text += `\\nNotes: ${inc.user_notes}\\n`;
                if (inc.ai_analysis?.factual_summary) text += `\\nAI Summary: ${inc.ai_analysis.factual_summary}\\n`;
                text += '\\n' + '-'.repeat(70) + '\\n\\n';
            });
            
            const blob = new Blob([text], { type: 'text/plain' });
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = `workplace_docs_${new Date().toISOString().split('T')[0]}.txt`;
            a.click();
        }
        
        async function copyAllData() {
            const response = await fetch('/api/incidents');
            const data = await response.json();
            await navigator.clipboard.writeText(JSON.stringify(data, null, 2));
            alert('Data copied to clipboard!');
        }
        
        // Utilities
        function showMessage(elementId, message, type) {
            const el = document.getElementById(elementId);
            el.textContent = message;
            el.className = 'message ' + type;
            setTimeout(() => { el.className = 'message'; }, 5000);
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text || '';
            return div.innerHTML;
        }
    </script>
</body>
</html>
"""

# =============================================================================
# HTTP SERVER
# =============================================================================

class DocHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler for the documentation tool."""
    
    analyzer = None
    analyzer_initializing = False
    
    @classmethod
    def get_analyzer(cls):
        return AIAnalyzer.get_instance()
    
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode())
            
        elif self.path == '/api/incidents':
            self.send_json(load_incidents())
            
        elif self.path == '/api/graph':
            self.send_json(load_graph())
            
        elif self.path == '/api/ai-status':
            analyzer = self.get_analyzer()
            self.send_json({"ready": analyzer.ready})
            
            # Initialize AI in background if not ready
            if not analyzer.ready and not DocHandler.analyzer_initializing:
                DocHandler.analyzer_initializing = True
                threading.Thread(target=self._init_ai_background, daemon=True).start()
            
        elif self.path == '/api/analyze-patterns':
            self._handle_async(self._analyze_patterns())
            
        elif self.path == '/api/suggest-questions':
            self._handle_async(self._suggest_questions())
            
        else:
            self.send_error(404)
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode())
        
        if self.path == '/api/save':
            self._handle_async(self._save_incident(data))
            
        elif self.path == '/api/generate-narrative':
            self._handle_async(self._generate_narrative(data))
            
        elif self.path == '/api/import':
            self._handle_import(data)
            
        else:
            self.send_error(404)
    
    def _handle_async(self, coro):
        """Run async function using the AI analyzer's dedicated event loop."""
        try:
            analyzer = self.get_analyzer()
            result = analyzer._run_async(coro, timeout=90)
            self.send_json(result)
        except asyncio.TimeoutError:
            self.send_json({"error": "Request timed out. Try 'Quick Save' without AI."})
        except Exception as e:
            print(f"Async handler error: {e}")
            traceback.print_exc()
            self.send_json({"error": str(e)})
        except Exception as e:
            print(f"Async handler error: {e}")
            traceback.print_exc()
            self.send_json({"error": str(e)})
    
    def _init_ai_background(self):
        """Initialize AI in background using dedicated loop."""
        try:
            analyzer = self.get_analyzer()
            analyzer.initialize_sync()
        except Exception as e:
            print(f"AI init error: {e}")
        finally:
            DocHandler.analyzer_initializing = False
    
    async def _save_incident(self, data):
        """Save an incident with optional AI analysis."""
        incidents = load_incidents()
        
        incident = {
            "id": len(incidents) + 1,
            "timestamp": datetime.now().isoformat(),
            "date": data.get('date', datetime.now().strftime('%Y-%m-%d')),
            "content": data.get('content', ''),
            "user_notes": data.get('userNotes', ''),
            "people": data.get('people', []),
            "categories": data.get('categories', [])
        }
        
        ai_analysis = None
        if data.get('useAI', False):
            analyzer = self.get_analyzer()
            if analyzer.ready:
                ai_analysis = await analyzer.analyze_incident(
                    data.get('content', ''),
                    data.get('userNotes', '')
                )
                incident['ai_analysis'] = ai_analysis
                
                # Use AI-detected patterns if user didn't select any
                if not incident['categories'] and ai_analysis.get('detected_patterns'):
                    incident['categories'] = ai_analysis['detected_patterns']
        
        incidents.append(incident)
        save_incidents(incidents)
        
        # Update knowledge graph
        update_knowledge_graph(incident)
        
        return {"success": True, "incident": incident, "ai_analysis": ai_analysis}
    
    async def _analyze_patterns(self):
        """Analyze patterns across all incidents."""
        incidents = load_incidents()
        if len(incidents) < 1:
            return {"error": "Need at least 1 incident for pattern analysis"}
        
        analyzer = self.get_analyzer()
        if not analyzer.ready:
            await analyzer.initialize()
        
        return await analyzer.analyze_all_patterns(incidents)
    
    async def _generate_narrative(self, data):
        """Generate HR narrative."""
        incidents = load_incidents()
        if not incidents:
            return {"narrative": "No incidents to generate narrative from."}
        
        analyzer = self.get_analyzer()
        if not analyzer.ready:
            await analyzer.initialize()
        
        narrative = await analyzer.generate_hr_narrative(
            incidents,
            data.get('focus')
        )
        return {"narrative": narrative}
    
    async def _suggest_questions(self):
        """Get suggested questions."""
        incidents = load_incidents()
        if not incidents:
            return ["Document some incidents first to get personalized questions."]
        
        analyzer = self.get_analyzer()
        if not analyzer.ready:
            await analyzer.initialize()
        
        return await analyzer.suggest_questions(incidents)
    
    def _handle_import(self, data):
        """Import data from exported JSON."""
        try:
            imported_data = data.get('data', {})
            imported_incidents = imported_data.get('incidents', imported_data) if isinstance(imported_data, dict) else imported_data
            
            if not isinstance(imported_incidents, list):
                self.send_json({"error": "Invalid data format"})
                return
            
            incidents = load_incidents()
            start_id = len(incidents) + 1
            
            imported_count = 0
            for inc in imported_incidents:
                # Avoid duplicates by checking content
                if any(existing.get('content') == inc.get('content') for existing in incidents):
                    continue
                
                new_inc = {
                    "id": start_id + imported_count,
                    "timestamp": datetime.now().isoformat(),
                    "date": inc.get('date', 'unknown'),
                    "content": inc.get('content', ''),
                    "user_notes": inc.get('user_notes', ''),
                    "people": inc.get('people', []),
                    "categories": inc.get('categories', []),
                    "ai_analysis": inc.get('ai_analysis'),
                    "imported": True
                }
                incidents.append(new_inc)
                update_knowledge_graph(new_inc)
                imported_count += 1
            
            save_incidents(incidents)
            self.send_json({"success": True, "imported": imported_count})
            
        except Exception as e:
            self.send_json({"error": str(e)})
    
    def send_json(self, data):
        """Send JSON response."""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode())
    
    def log_message(self, format, *args):
        pass  # Suppress logging


def start_server(port=PORT):
    """Start the web server."""
    ensure_data_dir()
    
    with socketserver.TCPServer(("", port), DocHandler) as httpd:
        print(f"""
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║     📝  WORKPLACE DOCUMENTATION TOOL                                     ║
║                                                                          ║
╠══════════════════════════════════════════════════════════════════════════╣
║                                                                          ║
║  ✅ Server running!                                                      ║
║                                                                          ║
║  🌐 Open in your browser:  http://localhost:{port}                         ║
║                                                                          ║
║  📁 Data stored at: {DATA_DIR}
║                                                                          ║
║  🔒 All data stays LOCAL on your computer                                ║
║                                                                          ║
║  🤖 AI features powered by GitHub Copilot SDK                            ║
║                                                                          ║
║  Press Ctrl+C to stop                                                    ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
""")
        
        # Open browser
        webbrowser.open(f'http://localhost:{port}')
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Server stopped.")


if __name__ == "__main__":
    # Rebuild graph from existing incidents on startup
    rebuild_graph_from_incidents()
    start_server()
