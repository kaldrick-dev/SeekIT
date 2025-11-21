# SeekIT

A comprehensive freelance marketplace platform that connects clients with freelancers. Built with Python and MySQL, SeekIT provides a complete CLI-based solution for managing freelance projects, job postings, applications, and workspaces.

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Database Setup](#database-setup)
- [Usage](#usage)
- [User Roles](#user-roles)
- [Development](#development)
- [Contributing](#contributing)

## Features

### For Freelancers
- **Profile Management**: Create and manage professional profiles with skills
- **Job Search**: Browse and search available job opportunities
- **Application Manager**: Track and manage job applications
- **Portfolio**: Showcase completed projects and client reviews
- **Workspace**: Submit deliverables and manage active projects

### For Clients
- **Job Posting**: Create and manage job listings
- **Freelancer Browser**: Search and filter freelancers by skills and ratings
- **Application Review**: Review and manage applicant submissions
- **Workspace**: Monitor project progress and review deliverables

### Core Features
- **Authentication**: Secure registration and login with bcrypt password hashing
- **User Management**: Role-based access control (Client/Freelancer)
- **Project Workspace**: Collaborative environment for managing active projects
- **Portfolio System**: Track completed projects with reviews and ratings
- **Application Tracking**: Complete job application lifecycle management

## Project Structure

```
SeekIT/
├── config/                 # Configuration files
│   ├── __init__.py
│   └── settings.py        # Database configuration
├── database/              # Database setup and management
│   ├── db_manager.py      # Database connection manager
│   ├── init_db.py         # Database initialization script
│   ├── schema.sql         # Database schema
│   └── seed_data.py       # Sample data seeding
├── features/              # Application features
│   ├── auth.py           # Authentication flows
│   ├── job_search.py     # Job search functionality
│   ├── job_posting.py    # Job posting management
│   ├── application_manager.py  # Application tracking
│   ├── freelancer_browser.py   # Freelancer search
│   ├── profile.py        # Profile management
│   ├── portfolio.py      # Portfolio management
│   └── workspace.py      # Project workspace
├── models/               # Data models
│   ├── user.py          # User model
│   ├── job.py           # Job model
│   ├── application.py   # Application model
│   ├── project.py       # Project model
│   └── portfolio.py     # Portfolio model
├── tests/               # Test files
│   ├── demo.py
│   ├── test_display.py
│   └── test_integration.py
├── utils/               # Utility modules
│   ├── display.py       # CLI display utilities
│   ├── helpers.py       # Helper functions
│   └── security.py      # Security utilities
├── main.py             # Application entry point
├── requirements.txt    # Python dependencies
└── .env               # Environment variables (create this)
```

## Prerequisites

- Python 3.8 or higher
- MySQL 5.7 or higher
- pip (Python package manager)

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd SeekIT
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. **Create a `.env` file** in the project root directory:
   ```env
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASS=your_password
   DB_NAME=SeekIT
   ```

2. **Update the configuration** based on your MySQL setup

## Database Setup

1. **Ensure MySQL is running** on your system

2. **Initialize the database**
   ```bash
   python database/init_db.py
   ```
   This will create the database and all necessary tables.

3. **(Optional) Seed with sample data**
   ```bash
   python database/seed_data.py
   ```
   This populates the database with sample users, jobs, and projects for testing.

## Usage

### Starting the Application

```bash
python main.py
```

### Main Menu Options

When you run the application, you'll see the following options:

```
1. Register new account     - Create a new user account
2. Log in to existing account - Access your account
3. List registered users    - View all users (requires login)
4. Log out                  - Sign out of current account
5. Search open jobs         - Browse available job listings
6. Application manager      - Manage job applications
7. Job posting tools        - Post and manage jobs (clients only)
8. View Profile            - View and edit your profile
9. View Portfolio          - View portfolio (freelancers only)
10. Workspace Manager       - Manage active projects
11. Browse freelancers      - Search for freelancers (clients only)
0. Exit                    - Quit the application
```

### Quick Start Guide

1. **Register an account**
   - Choose option 1 from the main menu
   - Select user type (client or freelancer)
   - Provide your details

2. **For Freelancers**
   - Search for jobs (option 5)
   - Apply to jobs via Application Manager (option 6)
   - Build your portfolio (option 9)
   - Manage projects in Workspace (option 10)

3. **For Clients**
   - Post jobs (option 7)
   - Browse freelancers (option 11)
   - Review applications (option 6)
   - Monitor projects (option 10)

## User Roles

### Freelancer
- Can search and apply for jobs
- Maintain a portfolio of completed work
- Submit deliverables for active projects
- Manage professional profile with skills

### Client
- Can post job opportunities
- Browse and filter freelancers
- Review job applications
- Monitor project progress and review deliverables

## Development

### Running Tests

```bash
# Run integration tests
python tests/test_integration.py

# Run display tests
python tests/test_display.py

# Run demo
python tests/demo.py
```

### Key Dependencies

- **mysql-connector-python**: MySQL database connectivity
- **python-dotenv**: Environment variable management
- **bcrypt**: Password hashing and security

### Database Schema

The application uses the following main tables:
- `users` - User accounts and authentication
- `skills` - Freelancer skills and expertise
- `jobs` - Job postings and descriptions
- `applications` - Job application submissions
- `projects` - Active client-freelancer projects
- `portfolio_items` - Freelancer portfolio entries
- `reviews` - Client reviews and ratings

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is part of an ALU academic project.

## Support

For issues, questions, or contributions, please open an issue in the repository.
