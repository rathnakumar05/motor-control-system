'''{
    "0" : {
        "index" : 1,
        "motor_name" : "MOTOR 1",
        "operation_pin" : 1,
        "relay" : "None",
        "feed_back" : 1,
        "pin" : 1,
        "buffer_time" : 10
    }
}'''

import json

out = {}
k = 1
d = 1
for i in range(1, 17):
    out[str(i)] = {
        "index" : k,
        "operation_pin" : d,
        "relay" : "None",
        "feed_back" : d,
        "pin" : "None",
        "buffer_time" : 0,
        "position" : i
    }
    if(i==8):
        d = 0
    elif(i>8):
        k -= 1
    else:
        k += 1

# with open("settings.json", "w") as f:
#     f.write(json.dumps(out))
obj = {}
k = 0
for i in range(1, 21):
    if (i>10):
        k = 1
    obj["S"+str(i)] = k

with open("output.json", 'w') as f:
    f.write(json.dumps(obj))