# Changelog

## v0.2.0 — Security - 04/09/2026

### Added
- User password hashing (bcrypt) instead of plaintext storage
- User-friendly error handling for MySQL (`DatabaseConnectionError`) and MongoDB (`PyMongoError`) connection issues instead of raw tracebacks
- Validation for empty usernames/passwords during registration

### Changed
- `users.password`: `VARCHAR(100)` → `VARCHAR(255)` to accommodate bcrypt hashes

### Security
- Passwords are no longer compared directly within SQL queries (`WHERE password = %s`); verification is now performed at the application level using `bcrypt.checkpw`

---

## v0.1.0 — Project recovery - 03/09/2026

### Added
- Project structure restored following repository loss: `db/`, `services/`, `user_interface/`
- MySQL/MongoDB configuration via `.env` (`python-dotenv`), eliminating hardcoded credentials
- Separate read/edit MySQL connections at the code level
- `.env.example`, `.gitignore`, `requirements.txt`, `README.md`, `ROADMAP.md`, `CHANGELOG.md`

### Security
- Initial repository commit contains no secrets
