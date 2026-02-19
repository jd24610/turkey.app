# Copilot Instructions for Capstone Project

## Project Overview
This is a Python-based capstone project with SQLite database integration. The primary module is `sqlite.py`, which will serve as the foundation for database operations.

## Architecture & Components

### Core Structure
- **sqlite.py**: Main database module (currently being developed)
  - Expected to handle SQLite connection management, schema operations, and data persistence
  - Use this as the entry point for all database-related functionality

### Database Patterns
When implementing database features:
1. **Connection Management**: Use context managers for SQLite connections to ensure proper cleanup
2. **Schema Initialization**: Keep schema definitions in a dedicated function or module section
3. **Query Patterns**: Use parameterized queries to prevent SQL injection

## Development Conventions

### Code Style
- Follow PEP 8 for all Python code
- Use type hints where practical for clarity
- Include docstrings for modules and key functions

### Database Operations
- Always use `sqlite3` with connection context managers:
  ```python
  with sqlite3.connect(db_path) as conn:
      cursor = conn.cursor()
      # operations here
  ```
- Execute transactions explicitly with commit/rollback semantics

## Key Files & Their Purpose
- `sqlite.py` - Database layer; implement all SQLite operations here

## Testing & Validation
- Create tests as features are added to `sqlite.py`
- Test database migrations and schema changes independently
- Verify parameterized query usage for security

## Getting Started
1. Populate `sqlite.py` with database connection initialization
2. Define core schema operations (tables, indexes)
3. Implement data access patterns matching the project's requirements

---

**Note**: This file will be updated as the project develops. Focus on maintainability and clear separation of concerns.
