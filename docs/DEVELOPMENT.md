# Development Guide

## Local Setup

### Prerequisites

- Python 3.12+
- Node.js 18+
- MongoDB Atlas account
- Cloudinary account

### Backend Setup

```bash
cd smriti-backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd smriti-frontend
npm install
cp .env.example .env
# Edit .env with your credentials
npm start
```

## Development Workflow

1. Create feature branch
2. Make changes
3. Write/update tests
4. Run tests locally
5. Commit with conventional commits
6. Push and create PR

## Code Style

### Python

- Follow PEP 8
- Use Black for formatting
- Type hints where possible

### JavaScript

- Use ESLint and Prettier
- Follow React Native best practices
- Use functional components

## Testing

- Write tests for new features
- Maintain >80% coverage
- Run tests before committing
