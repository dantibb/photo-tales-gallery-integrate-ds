from flask import Flask

def create_app(config_name='local', template_folder='templates'):
    app = Flask(__name__, template_folder=template_folder)
    if config_name == 'prod':
        app.config.from_object('app.config_prod')
    else:
        app.config.from_object('app.config_local')
    return app