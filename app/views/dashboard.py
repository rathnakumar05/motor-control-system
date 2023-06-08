from flask import render_template, request, Blueprint, session, redirect, url_for
import json
import time
import threading 
import sqlite3

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
    issue = 0
    emergency = 0
    waiting = 0
    logout = request.args.get("p")

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
            if (settings[str(i)]["pin"] is not None and settings[str(i)]["pin"]=="None") or (settings[str(17-i)]["pin"] is not None and settings[str(17-i)]["pin"]=="None") :
                return render_template("dashboard_error.html", error="Settings config not set properly", error_type="config")
            motors[str(i)] = {
                "forward" : settings[str(i)],
                "reverse" : settings[str(17-i)],
                "enable" : 0
            }
            # if output["S"+str(settings[str(i)]["pin"])] is not None and output["S"+str(settings[str(i)]["pin"])]==0 and output["S"+str(settings[str(17-i)]["pin"])] is not None and output["S"+str(settings[str(17-i)]["pin"])]==0:
            #     return render_template("dashboard_error.html", error="Something went wrong with the motor control system")
            motors[str(i)]["forward"]["output"] = output["S"+str(settings[str(i)]["pin"])]
            motors[str(i)]["reverse"]["output"] = output["S"+str(settings[str(17-i)]["pin"])]

        if input:
            if input["relay"]==99:
                issue = 1
                emergency = 1
                # return render_template("dashboard_error.html", error="Reset the system after the emergency situation ended", error_type="emergency")
            if input.get("waiting") is not None and input["waiting"]==1:
                waiting = 1
            if input["operation_mode"]==1:
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
            if output["S"+str(settings[str(1)]["pin"])]==1 and output["S"+str(settings[str(16)]["pin"])]==0:
                motors["1"]["enable"] = 1
                current_sequence = "OPEN"
                current_motor = "1"
                input = { "index" : "1" }

        if str(input["index"])=="1":
            if input["operation_mode"]==0:
                for key, value in motors.items():
                    if not (value["forward"]["output"]==1 and value["reverse"]["output"]==0):
                        motors[key]["issue"] = 1
                        issue = 1
            else:
                temp_sequence = current_sequence
                for key,value in motors.items():
                    if temp_sequence=="CLOSE":
                        if not (value["forward"]["output"]==1 and value["reverse"]["output"]==0):
                            motors[key]["issue"] = 1
                            issue = 1
                    else:
                        if not (value["forward"]["output"]==0 and value["reverse"]["output"]==1):
                            motors[key]["issue"] = 1
                            issue = 1
                    if str(input["index"])==key:
                        temp_sequence = "CLOSE" if temp_sequence=="OPEN" else "OPEN"

        elif str(input["index"])=="8":
            if input["operation_mode"]==1:
                for key, value in motors.items():
                    if not (value["forward"]["output"]==0 and value["reverse"]["output"]==1):
                        motors[key]["issue"] = 1
                        issue = 1
            else:
                temp_sequence = current_sequence
                for key,value in motors.items():
                    if str(input["index"])==key:
                        temp_sequence = "CLOSE" if temp_sequence=="OPEN" else "OPEN"
                    if temp_sequence=="CLOSE":
                        if not (value["forward"]["output"]==0 and value["reverse"]["output"]==1):
                            motors[key]["issue"] = 1
                            issue = 1
                    else:
                        if not (value["forward"]["output"]==1 and value["reverse"]["output"]==0):
                            motors[key]["issue"] = 1
                            issue = 1
        else:
            if current_sequence=="OPEN":
                temp_sequence = current_sequence
                for key,value in motors.items():
                    if temp_sequence=="CLOSE":
                        if not (value["forward"]["output"]==1 and value["reverse"]["output"]==0):
                            motors[key]["issue"] = 1
                            issue = 1
                    else:
                        if not (value["forward"]["output"]==0 and value["reverse"]["output"]==1):
                            motors[key]["issue"] = 1
                            issue = 1
                    if str(input["index"])==key:
                        temp_sequence = "CLOSE" if temp_sequence=="OPEN" else "OPEN"
            else:
                temp_sequence = current_sequence
                for key,value in motors.items():
                    if str(input["index"])==key:
                        temp_sequence = "CLOSE" if temp_sequence=="OPEN" else "OPEN"
                    if temp_sequence=="CLOSE":
                        if not (value["forward"]["output"]==0 and value["reverse"]["output"]==1):
                            motors[key]["issue"] = 1
                            issue = 1
                    else:
                        if not (value["forward"]["output"]==1 and value["reverse"]["output"]==0):
                            motors[key]["issue"] = 1
                            issue = 1
    
    if logout=="Y" and issue!=1:
        session.clear()
        return redirect(url_for("auth.login"))
    return render_template("index.html", motors=motors, current_sequence=current_sequence, current_motor=current_motor, issue=issue, emergency=emergency, waiting=waiting)

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
    output["S"+str(input["relay"])] = input["operation_mode"] 
    output["S"+str(input["relay"]-1)] = 0 if input["operation_mode"]==1 else 1 
    # forward 
    # output["S"+str(input["relay"])] = 0 if input["operation_mode"]==1 else 1
    # output["S"+str(input["relay"]+1)] = input["operation_mode"]
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
        input["status"] = 1
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
        # t = threading.Thread(target=sim, args=(input,))
        # t.start()
        while time.time()-start_time < input["buffer_time"]+5:
            pass
        with open(app.config["INPUT_PATH"]) as f:
            content = f.read()
            if content:
                input = json.loads(content)
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

    logout = "N"
    if input["index"]==8 and input["operation_mode"]==1:
        logout = "Y"
    if input["index"]==1 and input["operation_mode"]==0:
        logout = "Y"
    if flag==1:
        try:
            conn = sqlite3.connect(app.config["SQL"])
            cursor = conn.cursor()
            sql = '''INSERT INTO report(users, squence, motor, created_date, created_date_int) VALUES(?, ?, ?, datetime('now', 'localtime'),strftime('%s','now'))'''
            squence = "open" if input["operation_mode"]==1 else "close"
            motor = input["index"]
            username = session.get("username")
            cursor.execute(sql, (username, squence, motor))
            conn.commit()
        except Exception as err:
            pass
        if(logout=="Y"):
            return "logout"
        else:
            return "success"
    else:
        return "error"
    
