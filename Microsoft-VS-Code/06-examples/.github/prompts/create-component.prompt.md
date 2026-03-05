---
name: create-component
description: Scaffold a new React component with tests and stories
argument-hint: ComponentName
agent: agent
tools: ['edit', 'create', 'read', 'search']
---

Create a new React component named ${input:name} with the following files:

1. **Component**: `src/components/${input:name}/index.tsx`
   - Functional component with TypeScript props interface
   - Use CSS modules for styling

2. **Styles**: `src/components/${input:name}/styles.module.css`
   - Mobile-first responsive design

3. **Tests**: `src/components/${input:name}/${input:name}.test.tsx`
   - Render test, props test, interaction test

4. **Stories**: `src/components/${input:name}/${input:name}.stories.tsx`
   - Default story, with-props variants

Follow the patterns established in existing components. Reference
[project standards](../copilot-instructions.md) for coding conventions.
