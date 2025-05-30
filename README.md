# Job Portal System

A simple Flask-based job portal web application where job seekers can browse and apply for jobs, and employers can post jobs.

---

## Features

- User authentication with role-based access (`employer` and `seeker`)
- Employers can post job listings and mark jobs as closed
- Job seekers can browse jobs, search by title/skills/company, and apply by submitting a cover letter and resume
- Resume uploads with secure file handling and profile picture upload
- Flash messages for user feedback (login, logout, application status)
- Responsive UI built with CSS.
- PostgreSQL database integration using SQLAlchemy ORM
- SMTP email confirmation for user registration
- Pagination on job listings for better usability
- User profile page for both seekers and employers
- Employer dashboard to manage job posts and view applicants
- Environment configuration via `.env` for secret keys, database URI, and email credentials


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

   SECRET_KEY=your-secret-key
   DATABASE_URL=postgresql://username:password@localhost:5432/dbname
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=youremail@example.com
   MAIL_PASSWORD=yourpassword

   ```

5. Run the application:
   
   ```bash
   flask run
   ```


### Usage
- Register as a job seeker or employer

- Employers can post jobs, edit, and mark jobs as closed.

- Job seekers can browse jobs, use search, and apply by submitting cover letter and resume.

- View and manage profiles.

- Employers can view applicants for their job posts.

### License
This project is licensed under the MIT License.

### Contact
For questions or suggestions, reach out to [daminikhule99@gmail.com].

