# Finance Tracking System Backend

This project is a Python backend for a finance tracking system, built for a class assignment. It allows users to track their financial records, manage transactions (income and expenses), and view summaries.

## Tech Stack
- **Framework:** Python with Django and Django REST Framework
- **Database:** PostgreSQL (with Django's native ORM)
- **Authentication:** JWT (JSON Web Tokens)
- **Other Features:** Pagination, basic endpoint filtering

## Prerequisites
- Python 3.10+
- PostgreSQL 12+

## Setup Instructions

1. Clone this repository or download the source code
2. Navigate into the folder `PYTHON ASSIGNMNET`
3. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   # source venv/bin/activate
   ```
4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Configure your database credentials by creating a `.env` file in the root directory:
   ```
   DB_NAME=finance_db
   DB_USER=your_user
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=5432
   SECRET_KEY=some_random_secret_key_for_dev
   DEBUG=True
   ```
6. Run the database migrations:
   ```bash
   python manage.py migrate
   ```
7. Start the development server:
   ```bash
   python manage.py runserver
   ```

## Testing

To run the unit tests provided in the apps, you can use Django's testing framework:
```bash
python manage.py test
```

## Structure

- `/apps`: Contains all the Django apps (`users`, `transactions`, `analytics`, `audit`)
- `/config`: Core Django settings and URL configurations
- `/utils`: Helper functions and exception handlers

## Assignment Notes
The project attempts to create a clean separation of concerns and robust API responses, handling edge cases such as permission errors and input validation. The focus was kept simple to avoid overcomplicating the assignment boundaries while showcasing how a real backend looks like.
