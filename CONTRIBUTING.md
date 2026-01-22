# Contributing to Smriti 🌳

Thank you for your interest in contributing to Smriti! This document provides guidelines and instructions for contributing to the project.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Reporting Issues](#reporting-issues)

---

## 🤝 Code of Conduct

This project adheres to principles of mindfulness, respect, and minimalism. Please:

- Be respectful and considerate in all interactions
- Focus on the project's minimal, non-addictive philosophy
- Keep discussions constructive and solution-oriented

---

## 🚀 Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/smriti-combined.git
   cd smriti-combined
   ```
3. **Set up development environment** (see [README.md](./README.md))
4. **Create a branch** for your work:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

---

## 💻 Development Workflow

### Backend Development

```bash
cd smriti-backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd smriti-frontend
npm install
npm start
```

### Running Tests

**Backend:**
```bash
cd smriti-backend
pytest
```

**Frontend:**
```bash
cd smriti-frontend
npm test  # If test suite exists
```

---

## 📝 Coding Standards

### Python (Backend)

- Follow [PEP 8](https://pep8.org/) style guidelines
- Use type hints where appropriate
- Write docstrings for functions and classes
- Keep functions focused and single-purpose
- Use meaningful variable and function names

### JavaScript/TypeScript (Frontend)

- Follow ESLint configuration (if present)
- Use meaningful component and variable names
- Keep components small and focused
- Prefer functional components with hooks
- Add comments for complex logic

### General

- **Keep it minimal**: Align with the project's philosophy
- **Write clean code**: Code should be readable and maintainable
- **Add documentation**: Update README files when adding features
- **Test your changes**: Ensure existing tests pass and add new ones when needed

---

## 📦 Commit Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples

```
feat(backend): add user profile endpoint

Add GET /api/users/me endpoint to retrieve current user profile
information.

Closes #123
```

```
fix(frontend): resolve navigation issue on Android

Fixed navigation stack reset issue that occurred on Android devices
when returning from deep links.
```

---

## 🔄 Pull Request Process

1. **Update documentation** if you've changed functionality
2. **Ensure all tests pass** locally
3. **Update CHANGELOG.md** (if it exists) with your changes
4. **Create a pull request** with:
   - Clear title and description
   - Reference to related issues
   - Screenshots (for UI changes)
   - Testing instructions

### PR Checklist

- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] Changes tested locally

---

## 🐛 Reporting Issues

When reporting issues, please include:

- **Clear title** and description
- **Steps to reproduce** the issue
- **Expected behavior** vs **actual behavior**
- **Environment details** (OS, Node/Python versions, etc.)
- **Screenshots** (if applicable)
- **Error messages** or logs

### Issue Labels

- `bug`: Something isn't working
- `enhancement`: New feature or improvement
- `documentation`: Documentation improvements
- `question`: Further information needed
- `good first issue`: Good for newcomers

---

## 🎯 Project Philosophy

Remember: Smriti is designed to be **minimal and non-addictive**. When contributing:

- ✅ **Do**: Keep features simple and focused
- ✅ **Do**: Maintain chronological, time-based ordering
- ✅ **Do**: Prioritize user privacy and security
- ❌ **Don't**: Add engagement metrics, likes, or algorithms
- ❌ **Don't**: Implement infinite scroll or auto-refresh
- ❌ **Don't**: Add features that encourage addictive behavior

---

## 📞 Questions?

If you have questions about contributing:

- Open an issue with the `question` label
- Contact the project maintainer
- Check existing documentation in `docs/` folders

---

Thank you for contributing to Smriti! 🙏
