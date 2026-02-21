#!/usr/bin/env python3
import subprocess
import os
import sys
import time
import termios
import tty

# Path to your ROS 2 workspace setup
WORKSPACE_SETUP = "/workspaces/platform/install/setup.bash"

# Service / topic definitions
VACUUM_SERVICE_NAME = "/io_module/toggle_vacuum"
VACUUM_SERVICE_TYPE = "std_srvs/srv/SetBool"

SPINDLE_RPM_TOPIC = "/io_module/setServoMotorRPM"
SPINDLE_RPM_MSG = "std_msgs/msg/UInt16"
SPINDLE_RPM_VALUE = 500

TOOL_SERVICE_NAME = "/io_module/toggle_tool"
TOOL_SERVICE_TYPE = "std_srvs/srv/SetBool"

AFD_SERVICE_NAME = "/force_intf/set_f_target"
AFD_SERVICE_TYPE = "gmr_msgs/srv/SetInt"

CLAMP_OPEN_SERVICE_NAME = "/io_module/open_clamp"
CLAMP_CLOSE_SERVICE_NAME = "/io_module/close_clamp_for_pick_up"
CLAMP_SERVICE_TYPE = "std_srvs/srv/Trigger"

LIGHT_SERVICE_NAME = "/io_module/toggle_ambient_light"
LIGHT_SERVICE_TYPE = "std_srvs/srv/SetBool"

STAGE_SERVICE_NAME = "/io_module/toggle_stage"
STAGE_SERVICE_TYPE = "gmr_msgs/srv/ToggleUInt32"

TEST_COIL_SERVICE_NAME = "/io_module/test_coil"
TEST_COIL_SERVICE_TYPE = "developer_msgs/srv/ToggleCoil"

COGNEX_SERVICE_NAME = "/sandpaper_manager/trigger_camera"
COGNEX_SERVICE_TYPE = "std_srvs/srv/Trigger"

AFD_DEFAULT_NEG = -10
AFD_DEFAULT_POS = 10

# Global status
last_status = {"text": "No command run yet.", "success": None}


# ---------- Formatting helpers ----------
def color_text(text: str, color_code: str) -> str:
    return f"\033[{color_code}m{text}\033[0m"


def bold_yellow(text: str) -> str:
    return f"\033[1;33m{text}\033[0m"


def set_status(desc: str, success: bool, extra: str = ""):
    global last_status
    base = f"{desc} - {'SUCCESS' if success else 'FAILURE'}"
    if extra:
        base += f" ({extra})"
    last_status = {"text": base, "success": success}


# ---------- Core command helpers ----------
def run_cmd(cmd: str, desc: str):
    print(color_text(f"→ {desc}...", "96"))
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        print(color_text(f"✅ {desc} succeeded.", "92"))
        set_status(desc, True)
    else:
        print(color_text(f"❌ {desc} failed (code {result.returncode}).", "91"))
        if result.stdout.strip():
            print("---- STDOUT ----")
            print(result.stdout)
        if result.stderr.strip():
            print("---- STDERR ----")
            print(result.stderr)
        set_status(desc, False, f"code {result.returncode}")


def call_setbool(service: str, srv_type: str, state: bool, label: str):
    data = "true" if state else "false"
    cmd = (
        f"bash -c 'source {WORKSPACE_SETUP} && "
        f"ros2 service call {service} {srv_type} \"{{data: {data}}}\"'"
    )
    run_cmd(cmd, f"{label} {'ON' if state else 'OFF'}")


def call_trigger(service: str, srv_type: str, label: str):
    cmd = (
        f"bash -c 'source {WORKSPACE_SETUP} && "
        f"ros2 service call {service} {srv_type} \"{{}}\"'"
    )
    run_cmd(cmd, label)


def call_afd(value: int):
    cmd = (
        f"bash -c 'source {WORKSPACE_SETUP} && "
        f"ros2 service call {AFD_SERVICE_NAME} {AFD_SERVICE_TYPE} \"{{data: {value}}}\"'"
    )
    run_cmd(cmd, f"Set AFD force target {value}")


def call_stage(stage_key: int, state: bool):
    data = "true" if state else "false"
    cmd = (
        f"bash -c 'source {WORKSPACE_SETUP} && "
        f"ros2 service call {STAGE_SERVICE_NAME} {STAGE_SERVICE_TYPE} "
        f"\"{{key: {stage_key}, value: {data}}}\"'"
    )
    run_cmd(cmd, f"Stage {stage_key} {'ON' if state else 'OFF'}")


