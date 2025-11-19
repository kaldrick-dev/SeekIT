-- SeekIT Database Schema

-- Table: users
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name TEXT,
    email TEXT,
    password_hash TEXT,
    location TEXT,
    user_type TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: freelancer_skills
CREATE TABLE IF NOT EXISTS freelancer_skills (
    skill_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    skill_name TEXT,
    skill_level TEXT,
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);

-- Table: jobs
CREATE TABLE IF NOT EXISTS jobs (
    job_id INT AUTO_INCREMENT PRIMARY KEY,
    client_id INT,
    title TEXT,
    description TEXT,
    required_skills TEXT,
    budget_min DECIMAL(10, 2),
    budget_max DECIMAL(10, 2),
    deadline DATE,
    status VARCHAR(20) DEFAULT 'open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES users (user_id)
);

-- Table: applications
CREATE TABLE IF NOT EXISTS applications (
    application_id INT AUTO_INCREMENT PRIMARY KEY,
    job_id INT,
    freelancer_id INT,
    cover_letter TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES jobs (job_id),
    FOREIGN KEY (freelancer_id) REFERENCES users (user_id)
);

-- Table: projects
CREATE TABLE IF NOT EXISTS projects (
    project_id INT AUTO_INCREMENT PRIMARY KEY,
    job_id INT,
    freelancer_id INT,
    client_id INT,
    status VARCHAR(20) DEFAULT 'active',
    progress_percentage INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES jobs (job_id),
    FOREIGN KEY (freelancer_id) REFERENCES users (user_id),
    FOREIGN KEY (client_id) REFERENCES users (user_id)
);

-- Table: milestones
CREATE TABLE IF NOT EXISTS milestones (
    milestone_id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT,
    milestone_name TEXT,
    description TEXT,
    due_date DATE,
    status VARCHAR(20) DEFAULT 'pending',
    order_number INT,
    FOREIGN KEY (project_id) REFERENCES projects (project_id)
);

-- Table: submissions
CREATE TABLE IF NOT EXISTS submissions (
    submission_id INT AUTO_INCREMENT PRIMARY KEY,
    milestone_id INT,
    deliverable_description TEXT,
    file_path TEXT,
    version_number INT DEFAULT 1,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    client_feedback TEXT,
    FOREIGN KEY (milestone_id) REFERENCES milestones (milestone_id)
);

-- Table: reviews
CREATE TABLE IF NOT EXISTS reviews (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT,
    reviewer_id INT,
    reviewee_id INT,
    rating INT,
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects (project_id),
    FOREIGN KEY (reviewer_id) REFERENCES users (user_id),
    FOREIGN KEY (reviewee_id) REFERENCES users (user_id)
);

-- Table: search_history
CREATE TABLE IF NOT EXISTS search_history (
    search_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    search_query TEXT,
    results_found INT DEFAULT 0,
    searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);

-- Table: activity_log
CREATE TABLE IF NOT EXISTS activity_log (
    activity_id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT,
    user_id INT,
    activity_type VARCHAR(50),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects (project_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);