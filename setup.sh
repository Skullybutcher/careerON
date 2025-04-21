#!/bin/bash

# Check if python3.8 is available
if ! command -v python3.8 &> /dev/null
then
    echo "python3.8 could not be found. Please install Python 3.8.10 before running this script."
    exit 1
fi

# Create virtual environment named .venv
python3.8 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install packages from requirements.txt
pip install -r requirements.txt

# Check if psql (PostgreSQL client) is available
if ! command -v psql &> /dev/null
then
    echo "psql could not be found. Please install PostgreSQL client before running this script."
    exit 1
fi

# Create PostgreSQL user and database
echo "Setting up PostgreSQL database and user..."

# Create user if not exists
psql -U postgres -tc "SELECT 1 FROM pg_roles WHERE rolname='ayush'" | grep -q 1 || psql -U postgres -c "CREATE USER ayush WITH PASSWORD 'ayush';"

# Create database if not exists
psql -U postgres -tc "SELECT 1 FROM pg_database WHERE datname='career_navigator'" | grep -q 1 || psql -U postgres -c "CREATE DATABASE career_navigator OWNER ayush;"

echo "Setup complete. Virtual environment '.venv' created, packages installed, and PostgreSQL database setup done."