def call_test_coil(address: int, state: bool):
    data = "true" if state else "false"
    cmd = (
        f"bash -c 'source {WORKSPACE_SETUP} && "
        f"ros2 service call {TEST_COIL_SERVICE_NAME} {TEST_COIL_SERVICE_TYPE} "
        f"\"{{address: {address}, value: {data}}}\"'"
    )
    run_cmd(cmd, f"Test Coil (Address {address}) {'ON' if state else 'OFF'}")


def call_cognex_trigger():
    cmd = (
        f"bash -c 'source {WORKSPACE_SETUP} && "
        f"ros2 service call {COGNEX_SERVICE_NAME} {COGNEX_SERVICE_TYPE} \"{{}}\"'"
    )
    run_cmd(cmd, "Trigger Cognex Camera")


# ---------- AFD calibration (nc.traditional-based) ----------
def run_afd_calibration():
    """Run AFD calibration routine (equivalent to provided bash script)."""
    ip = "192.168.11.228"
    port = "1993"
    poses = [5.0, 10.0, 15.0, 8.0, 13.0]
    payloads = []

    print(color_text("→ Starting AFD calibration...", "96"))

    def send_cmd(cmd: str, wait: int = 1):
        subprocess.run(
            f'echo -n "{cmd}" | nc.traditional -w {wait} -q 10 -u {ip} {port}',
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def capture_payload():
        try:
            output = subprocess.check_output(
                f'echo -n "/afd/dumpCfg" | nc.traditional -w 2 -q 10 -u {ip} {port}',
                shell=True,
                text=True,
            )
            # Look for "payloadWeight":<number>
            for line in output.splitlines():
                if '"payloadWeight":' in line:
                    part = line.split('"payloadWeight":', 1)[1]
                    num_str = part.split(",", 1)[0].strip()
                    return float(num_str)
        except Exception:
            pass
        return None

    try:
        # Position mode
        send_cmd("/afd/controlMode=2", wait=1)

        # Loop through poses
        for pos in poses:
            print(f"  • Moving to position {pos:.1f} mm...")
            send_cmd(f"/afd/commandPosition={pos}", wait=4)
            send_cmd("/afd/weighPayload", wait=4)
            time.sleep(0.5)
            p = capture_payload()
            if p is not None:
                payloads.append(p)
                print(color_text(f"    Payload captured: {p:.3f}", "92"))
            else:
                print(color_text("    ⚠️ Failed to read payload.", "91"))

        if not payloads:
            msg = "No payloads captured — calibration failed."
            print(color_text(f"❌ {msg}", "91"))
            set_status("AFD Calibration", False, "no payload data")
            return

        avg_payload = sum(payloads) / len(payloads)
        print(color_text(f"\nAverage payload weight: {avg_payload:.3f}", "93"))

        # Force mode
        send_cmd("/afd/controlMode=1", wait=1)
        # Set average payload weight
        send_cmd(f"/afd/payloadWeight={avg_payload}", wait=2)
        # Test force -6
        send_cmd("/afd/commandForce=-6", wait=5)

        # Get positional error
        try:
            pos_output = subprocess.check_output(
                f'echo -n "/afd/actualPosition" | nc.traditional -w 2 -q 10 -u {ip} {port}',
                shell=True,
                text=True,
            )
            afd_pos = None
            for line in pos_output.splitlines():
                if '"/afd/actualPosition":' in line:
                    part = line.split('"/afd/actualPosition":', 1)[1]
                    num_str = part.split(",", 1)[0].strip()
                    afd_pos = float(num_str)
                    break
        except Exception:
            afd_pos = None

        # Reset force to 0
        send_cmd("/afd/commandForce=0", wait=5)

        if afd_pos is None:
            afd_pos = 0.0

        msg = (
            f"Average Payload Weight: {avg_payload:.3f} with {len(poses)} positions. "
            f"Current positional offset from 0 is {afd_pos:.3f} mm for -6N force."
        )
        print(color_text(f"\n✅ AFD Calibration completed successfully.\n{msg}", "92"))
        set_status("AFD Calibration", True)
    except Exception as e:
        print(color_text(f"❌ Calibration error: {e}", "91"))
        set_status("AFD Calibration", False, "exception")


# ---------- Input helpers ----------
def get_key() -> str:
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    return ch


def wait_for_any_key():
    print(color_text("Press any key to continue...", "93"), end="", flush=True)
    get_key()
    print()


def prompt_int(prompt: str) -> int:
    print(prompt, end="", flush=True)
    return int(input().strip())


# ---------- UI helpers ----------
def print_status():
    if last_status["success"] is None:
        print(bold_yellow(f"Last Status: {last_status['text']}"))
    elif last_status["success"]:
        print(bold_yellow("Last Status: ") + color_text(last_status["text"], "92"))
    else:
        print(bold_yellow("Last Status: ") + color_text(last_status["text"], "91"))
    print()


def print_menu(title: str, lines):
    os.system("clear")
    print(color_text(f"=== {title} ===", "1"))
    print_status()
    for line in lines:
        print(line)
    print("---------------------------------\n")


# ---------- Main ----------
def main():
    mode = "main"

    while True:
        # Render current menu
        if mode == "main":
            print_menu(
                "IO CONTROL TERMINAL",
                [
                    f"ROS2 workspace: {WORKSPACE_SETUP}",
                    "  [1] Vacuum",
                    "  [2] Spindle",
                    "  [3] AFD (Force Target)",
                    "  [4] Spindle Tool Clamp",
                    "  [5] Automatic Lighting",
                    "  [6] SPC Stage Test",
                    "  [7] Test IO Coil",
                    "  [8] Trigger Cognex",
                    "  [q] Quit",
                ],
            )
        elif mode == "vacuum":
            print_menu(
                "VACUUM CONTROL",
                [
                    "  [1] Vacuum ON",
                    "  [2] Vacuum OFF",
                    "  [b] Back",
                    "  [q] Quit",
                ],
            )
        elif mode == "spindle":
            print_menu(
                "SPINDLE CONTROL",
                [
                    f"  [1] Set RPM = {SPINDLE_RPM_VALUE}",
                    "  [2] Spindle ON",
                    "  [3] Spindle OFF",
                    "  [b] Back",
                    "  [q] Quit",
                ],
            )
        elif mode == "afd":
            print_menu(
                "AFD FORCE CONTROL",
                [
                    f"  [1] Force = {AFD_DEFAULT_NEG}",
                    f"  [2] Force = {AFD_DEFAULT_POS}",
                    "  [3] Custom target",
                    "  [4] Calibrate AFD",
                    "  [b] Back",
                    "  [q] Quit",
                ],
            )
        elif mode == "clamp":
            print_menu(
                "SPINDLE TOOL CLAMP",
                [
                    "  [1] Open clamp",
                    "  [2] Close clamp",
                    "  [b] Back",
                    "  [q] Quit",
                ],
            )
        elif mode == "light":
            print_menu(
                "AUTOMATIC LIGHTING",
                [
                    "  [1] Light ON",
                    "  [2] Light OFF",
                    "  [b] Back",
                    "  [q] Quit",
                ],
            )
        elif mode == "stage":
            print_menu(
                "SPC STAGE TEST",
                [
                    "  [1] Stage ON  (prompt for key)",
                    "  [2] Stage OFF (prompt for key)",
                    "  [c] Custom key & value",
                    "  [b] Back",
                    "  [q] Quit",
                ],
            )
        elif mode == "coil":
            print_menu(
                "TEST IO COIL",
                [
                    "  [1] Coil ON  (prompt for address)",
                    "  [2] Coil OFF (prompt for address)",
                    "  [c] Custom address & value",
                    "  [b] Back",
                    "  [q] Quit",
                ],
            )
        elif mode == "cognex":
            print_menu(
                "TRIGGER COGNEX CAMERA",
                [
                    "  [1] Trigger Now",
                    "  [b] Back",
                    "  [q] Quit",
                ],
            )

        # Read key
        key = get_key().lower()
        if key == "q":
            print("\nExiting...")
            break

        # ---- MAIN ----
        if mode == "main":
            if key == "1":
                mode = "vacuum"
            elif key == "2":
                mode = "spindle"
            elif key == "3":
                mode = "afd"
            elif key == "4":
                mode = "clamp"
            elif key == "5":
                mode = "light"
            elif key == "6":
                mode = "stage"
            elif key == "7":
                mode = "coil"
            elif key == "8":
                mode = "cognex"
            continue

        # ---- VACUUM ----
        if mode == "vacuum":
            if key == "1":
                call_setbool(VACUUM_SERVICE_NAME, VACUUM_SERVICE_TYPE, True, "Vacuum")
            elif key == "2":
                call_setbool(VACUUM_SERVICE_NAME, VACUUM_SERVICE_TYPE, False, "Vacuum")
            elif key == "b":
                mode = "main"
            continue

        # ---- SPINDLE ----
        if mode == "spindle":
            if key == "1":
                run_cmd(
                    f"bash -c 'source {WORKSPACE_SETUP} && "
                    f"ros2 topic pub --once {SPINDLE_RPM_TOPIC} {SPINDLE_RPM_MSG} "
                    f"\"{{data: {SPINDLE_RPM_VALUE}}}\"'",
                    f"Set spindle RPM {SPINDLE_RPM_VALUE}",
                )
            elif key == "2":
                call_setbool(TOOL_SERVICE_NAME, TOOL_SERVICE_TYPE, True, "Spindle")
            elif key == "3":
                call_setbool(TOOL_SERVICE_NAME, TOOL_SERVICE_TYPE, False, "Spindle")
            elif key == "b":
                mode = "main"
            continue

        # ---- AFD ----
        if mode == "afd":
            if key == "1":
                call_afd(AFD_DEFAULT_NEG)
            elif key == "2":
                call_afd(AFD_DEFAULT_POS)
            elif key == "3":
                try:
                    val = prompt_int("Enter custom force target: ")
                    call_afd(val)
                except ValueError:
                    set_status("AFD custom target", False, "invalid integer")
            elif key == "4":
                run_afd_calibration()
                wait_for_any_key()
            elif key == "b":
                mode = "main"
            continue

        # ---- CLAMP ----
        if mode == "clamp":
            if key == "1":
                call_trigger(CLAMP_OPEN_SERVICE_NAME, CLAMP_SERVICE_TYPE, "Open Clamp")
            elif key == "2":
                call_trigger(CLAMP_CLOSE_SERVICE_NAME, CLAMP_SERVICE_TYPE, "Close Clamp")
            elif key == "b":
                mode = "main"
            continue

        # ---- LIGHT ----
        if mode == "light":
            if key == "1":
                call_setbool(LIGHT_SERVICE_NAME, LIGHT_SERVICE_TYPE, True, "Lighting")
            elif key == "2":
                call_setbool(LIGHT_SERVICE_NAME, LIGHT_SERVICE_TYPE, False, "Lighting")
            elif key == "b":
                mode = "main"
            continue

        # ---- SPC STAGE TEST ----
        if mode == "stage":
            if key in ("1", "2", "c"):
                try:
                    stage_key = prompt_int("Enter stage key: ")
                except ValueError:
                    set_status("Stage", False, "invalid key")
                    wait_for_any_key()
                    continue

                if key == "1":
                    call_stage(stage_key, True)
                elif key == "2":
                    call_stage(stage_key, False)
                else:
                    val = input("Enter value (true/false/1/0): ").strip().lower()
                    state = val in ("true", "1", "t", "y", "yes")
                    call_stage(stage_key, state)
                wait_for_any_key()
            elif key == "b":
                mode = "main"
            continue

        # ---- TEST IO COIL ----
        if mode == "coil":
            if key in ("1", "2", "c"):
                try:
                    addr = prompt_int("Enter coil address: ")
                except ValueError:
                    set_status("Test IO Coil", False, "invalid address")
                    wait_for_any_key()
                    continue

                if key == "1":
                    call_test_coil(addr, True)
                elif key == "2":
                    call_test_coil(addr, False)
                else:
                    val = input("Enter value (true/false/1/0): ").strip().lower()
                    state = val in ("true", "1", "t", "y", "yes")
                    call_test_coil(addr, state)
                wait_for_any_key()
            elif key == "b":
                mode = "main"
            continue

        # ---- COGNEX ----
        if mode == "cognex":
            if key == "1":
                call_cognex_trigger()
                wait_for_any_key()
            elif key == "b":
                mode = "main"
            continue


if __name__ == "__main__":
    main()
