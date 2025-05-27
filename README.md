# Job Portal System

A simple Flask-based job portal web application where job seekers can browse and apply for jobs, and employers can post jobs.

## Features

- User authentication with role-based access (`employer` and `seeker`)
- Employers can post job listings
- Job seekers can browse jobs and apply by submitting a cover letter and resume
- Resume uploads with secure file handling
- Flash messages for user feedback (login, logout, application status)
- Responsive UI with Bootstrap 5
- PostgreSQL database integration using SQLAlchemy ORM
- Environment configuration via `.env` for secret keys and database URI

## Installation

1. Clone the repository:

```bash
git clone https://github.com/damini321/job_portal
cd job_portal
```

2. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a .env file in the project root and add the following variables:
   ```
   SECRET_KEY=your-secret-key
   DATABASE_URL=postgresql://username:password@localhost:5432/dbname
   ```

5. Run the application:
   
   ```bash
   flask run
   ```

### Usage
- Register as a job seeker or employer

- Employers can post jobs

- Job seekers can browse and apply for jobs

- View uploaded resumes from the job applications

### License
This project is licensed under the MIT License.
