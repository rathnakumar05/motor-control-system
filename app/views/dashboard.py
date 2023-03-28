from flask import render_template, request, Blueprint, session, redirect, url_for
import json
import time
import threading 

from app import app

dashboard = Blueprint("dashboard", __name__)

@dashboard.before_request
def dashboard_middleware():
    if not session.get("auth")=="Y":
        return redirect(url_for("auth.user_login"))

@dashboard.route("/")
def index():
    settings = None
    input = None
    output = None
    motors = None
    current_sequence = None
    current_motor = None
    with open(app.config["SETTINGS_PATH"]) as f:
        content = f.read()
        if content:
            settings = json.loads(content)
    with open(app.config["INPUT_PATH"]) as f:
        content = f.read()
        if content:
            input = json.loads(content)
    with open(app.config["OUTPUT_PATH"]) as f:
        content = f.read()
        if content:
            output = json.loads(content)
    if settings and output:
        motors = {}
        for i in range(1, 9):
            motors[str(i)] = {
                "forward" : settings[str(i)],
                "reverse" : settings[str(17-i)],
                "enable" : 0
            }
            motors[str(i)]["forward"]["output"] = output["S"+str(settings[str(i)]["relay"])]
            motors[str(i)]["reverse"]["output"] = output["S"+str(settings[str(i+8)]["relay"])]

        if input and output:
            if input["waiting"]==1:
                motors[str(input["index"])]["enable"] = 1
            else:
                if input["operation_pin"]==1:
                    if input["index"]!=8:
                        motors[str(input["index"]+1)]["enable"] = 1
                        current_sequence = "OPEN"
                        current_motor = str(input["index"]+1)
                    else:
                        motors[str(input["index"])]["enable"] = 1
                        current_sequence = "CLOSE"
                        current_motor = str(input["index"])
                else:
                    if input["index"]!=1:
                        motors[str(input["index"]-1)]["enable"] = 1
                        current_sequence = "CLOSE"
                        current_motor = str(input["index"]-1)
                    else:
                        motors[str(input["index"])]["enable"] = 1
                        current_sequence = "OPEN"
                        current_motor = str(input["index"])

        else:
            motors["1"]["enable"] = 1
            current_sequence = "OPEN"
            current_motor = str(input["index"])
    return render_template("index.html", motors=motors, current_sequence=current_sequence, current_motor=current_motor)

def sim(input):
    output = None
    with open(app.config["OUTPUT_PATH"]) as f:
        content = f.read()
        if content:
            output = json.loads(content)
    start_time = time.time()
    while time.time() - start_time < input["buffer_time"]:
        pass
    # reverse
    # output["S"+str(input["relay"])] = 0 if input["operation_pin"]==1 else 1
    # output["S"+str(input["relay"]-1)] = input["operation_pin"] 
    # forward 
    output["S"+str(input["relay"])] = input["operation_pin"]
    output["S"+str(input["relay"]+1)] = 0 if input["operation_pin"]==1 else 1 
    with open(app.config["OUTPUT_PATH"], 'w') as f:
        f.write(json.dumps(output))

@dashboard.route("/action", methods=["POST"])
def action():  
    position = request.form.get('position')
    
    input = None
    flag = 0
    if position: 
        settings = None
        with open(app.config["SETTINGS_PATH"]) as f:
            content = f.read()
            settings = json.loads(content)
        if settings is not None and settings.get(str(position)) is not None:
            input = settings.get(str(position))
    if input:
        input["waiting"] = 1
        with open(app.config["INPUT_PATH"], 'w') as f:
            f.write(json.dumps(input))
        with open(app.config["INPUT_PATH"]) as f:
            content = f.read()
            if content:
                input_check = json.loads(content)
                if input_check==input:
                    flag = 1
    if flag==1:
        start_time = time.time()
        t = threading.Thread(target=sim, args=(input,))
        t.start()
        while time.time()-start_time < input["buffer_time"]+5:
            pass
        input["waiting"] = 0
        with open(app.config["INPUT_PATH"], 'w') as f:
            f.write(json.dumps(input))
        with open(app.config["INPUT_PATH"]) as f:
            content = f.read()
            if content:
                input_check = json.loads(content)
                if input_check==input:
                    flag = 1
                else:
                    flag = 0
    if flag==1:
        return "success"
    else:
        return "error"