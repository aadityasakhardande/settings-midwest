import json
import os
data_path = "/home/gmr/wetstyle_deploy/src/platform/sandpaper_manager/change_sp_hdlr/data"
home_to_cam_path = os.path.join(data_path, "hometocam.json")
cam_to_home_path = os.path.join(data_path, "camtohome.json")
home_2_pick_path = os.path.join(data_path, "hometocam.json")
pick_2_home_path = os.path.join(data_path, "camtohome.json")
remove_path = os.path.join(data_path, "camtohome.json")

data_1 = [0.00, -30.00, -30.00, -90.00, 0.00, 90.00]
data_2 = [0.00, 30.00, -30.00, -90.00, 0.00, 90.00 ]
home_base = data_1
cam_homing_base = data_2
close_2_cam_base = data_1
camera_base = data_2
pick_base = data_1
remove_homing_base = data_2
r1_base = data_1
r2_base = data_2
r3_base = data_1
r3_homing_base = data_2


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
cam_homing = convert_2_json_object(cam_homing_base)
close_2_cam = convert_2_json_object(close_2_cam_base)
camera = convert_2_json_object(camera_base)
pick = convert_2_json_object(pick_base)
# push_down_slightly_after_pick = 
remove_homing = convert_2_json_object(remove_homing_base)
r1 = convert_2_json_object(r1_base)
r2 =  convert_2_json_object(r2_base)
r3 = convert_2_json_object(r3_base)
r3_homing =  convert_2_json_object(r3_homing_base)


###SEQUENCES###
hometocam = {
    "header":{
        "angleUnits": "d",
        "timeUnits": "ms"
    },
    "path": [
        home,
        cam_homing,
        close_2_cam,
        camera
    ],
    "comment": "From home to camera for inspection."
}

camtohome = {
    "header":{
        "angleUnits": "d",
        "timeUnits": "ms"
    },
    "path": [
        close_2_cam,
        cam_homing,
        home
    ],
    "comment": "From home to camera for inspection."
}

home2pick = {
    "header":{
        "angleUnits": "d",
        "timeUnits": "ms"
    },
    "path": [
        home,
        pick  
    ],
    "comment": "From home to camera for inspection."
}

pick2home = {
    "header":{
        "angleUnits": "d",
        "timeUnits": "ms"
    },
    "path": [
        # push_down_slightly_after_pick,
        pick,
        home
    ],
    "comment": "From home to camera for inspection."
}

remove = {
    "header":{
        "angleUnits": "d",
        "timeUnits": "ms"
    },
    "path": [
        home,
        remove_homing,
        r1,
        r2,
        r3,
        r3_homing,
        home
    ],
    "comment": "From home to camera for inspection."
}


h2c = json.dumps(hometocam, indent= 4)
c2h = json.dumps(camtohome, indent= 4)
h2p = json.dumps(home2pick, indent= 4) 
p2h = json.dumps(pick2home, indent= 4)
rem = json.dumps(remove, indent= 4)

home_to_cam_path = os.path.join(data_path, "hometocam.json")
cam_to_home_path = os.path.join(data_path, "camtohome.json")
home_2_pick_path = os.path.join(data_path, "home2pick.json")
pick_2_home_path = os.path.join(data_path, "pick2home.json")
remove_path = os.path.join(data_path, "remove.json")

with open(home_to_cam_path, 'w') as f:
        f.write(h2c)
        print('done')

with open(cam_to_home_path, 'w') as g:
        g.write(c2h)
        print('done')

with open(home_2_pick_path, 'w') as h:
        h.write(h2p)
        print('done')

with open(pick_2_home_path, 'w') as i:
        i.write(p2h)
        print('done')

with open(remove_path, 'w') as j:
        j.write(rem)
        print('done')
