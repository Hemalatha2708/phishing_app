"""
Database Schema Creation Script
Creates the phishing detection app database and tables
"""

import mysql.connector
from mysql.connector import Error

# Database connection configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'hemalatha2000'
}

# Database name
DATABASE_NAME = 'phishing'


def create_database():
    """Create the database if it doesn't exist"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Create database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME}")
        print(f"✅ Database '{DATABASE_NAME}' created or already exists")
        
        cursor.close()
        conn.close()
        
    except Error as e:
        print(f"❌ Error creating database: {e}")
        return False
    
    return True


def create_tables():
    """Create tables in the phishing database"""
    try:
        # Connect to the specific database
        DB_CONFIG['database'] = DATABASE_NAME
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # ========================
        # CREATE PROFILES TABLE
        # ========================
        create_profiles_table = """
        CREATE TABLE IF NOT EXISTS profiles (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(15) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        cursor.execute(create_profiles_table)
        print("✅ 'profiles' table created successfully")
        
        # ========================
        # CREATE HISTORY TABLE
        # ========================
        create_history_table = """
        CREATE TABLE IF NOT EXISTS history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            url VARCHAR(2048) NOT NULL,
            score FLOAT NOT NULL,
            status VARCHAR(20) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES profiles(id) ON DELETE CASCADE,
            INDEX idx_user_id (user_id),
            INDEX idx_created_at (created_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        cursor.execute(create_history_table)
        print("✅ 'history' table created successfully")
        
        conn.commit()
        cursor.close()
        conn.close()
        
    except Error as e:
        print(f"❌ Error creating tables: {e}")
        return False
    
    return True


def verify_schema():
    """Verify the schema was created correctly"""
    try:
        DB_CONFIG['database'] = DATABASE_NAME
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        print("\n📊 Database Schema Summary:")
        print(f"Tables created: {len(tables)}")
        
        for table in tables:
            print(f"  - {table[0]}")
            cursor.execute(f"DESCRIBE {table[0]}")
            columns = cursor.fetchall()
            for col in columns:
                print(f"    • {col[0]}: {col[1]}")
        
        cursor.close()
        conn.close()
        
    except Error as e:
        print(f"❌ Error verifying schema: {e}")
        return False
    
    return True


def main():
    """Main function to initialize the database"""
    print("🚀 Starting Database Schema Creation...\n")
    
    # Step 1: Create database
    print("Step 1: Creating database...")
    if not create_database():
        print("Failed to create database. Exiting...")
        return
    
    print()
    
    # Step 2: Create tables
    print("Step 2: Creating tables...")
    if not create_tables():
        print("Failed to create tables. Exiting...")
        return
    
    print()
    
    # Step 3: Verify schema
    print("Step 3: Verifying schema...")
    if verify_schema():
        print("\n✨ Database initialization completed successfully!")
    else:
        print("\n⚠️ Schema verification encountered issues")


if __name__ == "__main__":
    main()