@dashboard.route("/emergency", methods=["POST"])
def emergency():
    status = int(request.form.get("status"))
    input = None
    flag = 0
    with open(app.config["INPUT_PATH"]) as f:
        content = f.read()
        if content:
            input = json.loads(content)

    settings = None
    with open(app.config["SETTINGS_PATH"]) as f:
        content = f.read()
        settings = json.loads(content)
    if input==None:
        if settings:
            input = settings["1"]
            input["waiting"] = 0
            input["status"] = 0
    else:
        input = settings[str(input["position"])] 
        input["waiting"] = 0
        input["status"] = 0

    state = "OFF"
    if status==1:
        state = "ON"
        input["relay"] = 99
        input["status"] = 1

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
        try:
            conn = sqlite3.connect(app.config["SQL"])
            cursor = conn.cursor()
            sql = '''INSERT INTO report(users, squence, motor, created_date, created_date_int) VALUES(?, ?, ?, datetime('now'),strftime('%s','now'))'''
            username = session.get("username")
            squence = f"emergency {state}"
            motor = input["index"]
            cursor.execute(sql, (username, squence, motor))
            conn.commit()
        except Exception as err:
            pass
        return "success"
    else:
        return "error"
    
@dashboard.route("/reset", methods=["GET"])
def reset():
    flag = 0
    settings = None
    input = None
    with open(app.config["SETTINGS_PATH"]) as f:
        content = f.read()
        settings = json.loads(content)
    if settings is not None and settings.get('16') is not None:
        input = settings.get('16')

    if input is not None:
        input["waiting"] = 0
        input["status"] = 0
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
    