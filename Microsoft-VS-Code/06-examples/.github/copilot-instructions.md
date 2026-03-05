# Project Coding Guidelines

## Code Style
- Use semantic HTML5 elements (header, main, section, article)
- Prefer modern JavaScript (ES6+): const/let, arrow functions, template literals
- Use TypeScript strict mode when available

## Naming Conventions
- PascalCase for component names, interfaces, and type aliases
- camelCase for variables, functions, and methods
- Prefix private class members with underscore (_)
- Use ALL_CAPS for constants

## Code Quality
- Use meaningful variable and function names that clearly describe their purpose
- Include helpful comments for complex logic
- Add error handling for user inputs and API calls
- No bare except/catch blocks -- always handle specific errors

## Testing
- Write tests for all public functions
- Use descriptive test names: "should return 404 when user not found"
- Follow Arrange-Act-Assert pattern

## Git
- Use conventional commits: feat:, fix:, docs:, refactor:, test:, chore:
- One commit per logical change
