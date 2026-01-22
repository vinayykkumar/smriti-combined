# Security Guidelines

## Authentication

- Use JWT tokens for all authenticated requests
- Tokens expire after 30 days
- Store tokens securely (AsyncStorage for mobile)

## Password Security

- Minimum 6 characters
- Hashed with bcrypt (10 rounds)
- Never stored in plain text

## API Security

- CORS configured for specific origins
- Rate limiting (if implemented)
- Input validation on all endpoints
- SQL injection prevention (using ODM)

## Environment Variables

- Never commit `.env` files
- Use strong, random `SECRET_KEY`
- Rotate keys periodically

## Best Practices

1. Always validate user input
2. Use HTTPS in production
3. Keep dependencies updated
4. Regular security audits
5. Monitor for suspicious activity

## Reporting Security Issues

Report security vulnerabilities privately to the maintainer.
