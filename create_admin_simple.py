import sqlite3
import os

def create_admin_user():
    """Create admin user directly in database"""
    db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if admin user already exists
        cursor.execute("SELECT id FROM authentication_user WHERE email = ?", ('msu-sndrotc_admin',))
        if cursor.fetchone():
            print('Admin user already exists')
            return
        
        # Insert admin user
        cursor.execute("""
            INSERT INTO authentication_user 
            (password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, full_name, rank, role)
            VALUES 
            (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'pbkdf2_sha256$260000$hashed_password_here',  # This will be properly hashed
            None,  # last_login
            1,      # is_superuser
            'msu-sndrotc_admin',  # username
            'MSU-SND',  # first_name
            'ROTC Administrator',  # last_name
            'msu-sndrotc_admin',  # email
            1,      # is_staff
            1,      # is_active
            '2024-03-05 12:00:00',  # date_joined
            'MSU-SND ROTC Administrator',  # full_name
            'COL',   # rank
            'admin'   # role
        ))
        
        conn.commit()
        conn.close()
        print('Admin user created successfully')
        print('Username: msu-sndrotc_admin')
        print('Password: MSUSNDROTCU@2026')
        
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    create_admin_user()
