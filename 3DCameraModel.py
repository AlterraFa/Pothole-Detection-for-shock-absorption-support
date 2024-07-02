import matplotlib.pyplot as plt
from itertools import combinations
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

def planeCreate(corner: np.ndarray):
    xmax = corner[:, 0].max()
    xmin = corner[:, 0].min()
    ymax = corner[:, 1].max()
    ymin = corner[:, 1].min()
    actualCorner = np.array([[xmin, ymax], [xmax, ymin]])
    points = np.array([
        [0, 0, 0, 1]
    ] * 4)
    points[0, :2] = actualCorner[0]
    points[1, :2] = np.array([xmax, ymax])
    points[2, :2] = actualCorner[1]
    points[3, :2] = np.array([xmin, ymin])
    return points

def homogeneous_matrix_y(theta, tx, ty, tz):
    cos_theta = np.cos(theta)
    sin_theta = np.sin(theta)
    rotation_y = np.array([
        [cos_theta, 0, sin_theta, 0],
        [0, 1, 0, 0],
        [-sin_theta, 0, cos_theta, 0],
        [0, 0, 0, 1]
    ])
    translation = np.array([
        [1, 0, 0, tx],
        [0, 1, 0, ty],
        [0, 0, 1, tz],
        [0, 0, 0, 1]
    ])
    return np.dot(translation, rotation_y)

def drawPlane(points, ax):
    ax.scatter(points[:, 0], points[:, 1], points[:, 2], color='red')
    verts = [list(zip(points[:, 0], points[:, 1], points[:, 2]))]
    plane = Poly3DCollection(verts, alpha=0.5, edgecolor='r')
    ax.add_collection3d(plane)

tilt = 74

# Create initial plane points
points = planeCreate(np.array([[-700, -500], [500, 500]]))

# Transform camera plane
cameraPlane = (homogeneous_matrix_y(np.deg2rad(-tilt), -384, 0, 110) @ planeCreate(np.array([[-25, -50], [25, 50]])).T).T.astype(int)

# Define center projection point
centerProjection = (homogeneous_matrix_y(np.deg2rad(-tilt), -384, 0, 110) @ np.array([[0, 0, 80, 1]]).T).T.astype(int)

# Create a figure and a 3D axis
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

# Select all pairs of points from the camera plane
pairs = combinations(cameraPlane, 2)


for idx in range(0, 4):
    # Combine with center projection to define the plane
    plane_points = np.vstack([centerProjection[0, :3], cameraPlane[idx - 1][:3], cameraPlane[idx][:3]])
    # print(plane_points, end = '\n')
    
    # Draw the new plane formed by the three points
    drawPlane(plane_points, ax)
    
    # Find the intersection line with Z = 0
    try:
        # Plane equation: ax + by + cz = d
        p1, p2, p3 = plane_points
        normal = np.cross(p2 - p1, p3 - p1)
        d = np.dot(normal, p1)
        a, b, c = normal
        
        # Intersection with z = 0 plane: cz = 0 -> 0 = ax + by + d
        # Line equation: ax + by = d
        if idx % 2 == 1:
            x_vals = np.linspace(-260, 500, 100)
            y_vals = (d - a * x_vals) / b 
        else:
            y_vals = np.linspace(-140, 140, 100)
            x_vals = (d - b * y_vals) / a
        
        intersection_points = np.vstack([x_vals, y_vals, np.zeros_like(x_vals)]).T
        
        
        
        if idx != 2:
            # Plot the intersection line
            
            drawPlane(np.vstack([centerProjection[0, :3], [x_vals[0], y_vals[0], 0], [x_vals[-1], y_vals[-1], 0]]), ax)
            ax.plot(intersection_points[:, 0], intersection_points[:, 1], intersection_points[:, 2], color= 'green')
    except:
        pass
    if idx == 2: break

# Plot the center projection
ax.scatter(*centerProjection[0, :3], color='green')

# Plot the origin
ax.scatter([0], [0], [0], color='green')

# Plot the line between center projection and origin
ax.plot(*np.vstack([centerProjection[:, :3], [[0, 0, 0]]]).T)

# Draw the Z = 0 plane
drawPlane(points, ax)

# Draw the camera plane
drawPlane(cameraPlane, ax)

# Set labels
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.axis('equal')

plt.show()

