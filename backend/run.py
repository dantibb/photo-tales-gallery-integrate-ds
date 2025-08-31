from app import create_app
from flask_session import Session
import os

app = create_app('prod')
Session(app)

# Import and register production routes
import app.routes

# Print all registered routes for debugging
print("Registered routes:")
for rule in app.url_map.iter_rules():
    print(rule)

if __name__ == '__main__':
    app.run() 