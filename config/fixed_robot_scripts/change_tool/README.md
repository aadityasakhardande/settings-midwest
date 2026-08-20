# Robot Tool Change Procedure Documentation

This documentation provides an overview of the robot poses, motion types, and scripts required for automatic and manual tool change procedures. Each step follows a specific sequence using either joint or linear motion to ensure safe and efficient tool handling.

## Key Poses in Tool Change

1. **Local Home Pose**
   - **Description**: The safe starting and ending position for the tool change procedure. The robot returns to this position to await the next command.

2. **Pickup Tool Linear Entry Point**
   - **Description**: The initial position for beginning the linear approach to the tool, enabling precise entry.

3. **Pickup Tool Point**
   - **Description**: The location where the robot securely picks up the tool.

4. **Pickup Tool Exit Point**
   - **Description**: The final position to safely exit the tool area after pickup, designed to avoid any obstacles.

5. **Tool Presence Check Point**
   - **Description**: Position where the tool presence sensor verifies if the tool is correctly attached.

6. **Manual Tool Change Pose**
   - **Description**: The position for manual tool replacement, with the robot flange facing upward to facilitate easy access.

> **Note**: Each tool slot requires its own unique set of Pickup Tool Linear Entry, Pickup Tool, and Pickup Tool Exit points.

## Motion Types

1. **Joint Motion**
   - **Description**: Coordinated joint movements without specific path constraints to reach a target position.
   - **Usage**:
     - From Local Home Pose to Pickup Tool Linear Entry Point.
     - From Pickup Tool Exit Point back to Local Home Pose.

2. **Linear Motion**
   - **Description**: A controlled, straight-line motion necessary when approaching or retreating from tool points.
   - **Usage**:
     - From Pickup Tool Linear Entry Point to Pickup Tool Point.
     - From Pickup Tool Point to Pickup Tool Exit Point.

## Robot Scripts

### Tool Pickup and Exit Scripts
For each tool, the following scripts facilitate the tool pickup and exit process:

- **pickup_tool_entry_jointX.json**: Moves from Local Home Pose to Pickup Tool Linear Entry Point using joint motion.
- **pickup_tool_entry_linearX.json**: Moves from Pickup Tool Linear Entry Point to Pickup Tool Point using linear motion.
- **pickup_tool_exit_linearX.json**: Moves from Pickup Tool Point to Pickup Tool Exit Point using linear motion.
- **pickup_tool_exit_jointX.json**: Returns from Pickup Tool Exit Point to Local Home Pose using joint motion.

> **Note**: `X` represents the tool index, starting from 1 for each tool.

### Tool Presence Check Scripts
Used to approach and depart the tool presence check point for verifying tool attachment:

- **tool_check_approach.json**: Moves from Local Home Pose to Tool Presence Check Point using joint motion.
- **tool_check_depart.json**: Returns from Tool Presence Check Point to Local Home Pose using joint motion.

### Manual Tool Change Scripts
These scripts position the robot for manual tool replacement:

- **manual_tool_change_entry.json**: Moves from Local Home Pose to Manual Tool Change Pose using joint motion.
- **manual_tool_change_exit.json**: Returns from Manual Tool Change Pose to Local Home Pose using joint motion.

> **Note**: for more details for how to compose fixed robot scritps, please check the [schema file](../schema/fixed_robot_scripts_schema.json)