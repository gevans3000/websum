# WebSum Test Suite

This directory contains the test suite for WebSum, organized to ensure code quality and maintainability.

## Directory Structure

- `unit/`: Unit tests for individual components
  - Tests for markdown processing
  - Tests for URL handling
  - Tests for file operations
  
- `integration/`: Integration tests for combined functionality
  - End-to-end crawling tests
  - Content extraction and storage tests
  - Error handling and recovery tests

- `fixtures/`: Test data and mock responses
  - Sample HTML content
  - Expected markdown outputs
  - Mock API responses

- `test_data/`: Generated test outputs
  - Crawl results
  - Processed markdown files
  - Log files and error reports

## Recent Improvements

### Error Handling and Logging (2025-02-09)
- Added structured JSON logging
- Implemented rotating log files
- Created custom exception hierarchy
- Enhanced error context and debugging
- Added performance tracking

### Test Organization
- Separated unit and integration tests
- Added fixtures for consistent testing
- Implemented test data cleanup
- Added detailed test documentation

## Running Tests

1. Basic test run:
   ```bash
   pytest
   ```

2. Run with logging:
   ```bash
   pytest --log-cli-level=DEBUG
   ```

3. Run specific test categories:
   ```bash
   pytest tests/unit  # Unit tests only
   pytest tests/integration  # Integration tests only
   ```

## Test Configuration

The test suite uses the following configuration:
- JSON logging for detailed debugging
- Separate test output directory
- Mock responses for external services
- Automatic cleanup of test data

## Adding New Tests

When adding new tests:
1. Choose appropriate directory (unit/integration)
2. Add necessary fixtures to `fixtures/`
3. Follow existing naming conventions
4. Include detailed docstrings
5. Update this README if needed

## Known Issues and TODOs

1. Configuration Issues:
   - [x] Fixed BrowserConfig parameters
   - [x] Corrected CrawlerConfig settings
   - [x] Added proper logging configuration

2. Error Handling:
   - [x] Implemented custom exceptions
   - [x] Added structured logging
   - [x] Enhanced error context
   - [ ] Add retry mechanisms for network errors

3. Test Coverage:
   - [x] Basic markdown processing
   - [x] File operations
   - [ ] Add more edge cases
   - [ ] Add performance benchmarks
