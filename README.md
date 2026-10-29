
# CareerPilot API

A job application tracking REST API built with Python, FastAPI, and SQLite.

## Features

- Create job applications
- Retrieve all applications
- Update application details and status
- Delete applications
- Validate request data using Pydantic
- Store application records in SQLite

## Tech Stack

- Python
- FastAPI
- SQLite
- Pydantic
- Uvicorn

## Run Locally

1. Clone this repository.
2. Create and activate a Python virtual environment.
3. Install the dependencies:

   ```bash
   python -m pip install "fastapi[standard]"
   ```

4. Start the API:

   ```bash
   python -m uvicorn main:app --reload
   ```

5. Open the interactive API documentation:

   http://127.0.0.1:8000/docs

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/applications` | List applications |
| POST | `/applications` | Create an application |
| PUT | `/applications/{application_id}` | Update an application |
| DELETE | `/applications/{application_id}` | Delete an application |

## Database

SQLite stores application records in `careerpilot.db`. The database is created locally when the application starts.

## Project Status

Core CRUD functionality implemented and tested locally.
