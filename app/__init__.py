from flask import Flask
import json

app = Flask(__name__)
app.config.from_file('../config.json', load=json.load)
app.config['SECRET_KEY'] = '1e1cba7a-32e8-4cad-9f1e-e4ca0de4ca1f'

from app.views.auth import auth
from app.views.dashboard import dashboard
from app.views.users import users
from app.views.settings import settings

app.register_blueprint(auth)
app.register_blueprint(dashboard)
app.register_blueprint(users)
app.register_blueprint(settings)


#user table structure
#  CREATE TABLE users (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     username VARCHAR(100) NOT NULL UNIQUE,
#     password VARCHAR(100) NOT NULL,
#     created_date VARCHAR(100) DEFAULT NULL,
#     modified_date VARCHAR(100) DEFAULT NULL
#  )

# {
#     "index": 2, motor_number
#     "operation_pin": 0, forward(1) or reverse(0) 
#     "relay": "None", relay number from 1 to 20
#     "feed_back": 0, forward(1) or reverse(0)
#     "pin": "None", pin number from 1 to 20
#     "buffer_time": 0, time out 
#     "position": 15, position in the list of 16 items
# }



