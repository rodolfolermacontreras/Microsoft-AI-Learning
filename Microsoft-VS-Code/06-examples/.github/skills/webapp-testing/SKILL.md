---
name: webapp-testing
description: Run and debug web application tests using Playwright and Jest. Use this skill when testing web applications, fixing failing tests, or setting up test infrastructure.
---

# Web Application Testing

## When to Use This Skill

- Running or debugging web application tests
- Setting up test infrastructure for a new project
- Fixing failing Playwright or Jest tests
- Writing new test cases for web features

## Playwright Tests

### Setup Check

1. Verify `playwright.config.ts` exists
2. Check for `@playwright/test` in dependencies
3. If missing, run: `npm install -D @playwright/test && npx playwright install`

### Running Tests

```bash
# Run all tests
npx playwright test

# Run specific test file
npx playwright test tests/login.spec.ts

# Run with UI mode for debugging
npx playwright test --ui

# Run headed (visible browser)
npx playwright test --headed
```

### Writing Tests

```typescript
import { test, expect } from '@playwright/test';

test('should display login form', async ({ page }) => {
    await page.goto('/login');
    await expect(page.getByRole('heading', { name: 'Login' })).toBeVisible();
    await expect(page.getByLabel('Email')).toBeVisible();
    await expect(page.getByLabel('Password')).toBeVisible();
});
```

## Jest Tests

### Running Tests

```bash
# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test
npm test -- --testPathPattern=auth
```

### Debugging Failures

1. Read the full error message and stack trace
2. Identify the root cause (not just the symptom)
3. Check if the issue is in the test or the implementation
4. Fix the root cause
5. Re-run to confirm
