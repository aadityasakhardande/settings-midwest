import numpy as np
from scipy.spatial.transform import Rotation as R
import matplotlib.pyplot as plt
import matplotlib.widgets as widgets
from mpl_toolkits.mplot3d import Axes3D

# --- Configuration Options ---
INITIAL_WIDTH = 8    # Initial figure width (inches)
INITIAL_HEIGHT = 8    # Initial figure height (inches)

# Default view parameters and axis limits for the 3D plot
DEFAULT_ELEV = -175
DEFAULT_AZIM = 6            # Default azimuth set to 6
AXIS_XLIM = [-0.8, -0.2]
AXIS_YLIM = [-0.6, 0.6]
AXIS_ZLIM = [0.0, 0.8]

# Transformation axis (tf) arrow length
ARROW_LENGTH = 0.5  # Configure the lengths of the transformation arrows here

def transformation_matrix(translation, quaternion):
    """Create a 4x4 transformation matrix from translation and quaternion."""
    rotation_matrix = R.from_quat(quaternion).as_matrix()
    transform = np.eye(4)
    transform[:3, :3] = rotation_matrix
    transform[:3, 3] = translation
    return transform

def apply_transformation(base_tf, translation, quaternion):
    """Apply a transformation to a base transformation matrix."""
    new_tf = transformation_matrix(translation, quaternion)
    return np.dot(base_tf, new_tf)

def plot_transformation(ax, tf, label, color):
    """Visualize the transformation in 3D space and display the label."""
    origin = tf[:3, 3]
    x_axis = tf[:3, :3] @ np.array([1, 0, 0])
    y_axis = tf[:3, :3] @ np.array([0, 1, 0])
    z_axis = tf[:3, :3] @ np.array([0, 0, 1])
    
    ax.quiver(*origin, *x_axis, color='r', length=ARROW_LENGTH, normalize=True)
    ax.quiver(*origin, *y_axis, color='g', length=ARROW_LENGTH, normalize=True)
    ax.quiver(*origin, *z_axis, color='b', length=ARROW_LENGTH, normalize=True)
    ax.text(*origin, label, color=color)

def update(val):
    """Update transformation based on slider values, update text boxes, and keep fixed view."""
    # Get Euler angles from sliders
    angles = [slider_x.val, slider_y.val, slider_z.val]
    new_quaternion = R.from_euler('xyz', angles, degrees=True).as_quat()
    
    ax.clear()
    ax.set_xlim(AXIS_XLIM)
    ax.set_ylim(AXIS_YLIM)
    ax.set_zlim(AXIS_ZLIM)
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.set_zlabel("Z (m)")
    ax.view_init(elev=DEFAULT_ELEV, azim=DEFAULT_AZIM)
    ax.grid(False)
    
    transformed_tf = apply_transformation(base_tf, translation, new_quaternion)
    
    plot_transformation(ax, base_tf, "tool0", "black")
    plot_transformation(ax, transformed_tf, "tooltcp", "blue")
    
    # Format each quaternion component with 7 significant figures;
    # if a component is near zero (abs < 1e-6), show it as 0.
    tol = 1e-4
    formatted_quat = "[" + ", ".join("0" if abs(q) < tol else f"{q:.7g}" for q in new_quaternion) + "]"
    quaternion_text.set_text(f"Quaternion: {formatted_quat}")
    
    # Update Euler angle text boxes with slider values (formatted to two decimals)
    text_box_x.set_val(f"{slider_x.val:.2f}")
    text_box_y.set_val(f"{slider_y.val:.2f}")
    text_box_z.set_val(f"{slider_z.val:.2f}")
    
    fig.canvas.draw_idle()

def submit_x(text):
    slider_x.set_val(float(text))

def submit_y(text):
    slider_y.set_val(float(text))

def submit_z(text):
    slider_z.set_val(float(text))

# --- Base Transformation Parameters ---
translation = np.array([-0.379, 0, 0.257953])
# Use default Euler angles [0, 90, -180] to compute the base quaternion
quaternion = R.from_euler('xyz', [0, 90, -180], degrees=True).as_quat()
base_tf = transformation_matrix(translation, quaternion)

# --- Create the Figure and 3D Axes ---
fig = plt.figure(figsize=(INITIAL_WIDTH, INITIAL_HEIGHT))
fig.canvas.manager.set_window_title("tcp calibration pro")
# Move the main 3D plot upward so the widget area is below it.
plt.subplots_adjust(left=0.1, bottom=0.55, right=0.95, top=0.95)
ax = fig.add_subplot(111, projection='3d')
ax.set_xlim(AXIS_XLIM)
ax.set_ylim(AXIS_YLIM)
ax.set_zlim(AXIS_ZLIM)
ax.set_xlabel("X (m)")
ax.set_ylabel("Y (m)")
ax.set_zlabel("Z (m)")
ax.view_init(elev=DEFAULT_ELEV, azim=DEFAULT_AZIM)
ax.grid(False)

plot_transformation(ax, base_tf, "Base", "black")
plot_transformation(ax, apply_transformation(base_tf, translation, quaternion), "Transformed", "blue")

# --- Sliders for Euler Angle Rotation ---
axcolor = 'lightgoldenrodyellow'
ax_x = plt.axes([0.1, 0.48, 0.65, 0.03], facecolor=axcolor)
ax_y = plt.axes([0.1, 0.43, 0.65, 0.03], facecolor=axcolor)
ax_z = plt.axes([0.1, 0.38, 0.65, 0.03], facecolor=axcolor)

slider_x = widgets.Slider(ax_x, 'Rotate X', -180, 180, valinit=0, valfmt="%.2f")
slider_y = widgets.Slider(ax_y, 'Rotate Y', 0, 180, valinit=90, valfmt="%.2f")
slider_z = widgets.Slider(ax_z, 'Rotate Z', -270, -90, valinit=-180, valfmt="%.2f")

# Hide the slider's built-in numeric display
slider_x.valtext.set_visible(False)
slider_y.valtext.set_visible(False)
slider_z.valtext.set_visible(False)

# --- Text Boxes for Manual Euler Angle Entry ---
axbox_x = plt.axes([0.8, 0.48, 0.1, 0.03])
axbox_y = plt.axes([0.8, 0.43, 0.1, 0.03])
axbox_z = plt.axes([0.8, 0.38, 0.1, 0.03])

text_box_x = widgets.TextBox(axbox_x, "X:", initial="0.00")
text_box_y = widgets.TextBox(axbox_y, "Y:", initial="90.00")
text_box_z = widgets.TextBox(axbox_z, "Z:", initial="-180.00")

text_box_x.on_submit(submit_x)
text_box_y.on_submit(submit_y)
text_box_z.on_submit(submit_z)

# --- Quaternion Display (Single FigText) ---
quaternion_text = plt.figtext(0.1, 0.05, "", fontsize=12, color='black')

# --- Connect Slider Updates ---
slider_x.on_changed(update)
slider_y.on_changed(update)
slider_z.on_changed(update)

# Initialize the display
update(None)

plt.show()