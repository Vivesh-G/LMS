# LMS
Learning Management System built for DBMS Project

<img width="1919" height="881" alt="Screenshot 2025-04-08 223725" src="https://github.com/user-attachments/assets/54d0af56-c84a-4146-8508-c49736bea8a8" />

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/Vivesh-G/LMS
    cd LMS
    ```

2.  **Create a virtual environment:**

    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
    ```

3.  **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Import the database:**

    *   Make sure your MySQL server is running.
    *   Create a new database (e.g., `snulms`).
    *   Import the `snulms-dump.sql` file into your new database:

    ```bash
    mysql -u your_mysql_username -p your_database_name < snulms-dump.sql
    ```

### Running the Application

Once you have completed the installation steps, you can run the application with the following command:

```bash
uvicorn fastapp:app --reload
```

The application will be available at `http://127.0.0.1:8000`.
