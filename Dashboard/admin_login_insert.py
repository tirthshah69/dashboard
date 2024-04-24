import pymysql
import time
import bcrypt
import getpass


def database_connection():
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        db='project',
        charset='utf8',
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection


def encrypt_password(password):
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')


def insert_admin_data(login_username, login_password):
    try:
        connection = database_connection()
        with connection.cursor() as cursor:
            hashed_login_password = encrypt_password(login_password)
            login_role = 'admin'
            is_deleted = False
            created_on = int(time.time())
            modified_on = int(time.time())

            # Execute SQL query to insert data
            sql_query = ("INSERT INTO login_table (login_username, "
                     "login_password, login_role, is_deleted, created_on, modified_on) VALUES (%s, %s, %s, %s, %s, %s)")
            cursor.execute(sql_query, (
            login_username, hashed_login_password, login_role, is_deleted, created_on,
            modified_on))

            # Commit the transaction
            connection.commit()
            connection.close()
    except Exception:
        print("Error while inserting. Try Again.")



def insert_user_data():
    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")
    confirm_password = getpass.getpass("Confirm password: ")
    if password == confirm_password:
        insert_admin_data(username, password)
        print("Admin login data added successfully.")
    else:
        print("Error: Passwords do not match. Please try again.")


if __name__ == '__main__':
    insert_user_data()