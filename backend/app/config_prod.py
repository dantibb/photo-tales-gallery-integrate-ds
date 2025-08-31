import os
SECRET_KEY = os.environ.get('SECRET_KEY', 'prod')
SESSION_TYPE = 'filesystem'
UPLOAD_FOLDER = 'test_images'
USE_FIRESTORE = True 