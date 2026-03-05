---
name: Python Standards
description: Coding conventions for Python files
applyTo: '**/*.py'
---

# Python Coding Standards

- Follow PEP 8 style guide
- Use type hints for all function signatures
- Write docstrings for all public functions and classes
- Use 4 spaces for indentation (never tabs)
- Prefer f-strings over .format() or % formatting
- Use `with` statements for resource management (files, connections)
- Import order: stdlib, then third-party, then local
- Use specific exception types, never bare `except:`
