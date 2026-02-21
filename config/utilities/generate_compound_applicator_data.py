#!/usr/bin/env python3

import json
import os
data_path = "/home/gmr/wetstyle_deploy/src/platform/sandpaper_manager/apply_cp_hdlr/data"
home_to_plate_path = os.path.join(data_path, "hometoplate.json")
plate_to_home_path = os.path.join(data_path, "platetohome.json")

data_1 = [0.00, 27.248, -34.189, 0, 61.433, 0]
data_2 = [0.00, 27.248, -34.189, 0, 61.433, 0]

# home_base = [-4.203, 55.078, -10.331, 182.044, -66.310, -183.782]
# pick_base = [-4.731, 70.439, -1.943, 182.499, -73.278, -183.687]

home_base = data_1
pick_base = data_2

###JSON objects###
def convert_2_json_object(list):
    json_object = {
            "type": "movej",
            "target": list,
            "time": 500,
            "tool_status": False
        }
    return json_object

home = convert_2_json_object(home_base)
plate = convert_2_json_object(pick_base)


###SEQUENCES###

home2plate = {
    "header":{
        "angleUnits": "d",
        "timeUnits": "ms"
    },
    "path": [
        home,
        plate  
    ],
    "comment": "From home to camera for inspection."
}

plate2home = {
    "header":{
        "angleUnits": "d",
        "timeUnits": "ms"
    },
    "path": [
        # push_down_slightly_after_pick,
        plate,
        home
    ],
    "comment": "From home to camera for inspection."
}


h2p = json.dumps(home2plate, indent= 4) 
p2h = json.dumps(plate2home, indent= 4)

with open(home_to_plate_path, 'w') as h:
        h.write(h2p)
        print('done')

with open(plate_to_home_path, 'w') as i:
        i.write(p2h)
        print('done')
