import firebase_admin
from firebase_admin import credentials, auth
import os
from dotenv import load_dotenv
#use this if you want to delete your firebase auth
load_dotenv()
# Initialize the app with your service account key file
key_path = os.getenv("FIREBASE_GOOGLE_CREDENTIALS")
cred = credentials.Certificate(key_path)
firebase_admin.initialize_app(cred, {
    "projectId": os.getenv("FIREBASE_PROJECT_ID")
})
# Function to list all users (up to 1000 at a time)
def list_all_users():
    page = auth.list_users()
    while page:
        for user in page.users:
            print(f'User: {user.uid}, Email: {user.email}')
            delete_user_by_email(user.email)
        page = page.get_next_page()

# Function to delete user by email
def delete_user_by_email(email):
    try:
        user = auth.get_user_by_email(email)
        auth.delete_user(user.uid)
        print(f'Successfully deleted user: {email}')
    except auth.UserNotFoundError:
        print(f'User with email {email} not found.')
    except Exception as e:
        print(f'Error deleting user: {e}')
print("HELLO")
if __name__ == '__main__':
    # Example usage:
    
    print("Listing users:")
    list_all_users()

    # Uncomment to delete a user by email:
    