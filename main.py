
import sqlite3

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from typing import Literal

DATABASE = "careerpilot.db"

app = FastAPI(title="CareerPilot API")


# Connect to the SQLite database
def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


# Create the database table if it doesn't exist
def create_table():
    connection = get_connection()

    try:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL,
                role TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Applied'
            )
        """)
        connection.commit()
    finally:
        connection.close()


create_table()


# Validate incoming application data
class JobApplication(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    company: str = Field(min_length=1, max_length=100)
    role: str = Field(min_length=1, max_length=100)
    status: Literal[
        "Applied",
        "Interview",
        "Selected",
        "Rejected",
        "Withdrawn"
    ] = "Applied"


# READ: Get all applications
@app.get("/applications")
def get_applications():
    connection = get_connection()

    try:
        rows = connection.execute(
            "SELECT * FROM applications ORDER BY id"
        ).fetchall()

        return [dict(row) for row in rows]
    finally:
        connection.close()


# CREATE: Add a new application
@app.post("/applications", status_code=status.HTTP_201_CREATED)
def create_application(application: JobApplication):
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO applications (company, role, status)
            VALUES (?, ?, ?)
            """,
            (application.company, application.role, application.status)
        )

        connection.commit()

        new_id = cursor.lastrowid

        row = connection.execute(
            "SELECT * FROM applications WHERE id = ?",
            (new_id,)
        ).fetchone()

        return {
            "message": "Application created successfully",
            "application": dict(row)
        }
    finally:
        connection.close()


# UPDATE: Change an existing application
@app.put("/applications/{application_id}")
def update_application(
    application_id: int,
    application: JobApplication
):
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            UPDATE applications
            SET company = ?, role = ?, status = ?
            WHERE id = ?
            """,
            (
                application.company,
                application.role,
                application.status,
                application_id
            )
        )

        connection.commit()

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Application not found"
            )

        row = connection.execute(
            "SELECT * FROM applications WHERE id = ?",
            (application_id,)
        ).fetchone()

        return {
            "message": "Application updated successfully",
            "application": dict(row)
        }
    finally:
        connection.close()


# DELETE: Remove an application
@app.delete("/applications/{application_id}")
def delete_application(application_id: int):
    connection = get_connection()

    try:
        cursor = connection.execute(
            "DELETE FROM applications WHERE id = ?",
            (application_id,)
        )

        connection.commit()

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Application not found"
            )

        return {
            "message": "Application deleted successfully",
            "id": application_id
        }
    finally:
        connection.close()
