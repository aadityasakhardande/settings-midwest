import os
import json
import sys

profile_name = "cirrus_1"
base_location = "/home/gmr/cirrus_dev/src/platform/profile_module/profile_handler/data/profiles/"

folder_path = base_location + profile_name
folder_contents = os.listdir(folder_path)

for item in folder_contents:
    item_path = os.path.join(folder_path, item)
    if os.path.isdir(item_path): # replace 'folder_name' with the name of the folder you're looking for
        rt0_path = item_path + "/pass_settings/rt0.json"
        print(f"Found the file at: {rt0_path}")
        break  # Stop searching once you've found the folder

with open(rt0_path) as j:
    data = json.load(j)

if "robot_traj" in data:
    traj = data["robot_traj"]
    print("loaded trajectory object \n")

rt0_time = [] 
for i in range(len(traj)):
    if traj[i]["time"] != 0.0:
        rt0_time.append((traj[i]["time"]))
    else:
        rt0_time.append((0.008))

print(sum(rt0_time))


sys.exit()