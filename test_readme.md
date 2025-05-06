# FASTransit Point Management System - Testing Guide

This document provides instructions on how to run the test cases for the FASTransit Point Management System.

## Test Suite Overview

The test suite includes unit tests and integration tests for various modules of the system:

1. **User Authentication Tests** - Tests for user registration, login, and validation
2. **Transportation Management Tests** - Tests for route and vehicle management
3. **Payment Processing Tests** - Tests for voucher generation and payment processing
4. **Noticeboard Tests** - Tests for notice creation and feedback submission
5. **Driver Management Tests** - Tests for driver registration and vehicle assignment

## Prerequisites

- Python 3.6+
- Django 5.1.2
- MySQL Database

## Setting Up the Test Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/FASTProjectSDA22K-4212.git
   cd FASTProjectSDA22K-4212/code/FASTransit
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up a test database in MySQL and run migrations.

5. Configure test settings:
   Create a `.env.test` file in the project root with the following content:
   ```
   SECRET_KEY=your-test-secret-key
   DEBUG=True
   DATABASE_URL=mysql://root:@localhost/fastransit_test
   RECAPTCHA_PRIVATE_KEY=your-test-recaptcha-key
   STRIPE_PUBLIC_KEY=your-test-stripe-public-key
   STRIPE_PRIVATE_KEY=your-test-stripe-private-key
   STRIPE_WEBHOOK=your-test-stripe-webhook-key
   ```

## Running the Tests

### Running All Tests

To run all tests at once:

```bash
python manage.py test
```

### Running Tests for Specific Apps

To run tests for a specific app:

```bash
python manage.py test userauth
python manage.py test transport
python manage.py test payment
python manage.py test noticeboard
python manage.py test driver
```

### Running Specific Test Cases

To run a specific test case:

```bash
python manage.py test userauth.tests.UserAuthTest.test_user_registration_valid
```

### Test Coverage Report

To generate a test coverage report:

1. Install coverage:
   ```bash
   pip install coverage
   ```

2. Run the tests with coverage:
   ```bash
   coverage run --source='.' manage.py test
   ```

3. Generate the coverage report:
   ```bash
   coverage report
   ```

4. For a detailed HTML report:
   ```bash
   coverage html
   ```
   Then open `htmlcov/index.html` in your browser.

## Troubleshooting

### Database Issues

If you encounter database issues when running tests:

1. Make sure the MySQL service is running
2. Verify that the database credentials in the `.env.test` file are correct
3. Try resetting the test database:
   ```bash
   python manage.py flush --database=default
   ```

### Missing Dependencies

If you get errors about missing dependencies:

```bash
pip install -r requirements.txt
```

### Test Fails Due to Environment Variables

If tests fail due to missing environment variables:

1. Make sure the `.env.test` file exists in the project root
2. Verify that all required variables are set
3. Try loading the environment variables manually before running tests:
   ```bash
   export $(cat .env.test | xargs)
   ```

## Additional Resources

- [Django Testing Documentation](https://docs.djangoproject.com/en/5.1/topics/testing/)
- [Test Case Document](test_case_document.md)
- [Test Log Report](test_log_report.md)

## Contact

For any questions or issues regarding the testing process, please contact the development team at fastransit@example.com. 