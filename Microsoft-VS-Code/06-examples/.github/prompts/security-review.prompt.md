---
name: security-review
description: Audit code for common security vulnerabilities
tools: ['read', 'search', 'codebase', 'problems']
agent: ask
---

Perform a security review of the current project. Check for:

1. **Injection**: SQL injection, command injection, XSS
2. **Credentials**: Hardcoded API keys, tokens, passwords
3. **Authentication**: Missing or weak auth checks
4. **Authorization**: Broken access control, privilege escalation
5. **Data exposure**: Sensitive data in logs, error messages, or responses
6. **Dependencies**: Known vulnerable packages (check package.json/requirements.txt)
7. **Configuration**: Overly permissive CORS, missing security headers
8. **Input validation**: Missing or insufficient validation
9. **Cryptography**: Weak algorithms, insecure random generation

Provide findings ranked by severity: critical, high, medium, low.
For each finding, explain the risk and suggest a specific fix.
