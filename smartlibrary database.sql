-- SmartLibrary Database Setup Script (SQL ONLY)
-- Complete setup with proper bcrypt password hashing
-- Run this script in PostgreSQL to create everything

-- Drop existing database if exists (optional - use with caution!)
-- DROP DATABASE IF EXISTS smartlibrary_db;

-- Create database (run this first if database doesn't exist)
-- CREATE DATABASE smartlibrary_db;

-- Connect to the database
\c smartlibrary_db;

-- ============================================
-- ENABLE PGCRYPTO EXTENSION FOR PASSWORD HASHING
-- ============================================
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ============================================
-- DROP EXISTING TABLES (FOR CLEAN SETUP)
-- ============================================
DROP TABLE IF EXISTS book_club_members CASCADE;
DROP TABLE IF EXISTS loans CASCADE;
DROP TABLE IF EXISTS book_clubs CASCADE;
DROP TABLE IF EXISTS books CASCADE;
DROP TABLE IF EXISTS authors CASCADE;
DROP TABLE IF EXISTS members CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS roles CASCADE;

-- ============================================
-- TABLE CREATION
-- ============================================

-- Roles table
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash BYTEA NOT NULL,
    role_id INTEGER REFERENCES roles(id) ON DELETE SET NULL,
    name VARCHAR(200) NOT NULL,
    email VARCHAR(200) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Members table (extends Users)
CREATE TABLE members (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    student_id VARCHAR(50) UNIQUE NOT NULL,
    contact VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Authors table
CREATE TABLE authors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    bio TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Books table
CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(300) NOT NULL,
    isbn VARCHAR(20) UNIQUE NOT NULL,
    genre VARCHAR(100),
    available BOOLEAN DEFAULT TRUE,
    author_id INTEGER REFERENCES authors(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Loans table
CREATE TABLE loans (
    id SERIAL PRIMARY KEY,
    book_id INTEGER REFERENCES books(id) ON DELETE CASCADE,
    member_id INTEGER REFERENCES members(id) ON DELETE CASCADE,
    borrow_date DATE DEFAULT CURRENT_DATE,
    due_date DATE DEFAULT (CURRENT_DATE + INTERVAL '7 days'),
    return_date DATE,
    status VARCHAR(20) DEFAULT 'Active' CHECK (status IN ('Active', 'Returned', 'Overdue')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Book Clubs table
CREATE TABLE book_clubs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Book Club Members junction table
CREATE TABLE book_club_members (
    id SERIAL PRIMARY KEY,
    club_id INTEGER REFERENCES book_clubs(id) ON DELETE CASCADE,
    member_id INTEGER REFERENCES members(id) ON DELETE CASCADE,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(club_id, member_id)
);

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role_id);
CREATE INDEX idx_members_user_id ON members(user_id);
CREATE INDEX idx_members_student_id ON members(student_id);
CREATE INDEX idx_books_title ON books(title);
CREATE INDEX idx_books_isbn ON books(isbn);
CREATE INDEX idx_books_author ON books(author_id);
CREATE INDEX idx_loans_member ON loans(member_id);
CREATE INDEX idx_loans_book ON loans(book_id);
CREATE INDEX idx_loans_status ON loans(status);
CREATE INDEX idx_book_club_members_club ON book_club_members(club_id);
CREATE INDEX idx_book_club_members_member ON book_club_members(member_id);

-- ============================================
-- TRIGGERS AND FUNCTIONS
-- ============================================

-- Function to check max loans per member (3 loans)
CREATE OR REPLACE FUNCTION check_max_loans()
RETURNS TRIGGER AS $$
BEGIN
    IF (SELECT COUNT(*) FROM loans
        WHERE member_id = NEW.member_id AND status = 'Active') >= 3 THEN
        RAISE EXCEPTION 'Member has reached maximum loan limit (3 books)';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to enforce max loans
CREATE TRIGGER trigger_check_max_loans
    BEFORE INSERT ON loans
    FOR EACH ROW
    EXECUTE FUNCTION check_max_loans();

-- Function to automatically mark overdue loans
CREATE OR REPLACE FUNCTION update_overdue_loans()
RETURNS void AS $$
BEGIN
    UPDATE loans
    SET status = 'Overdue'
    WHERE status = 'Active' AND due_date < CURRENT_DATE;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- INSERT SAMPLE DATA
-- ============================================

-- Insert roles
INSERT INTO roles (name) VALUES
    ('Librarian'),
    ('Member');

-- Insert users with PROPERLY HASHED PASSWORDS using crypt()
-- Password for all accounts: 'password123'
-- Using crypt() with bf (blowfish/bcrypt) algorithm
CREATE EXTENSION IF NOT EXISTS pgcrypto;

INSERT INTO users (username, password_hash, role_id, name, email) VALUES
    ('admin', crypt('password123', gen_salt('bf'))::bytea,
     (SELECT id FROM roles WHERE name = 'Librarian'), 'Admin Librarian', 'admin@limkokwing.edu'),
    ('librarian1', crypt('password123', gen_salt('bf'))::bytea,
     (SELECT id FROM roles WHERE name = 'Librarian'), 'Sarah Johnson', 'sarah.j@limkokwing.edu'),
    ('john_doe', crypt('password123', gen_salt('bf'))::bytea,
     (SELECT id FROM roles WHERE name = 'Member'), 'John Doe', 'john.doe@student.limkokwing.edu'),
    ('jane_smith', crypt('password123', gen_salt('bf'))::bytea,
     (SELECT id FROM roles WHERE name = 'Member'), 'Jane Smith', 'jane.smith@student.limkokwing.edu'),
    ('mike_brown', crypt('password123', gen_salt('bf'))::bytea,
     (SELECT id FROM roles WHERE name = 'Member'), 'Mike Brown', 'mike.brown@student.limkokwing.edu'),
    ('emma_wilson', crypt('password123', gen_salt('bf'))::bytea,
     (SELECT id FROM roles WHERE name = 'Member'), 'Emma Wilson', 'emma.wilson@student.limkokwing.edu'),
    ('david_lee', crypt('password123', gen_salt('bf'))::bytea,
     (SELECT id FROM roles WHERE name = 'Member'), 'David Lee', 'david.lee@student.limkokwing.edu');

-- Insert members
INSERT INTO members (user_id, student_id, contact) VALUES
    ((SELECT id FROM users WHERE username = 'john_doe'), 'LKW2023001', '+60123456789'),
    ((SELECT id FROM users WHERE username = 'jane_smith'), 'LKW2023002', '+60123456790'),
    ((SELECT id FROM users WHERE username = 'mike_brown'), 'LKW2023003', '+60123456791'),
    ((SELECT id FROM users WHERE username = 'emma_wilson'), 'LKW2023004', '+60123456792'),
    ((SELECT id FROM users WHERE username = 'david_lee'), 'LKW2023005', '+60123456793');

-- Insert authors
INSERT INTO authors (name, bio) VALUES
    ('J.K. Rowling', 'British author, best known for the Harry Potter series'),
    ('George R.R. Martin', 'American novelist and short story writer, author of A Song of Ice and Fire'),
    ('Stephen King', 'American author of horror, supernatural fiction, suspense, and fantasy novels'),
    ('Agatha Christie', 'English writer known for her detective novels'),
    ('Isaac Asimov', 'American writer and professor of biochemistry, prolific science fiction author'),
    ('Jane Austen', 'English novelist known for her romantic fiction'),
    ('Mark Twain', 'American writer, humorist, and lecturer'),
    ('Ernest Hemingway', 'American novelist, short-story writer, and journalist'),
    ('Harper Lee', 'American novelist best known for To Kill a Mockingbird'),
    ('F. Scott Fitzgerald', 'American novelist and short story writer');

-- Insert books
INSERT INTO books (title, isbn, genre, available, author_id) VALUES
    ('Harry Potter and the Philosopher''s Stone', '9780747532699', 'Fantasy', TRUE,
     (SELECT id FROM authors WHERE name = 'J.K. Rowling')),
    ('Harry Potter and the Chamber of Secrets', '9780747538493', 'Fantasy', TRUE,
     (SELECT id FROM authors WHERE name = 'J.K. Rowling')),
    ('A Game of Thrones', '9780553103540', 'Fantasy', TRUE,
     (SELECT id FROM authors WHERE name = 'George R.R. Martin')),
    ('The Shining', '9780385121675', 'Horror', TRUE,
     (SELECT id FROM authors WHERE name = 'Stephen King')),
    ('It', '9780670813025', 'Horror', FALSE,
     (SELECT id FROM authors WHERE name = 'Stephen King')),
    ('Murder on the Orient Express', '9780062693662', 'Mystery', TRUE,
     (SELECT id FROM authors WHERE name = 'Agatha Christie')),
    ('And Then There Were None', '9780062073488', 'Mystery', TRUE,
     (SELECT id FROM authors WHERE name = 'Agatha Christie')),
    ('Foundation', '9780553293357', 'Science Fiction', TRUE,
     (SELECT id FROM authors WHERE name = 'Isaac Asimov')),
    ('I, Robot', '9780553382563', 'Science Fiction', TRUE,
     (SELECT id FROM authors WHERE name = 'Isaac Asimov')),
    ('Pride and Prejudice', '9780141439518', 'Classic', TRUE,
     (SELECT id FROM authors WHERE name = 'Jane Austen')),
    ('Emma', '9780141439587', 'Classic', TRUE,
     (SELECT id FROM authors WHERE name = 'Jane Austen')),
    ('The Adventures of Tom Sawyer', '9780143107330', 'Classic', TRUE,
     (SELECT id FROM authors WHERE name = 'Mark Twain')),
    ('The Old Man and the Sea', '9780684801223', 'Classic', TRUE,
     (SELECT id FROM authors WHERE name = 'Ernest Hemingway')),
    ('To Kill a Mockingbird', '9780061120084', 'Classic', TRUE,
     (SELECT id FROM authors WHERE name = 'Harper Lee')),
    ('The Great Gatsby', '9780743273565', 'Classic', TRUE,
     (SELECT id FROM authors WHERE name = 'F. Scott Fitzgerald'));

-- Insert active loans (some overdue for testing)
INSERT INTO loans (book_id, member_id, borrow_date, due_date, status) VALUES
    ((SELECT id FROM books WHERE title = 'It'),
     (SELECT id FROM members WHERE student_id = 'LKW2023001'),
     CURRENT_DATE - INTERVAL '10 days', CURRENT_DATE - INTERVAL '3 days', 'Overdue'),
    ((SELECT id FROM books WHERE title = 'Harry Potter and the Philosopher''s Stone'),
     (SELECT id FROM members WHERE student_id = 'LKW2023002'),
     CURRENT_DATE - INTERVAL '3 days', CURRENT_DATE + INTERVAL '4 days', 'Active'),
    ((SELECT id FROM books WHERE title = 'The Great Gatsby'),
     (SELECT id FROM members WHERE student_id = 'LKW2023003'),
     CURRENT_DATE - INTERVAL '1 day', CURRENT_DATE + INTERVAL '6 days', 'Active');

-- Update book availability based on active loans
UPDATE books SET available = FALSE
WHERE id IN (SELECT book_id FROM loans WHERE status IN ('Active', 'Overdue'));

-- Insert returned loans (for history)
INSERT INTO loans (book_id, member_id, borrow_date, due_date, return_date, status) VALUES
    ((SELECT id FROM books WHERE title = 'Foundation'),
     (SELECT id FROM members WHERE student_id = 'LKW2023001'),
     CURRENT_DATE - INTERVAL '20 days', CURRENT_DATE - INTERVAL '13 days',
     CURRENT_DATE - INTERVAL '12 days', 'Returned'),
    ((SELECT id FROM books WHERE title = 'Pride and Prejudice'),
     (SELECT id FROM members WHERE student_id = 'LKW2023002'),
     CURRENT_DATE - INTERVAL '15 days', CURRENT_DATE - INTERVAL '8 days',
     CURRENT_DATE - INTERVAL '7 days', 'Returned');

-- Insert book clubs
INSERT INTO book_clubs (name, description, created_by) VALUES
    ('Fantasy Readers Club', 'A club for lovers of fantasy literature',
     (SELECT id FROM users WHERE username = 'admin')),
    ('Mystery & Thriller Society', 'Discussing the latest mystery novels',
     (SELECT id FROM users WHERE username = 'librarian1')),
    ('Classic Literature Circle', 'Exploring timeless literary works',
     (SELECT id FROM users WHERE username = 'admin')),
    ('Sci-Fi Enthusiasts', 'Science fiction discussions and recommendations',
     (SELECT id FROM users WHERE username = 'librarian1'));

-- Add members to book clubs
INSERT INTO book_club_members (club_id, member_id) VALUES
    ((SELECT id FROM book_clubs WHERE name = 'Fantasy Readers Club'),
     (SELECT id FROM members WHERE student_id = 'LKW2023001')),
    ((SELECT id FROM book_clubs WHERE name = 'Fantasy Readers Club'),
     (SELECT id FROM members WHERE student_id = 'LKW2023002')),
    ((SELECT id FROM book_clubs WHERE name = 'Mystery & Thriller Society'),
     (SELECT id FROM members WHERE student_id = 'LKW2023002')),
    ((SELECT id FROM book_clubs WHERE name = 'Mystery & Thriller Society'),
     (SELECT id FROM members WHERE student_id = 'LKW2023003')),
    ((SELECT id FROM book_clubs WHERE name = 'Classic Literature Circle'),
     (SELECT id FROM members WHERE student_id = 'LKW2023004')),
    ((SELECT id FROM book_clubs WHERE name = 'Sci-Fi Enthusiasts'),
     (SELECT id FROM members WHERE student_id = 'LKW2023005'));

-- ============================================
-- VERIFICATION QUERIES
-- ============================================

SELECT '============================================' as message;
SELECT 'DATABASE SETUP COMPLETED SUCCESSFULLY!' as message;
SELECT '============================================' as message;

SELECT 'Total Users:' as info, COUNT(*) as count FROM users;
SELECT 'Total Members:' as info, COUNT(*) as count FROM members;
SELECT 'Total Authors:' as info, COUNT(*) as count FROM authors;
SELECT 'Total Books:' as info, COUNT(*) as count FROM books;
SELECT 'Total Loans:' as info, COUNT(*) as count FROM loans;
SELECT 'Total Book Clubs:' as info, COUNT(*) as count FROM book_clubs;

SELECT '============================================' as message;
SELECT 'LOGIN CREDENTIALS (All passwords: password123)' as message;
SELECT '============================================' as message;
