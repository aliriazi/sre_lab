# Testing Guide

This project includes comprehensive test cases for the Flask API backend.

## Setup

Install test dependencies:

```bash
pip install -r requirements-test.txt
```

## Running Tests

Run all tests:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=apps tests/
```

Run specific test file:

```bash
pytest tests/test_frontend.py
```

Run specific test:

```bash
pytest tests/test_frontend.py::TestFrontendAPI::test_post_single_entry
```

## Test Coverage

The test suite covers:

### API Endpoints
- **GET /entries** - Retrieve all project entries
- **POST /entries** - Create new project entries

### Test Cases

1. **Empty Database Tests**
   - `test_get_empty_entries` - Verify empty list on initial request

2. **Single Entry Tests**
   - `test_post_single_entry` - Add entry with title and description
   - `test_post_entry_without_description` - Add entry with only title

3. **Multiple Entries Tests**
   - `test_post_multiple_entries` - Test auto-incrementing IDs
   - `test_get_entries_after_adding` - Retrieve all added entries

4. **Data Validation Tests**
   - `test_special_characters_in_title` - Handle special chars and emojis
   - `test_long_entry_text` - Handle long strings (500+ chars)
   - `test_empty_title` - Handle empty title field
   - `test_whitespace_handling` - Preserve whitespace and newlines

5. **API Robustness Tests**
   - `test_missing_content_type` - Handle requests without explicit content-type
   - `test_entry_id_persistence` - Verify unique and sequential IDs

## Test Structure

Tests use `pytest` fixtures to create isolated test environments with temporary databases. Each test runs in isolation without affecting others.

### Fixture: `app_with_db`
- Creates a temporary database directory
- Initializes a Flask test client
- Cleans up resources after each test

## CI/CD Integration

To integrate tests in CI/CD pipeline:

```bash
pytest --cov=apps --cov-report=xml --cov-report=html
```

This generates coverage reports in XML and HTML formats for CI/CD systems.
