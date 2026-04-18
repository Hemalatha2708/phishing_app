# Security Documentation

## Overview

This document outlines the security features implemented in the Phishing Detection Application and best practices for deployment.

## Security Features Implemented

### 1. Authentication & Authorization

✅ **Implemented:**
- Password hashing using werkzeug (`generate_password_hash`, `check_password_hash`)
- Parameterized SQL queries (prevents SQL injection)
- Session-based authentication
- Login/logout functionality
- Password validation on registration

**Best Practices:**
- Enforce strong passwords (minimum 6 chars with uppercase, lowercase, digits)
- Implement account lockout after failed login attempts (recommended: 5 attempts)
- Add two-factor authentication (2FA) for sensitive accounts
- Implement session timeout (recommended: 30 minutes of inactivity)

### 2. CSRF Protection

✅ **Implemented:**
- Flask-WTF CSRF protection on all forms
- CSRF tokens generated and validated automatically
- Tokens embedded in HTML forms: `{{ csrf_token() }}`

**Configuration:**
- CSRF tokens enabled by default
- Token validation on all POST/PUT/DELETE requests
- Configure CSRF in Flask via `CSRFProtect(app)`

### 3. Input Validation

✅ **Implemented:**
- Email validation using email-validator
- Username validation (alphanumeric, length checks)
- Password strength validation
- URL format validation before feature extraction
- String sanitization with `sanitize_string()`

**Validation Rules:**
- **Username**: 3-50 chars, alphanumeric + underscore/hyphen
- **Email**: Valid RFC 5322 format
- **Password**: Min 6 chars, must contain uppercase, lowercase, and digit
- **URL**: Must start with http:// or https://, max 2048 chars

### 4. Configuration Management

✅ **Implemented:**
- Environment-based configuration via `config.py`
- Support for `.env` files using `python-dotenv`
- No hardcoded secrets in codebase
- Separate configs for development, testing, production

**Environment Variables:**
```env
SECRET_KEY=                # Flask session key (MUST be set in production)
DB_HOST=localhost          # Database host
DB_USER=root               # Database user
DB_PASSWORD=               # Database password (REQUIRED)
DB_NAME=phishing           # Database name
FLASK_ENV=development      # development|testing|production
DEBUG=False                # Disable debug mode in production
LOG_LEVEL=INFO             # DEBUG|INFO|WARNING|ERROR|CRITICAL
```

### 5. Logging & Monitoring

✅ **Implemented:**
- Structured logging to file and console
- Security events logged:
  - User login attempts (success and failure)
  - User registration
  - Prediction requests
  - Database errors
  - Authentication failures
  - Model loading failures

**Log File:** `phishing_app.log` (configured via `LOG_FILE` env var)

**Log Levels:**
- `DEBUG`: Detailed execution info (development only)
- `INFO`: General events (logins, registrations)
- `WARNING`: Unexpected conditions
- `ERROR`: Error events with stack traces
- `CRITICAL`: Critical failures requiring immediate attention

### 6. Database Security

✅ **Implemented:**
- Parameterized queries (prevents SQL injection)
- Connection pooling with credential management
- Foreign key constraints
- User data separated from authentication data
- Indexes on frequently queried columns

**Best Practices:**
- Use least privilege principle for DB user
- Enable database backups
- Restrict database network access (firewall rules)
- Use encrypted connections (SSL/TLS) for remote databases
- Regularly review access logs

### 7. Error Handling

✅ **Implemented:**
- Try-catch blocks on critical operations
- User-friendly error messages
- Detailed error logging for debugging
- Graceful degradation (app continues if non-critical feature fails)
- Error handler pages (404, 500)

## Vulnerability Mitigations

### SQL Injection
✅ **Mitigated By:**
- Parameterized queries with `%s` placeholders
- Never concatenating user input into SQL queries
- Example: `cursor.execute("SELECT * FROM profiles WHERE username=%s", (username,))`

### Cross-Site Scripting (XSS)
✅ **Mitigated By:**
- Jinja2 auto-escaping (enabled by default)
- `{{ variable }}` syntax automatically escapes HTML
- Input sanitization before storage
- Content Security Policy (CSP) headers recommended

### Cross-Site Request Forgery (CSRF)
✅ **Mitigated By:**
- Flask-WTF CSRF protection
- CSRF tokens in all forms: `{{ csrf_token() }}`
- Token validation on all state-changing operations
- SameSite cookie attribute (recommended)

### Password-Related
✅ **Mitigated By:**
- Password hashing with salting (werkzeug default)
- Never storing plain text passwords
- Password strength validation on registration
- Secure password transmission (HTTPS recommended)

