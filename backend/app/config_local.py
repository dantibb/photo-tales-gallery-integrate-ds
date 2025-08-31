SECRET_KEY = 'dev'
SESSION_TYPE = 'filesystem'
USE_FIRESTORE = False 

import os
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'test_images')