from flask import Blueprint, redirect, render_template, request, url_for, session
import json

from app import app

settings = Blueprint("settings", __name__)

@settings.before_request
def settings_middleware():
    if not session.get("auth")=="Y":
        return redirect(url_for("auth.login"))
    if not session.get("role")=="admin":
        return redirect(url_for("dashboard.index")) 

@settings.route("/settings", methods=["GET"])
def index():
    settings = None
    with open(app.config["SETTINGS_PATH"]) as f:
        content = f.read()
        if content:
            settings = json.loads(content)
            order = []
            for i in range(1, 9):
                order.append(str(i))
                order.append(str(17-i))
            settings = {key: settings[key] for key in order}
            
                
    return render_template("settings.html", settings=settings)

@settings.route("/settings/editform", methods=["GET"])
def edit_form():
    index = request.args.get("index")
    settings = None
    if index:
        with open(app.config["SETTINGS_PATH"]) as f:
            content = f.read()
            if content:
                settings = json.loads(content)
        if settings:
            current_config = settings.get(str(index))
            if current_config: 
                not_available_relays = []
                not_available_pins = []
                for key, value in settings.items():
                    if(key!=str(index)):
                        not_available_relays.append(value["relay"])
                        not_available_pins.append(value["pin"])
                return render_template("settings_form.html", current_config=current_config, not_available_relays=not_available_relays, not_available_pins=not_available_pins)
    return "error"

@settings.route("/settings/edit", methods=["POST"])
def edit():
    response = {
        "status" : "",
        "message" : "",
    }

    if request.method=="POST":
        relay = request.form.get("relay") 
        pin = request.form.get("pin")
        buffer_time = request.form.get("buffer_time")
        position = request.form.get("position")

        settings = None
        with open(app.config["SETTINGS_PATH"], 'r') as f:
            content = f.read()
            if content:
                settings = json.loads(content)
        if settings is not None and settings.get(position) is not None:
            settings.get(position)["relay"] = int(request.form.get("relay")) if (request.form.get("relay")!="None") else request.form.get("relay")
            settings.get(position)["pin"] = int(request.form.get("pin")) if (request.form.get("pin")!="None") else request.form.get("pin")
            settings.get(position)["buffer_time"] = int(request.form.get("buffer_time"))
            content = json.dumps(settings)
            if content:
                with open(app.config["SETTINGS_PATH"], 'w') as f:
                    f.write(content)
                response["status"] = "success"
                response["message"] = "updated successfully"
                return response
            
    response["status"] = "error"
    response["message"] = "something went wrong, try again"

    return response

@settings.route("/settings/backup", methods=["GET"])
def backup():
    settings = None
    with open(app.config["BACKUP_SETTINGS_PATH"], 'r') as f:
        content = f.read()
        if content:
            settings = json.loads(content)
    if settings:
        with open(app.config["SETTINGS_PATH"], 'w') as f:
            f.write(json.dumps(settings))

    return "success"