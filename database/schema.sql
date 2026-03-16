DROP TABLE IF EXISTS loan_decisions CASCADE;
DROP TABLE IF EXISTS income_records CASCADE;
DROP TABLE IF EXISTS loan_applications CASCADE;
DROP TABLE IF EXISTS users CASCADE;

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE loan_applications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    loan_amount DECIMAL(12, 2) NOT NULL,
    loan_purpose VARCHAR(100) NOT NULL,
    loan_term_months INTEGER NOT NULL,
    employment_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE income_records (
    id SERIAL PRIMARY KEY,
    application_id INTEGER NOT NULL REFERENCES loan_applications(id) ON DELETE CASCADE,
    month_year VARCHAR(7) NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    source VARCHAR(100)
);

CREATE TABLE loan_decisions (
    id SERIAL PRIMARY KEY,
    application_id INTEGER NOT NULL REFERENCES loan_applications(id) ON DELETE CASCADE,
    decision VARCHAR(20) NOT NULL,
    stability_score DECIMAL(5, 2),
    average_monthly_income DECIMAL(12, 2),
    income_variance DECIMAL(12, 2),
    debt_to_income_ratio DECIMAL(5, 2),
    reasoning TEXT,
    decided_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO users (full_name, email, password_hash) VALUES ('Test User', 'test@example.com', 'hashed_password_here');
INSERT INTO loan_applications (user_id, loan_amount, loan_purpose, loan_term_months, employment_type) VALUES (1, 15000.00, 'Home Renovation', 24, 'freelancer');
INSERT INTO income_records (application_id, month_year, amount, source) VALUES
(1, '2024-01', 3200.00, 'Freelance Design'),
(1, '2024-02', 1800.00, 'Freelance Design'),
(1, '2024-03', 4500.00, 'Freelance Design'),
(1, '2024-04', 2100.00, 'Freelance Design'),
(1, '2024-05', 3900.00, 'Freelance Design'),
(1, '2024-06', 2700.00, 'Freelance Design');