## Production Deployment Checklist

### Before Deployment

- [ ] Set strong `SECRET_KEY` in production:
  ```bash
  python -c "import secrets; print(secrets.token_hex(32))"
  ```

- [ ] Set `FLASK_ENV=production` and `DEBUG=False`

- [ ] Configure database credentials in `.env`:
  ```bash
  DB_PASSWORD=strong-secure-password
  ```

- [ ] Use environment variables, not `.env` file in production

- [ ] Enable HTTPS/SSL:
  - Obtain SSL certificate (Let's Encrypt recommended)
  - Configure reverse proxy (nginx/Apache)
  - Redirect HTTP to HTTPS

- [ ] Set security headers:
  ```python
  @app.after_request
  def set_security_headers(response):
      response.headers['X-Content-Type-Options'] = 'nosniff'
      response.headers['X-Frame-Options'] = 'SAMEORIGIN'
      response.headers['X-XSS-Protection'] = '1; mode=block'
      response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
      return response
  ```

- [ ] Implement rate limiting to prevent brute force attacks
  - Login endpoint: max 5 attempts per 15 minutes per IP
  - Prediction endpoint: max 100 requests per hour per user

- [ ] Database security:
  - Use strong password for DB user
  - Create separate DB user with limited privileges
  - Enable binary logging for audit trail
  - Regular backups (daily minimum)

- [ ] Application server:
  - Use production WSGI server (Gunicorn, uWSGI) instead of Flask dev server
  - Run behind reverse proxy (nginx, Apache)
  - Set proper file permissions (no world-readable secrets)
  - Enable firewall rules
  - Regularly update dependencies

- [ ] Monitoring & Alerting:
  - Set up log aggregation and monitoring
  - Configure alerts for errors and suspicious activity
  - Monitor database performance
  - Track model prediction accuracy over time

### During Deployment

- [ ] Test all security features in staging environment
- [ ] Run security scanning tools (OWASP ZAP, Burp Suite)
- [ ] Perform penetration testing
- [ ] Verify HTTPS/SSL configuration
- [ ] Test CSRF protection with form submissions

### After Deployment

- [ ] Monitor logs for errors and security events
- [ ] Track user access patterns
- [ ] Monitor model accuracy and predictions
- [ ] Regularly backup database
- [ ] Keep dependencies updated
- [ ] Review security logs weekly
- [ ] Perform security audits quarterly

## Incident Response

### Potential Security Incidents

1. **Unusual Database Queries**
   - Check logs: `grep "error\|exception" phishing_app.log`
   - Review recent deployments
   - Check database query logs

2. **Failed Login Attempts**
   - Check for patterns in logs
   - Consider IP-based rate limiting
   - Investigate compromised credentials

3. **Prediction Accuracy Degradation**
   - May indicate data poisoning or model drift
   - Retrain models with recent clean data
   - Review prediction logs for anomalies

4. **Database Connection Issues**
   - Check database server status
   - Review connection pool configuration
   - Check network connectivity

## Security Best Practices

1. **Keep Dependencies Updated**
   ```bash
   pip list --outdated
   pip install --upgrade <package-name>
   ```

2. **Regularly Review Logs**
   - Check for suspicious authentication patterns
   - Monitor error rates
   - Track performance metrics

3. **Use Strong Passwords**
   - Database passwords: min 16 chars, mixed case, numbers, symbols
   - Flask SECRET_KEY: cryptographically random, min 32 chars

4. **Database User Privileges**
   ```sql
   -- Create limited privilege user for application
   CREATE USER 'phishing_app'@'localhost' IDENTIFIED BY 'strong-password';
   GRANT SELECT, INSERT, UPDATE ON phishing.* TO 'phishing_app'@'localhost';
   FLUSH PRIVILEGES;
   ```

5. **Network Security**
   - Firewall rules: only allow necessary ports (80, 443)
   - Database: restrict to localhost or specific app server
   - SSH: use key-based authentication, disable root login

6. **Backup & Recovery**
   - Daily database backups
   - Test restore procedures regularly
   - Store backups off-site

## Known Limitations

- **Model Accuracy**: Models trained on Test.csv dataset; accuracy depends on data quality
- **URL Analysis Only**: Analyzes URL structure, not webpage content
- **Requires HTTPS**: Deployment recommendation for security
- **Rate Limiting**: Not implemented; recommended to add at reverse proxy level
- **2FA**: Not implemented; recommended to add for user accounts

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/latest/security/)
- [SQL Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
- [CSRF Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)

## Security Contact

For security concerns or vulnerability reports, please follow responsible disclosure practices and contact the development team directly.
