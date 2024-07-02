import numpy as np
import cv2

def SIApproxMapping(frame: np.ndarray, tilt: float, height: float, intrinsicMatrix: np.ndarray) -> np.ndarray:
    """
    Perform a simplified inverse perspective mapping to approximate real-world coordinates from pixel coordinates.

    This function calculates the depth and mapping values for each pixel in an image frame using the intrinsic camera matrix.
    It is particularly useful in computer vision applications where understanding the real-world position of objects in an image is required.

    Parameters
    ----------
    frame : np.ndarray
        The input image frame as a NumPy array.
    tilt : float
        The tilt angle of the camera in radians.
    height : float
        The height of the camera from the ground in the same units as the intrinsic matrix.
    intrinsicMatrix : np.ndarray
        The intrinsic camera matrix as a NumPy array.

    Returns
    -------
    np.ndarray
        Two NumPy arrays representing the X and Y mapping values for each pixel in the frame.

    Examples
    --------
    >>> import numpy as np
    >>> frame = np.random.rand(480, 640, 3)
    >>> tilt = np.radians(30.0)
    >>> height = 1.5
    >>> intrinsicMatrix = np.array([[1000, 0, 320], [0, 1000, 240], [0, 0, 1]])
    >>> xMapper, yMapper = SIApproxMapping(frame, tilt, height, intrinsicMatrix)
    >>> xMapper.shape
    (480, 640)
    >>> yMapper.shape
    (480, 640)
    """
    # Extract frame dimensions
    heightPx, widthPx, _ = frame.shape 
    # Extract focal lengths and principal point coordinates from the intrinsic matrix
    fx, fy, cx, cy = intrinsicMatrix[0, 0], intrinsicMatrix[1, 1], intrinsicMatrix[0, 2], intrinsicMatrix[1, 2] # Cx, Cy is the principal point
    # Rescaling fx, fy
    fx /= (cx * 2 / widthPx)
    fy /= (cy * 2 / heightPx)
    
    # Generate arrays of pixel indices for width and height
    u, v = np.arange(- widthPx // 2, widthPx // 2, 1, dtype = float), np.arange(- heightPx // 2, heightPx // 2, 1, dtype = float)
    # Calculate relative tilt angles for each pixel
    relativeYTilt = np.arctan2(v, fy)
    # Calculate absolute tilt angles by adjusting with the camera tilt
    absYTilt = tilt - relativeYTilt 
    # Compute the depth vector for the center line of the image
    centerDepthVect = height / np.sin(absYTilt)

    # Split the horizontal pixel indices at the center to process left and right halves separately
    halfRightU = u[np.where(u == 0)[0][0] + 1: ]
    halfLeftU = np.abs(u[: np.where(u == 0)[0][0]])
    # Calculate tilt angles for the right and left halves
    halfRightTilt = np.arctan2(halfRightU, fx)
    halfLeftTilt = np.arctan2(halfLeftU, fx)
    # Calculate depth values for the right and left halves using cosine adjustments
    halfRightDepth = centerDepthVect[::-1, np.newaxis] / np.cos(halfRightTilt)
    halfLeftDepth = centerDepthVect[::-1, np.newaxis] / np.cos(halfLeftTilt)
    
    # Combine the depth values from left, center, and right to form the complete depth map
    depth = np.hstack([halfLeftDepth, centerDepthVect[::-1, np.newaxis], halfRightDepth])
    
    
    # Define the center coordinates of the image
    centerX, centerY = widthPx // 2, heightPx - 1
    
    # Calculate the horizontal (X) mapping values from depth
    Xmapper = np.sqrt(depth ** 2 - depth[:, centerX, np.newaxis] ** 2)
    Xmapper[:, :centerX] = - Xmapper[:, :centerX]
    # Handle invalid depth values
    Xmapper = np.where(depth < 0, np.inf, Xmapper)
    
    # Create meshgrid for pixel indices
    u, v = np.meshgrid(u, v[::-1])
    # Calculate distances from image center to all pixels
    imageCenterToALLPixels = np.sqrt(u ** 2 + v ** 2)
    # Calculate distances from projection center to all pixels
    projectionCenterToImagePixels = np.sqrt(np.mean([fx, fy]) ** 2 + imageCenterToALLPixels ** 2)
    
    
    # Calculate distances and differences for vertical (Y) mapping
    c1 = projectionCenterToImagePixels[centerY].astype(float)
    a1 = projectionCenterToImagePixels.astype(float)
    b1 = (v - v[centerY]).astype(float)
    c = depth[centerY]
    a = depth
    # Calculate the vertical (Y) mapping values from depth
    Ymapper = np.sqrt(-(((c1 ** 2 + a1 ** 2 - b1 ** 2) / (2 * a1 * c1)) * 2 * a * c - a ** 2 - c ** 2))
    Ymapper = np.where(depth < 0, np.inf, Ymapper)

    return Xmapper, Ymapper

def centerOfMass(mask: np.ndarray) -> np.ndarray:
    """
    Calculate the center of mass of a binary mask.

    This function computes the center of mass (centroid) of a binary mask using image moments.

    Parameters
    ----------
    mask : np.ndarray
        The input binary mask as a NumPy array.

    Returns
    -------
    np.ndarray
        A NumPy array containing the x and y coordinates of the center of mass.

    Examples
    --------
    >>> import numpy as np
    >>> mask = np.zeros((10, 10), dtype=np.uint8)
    >>> mask[3:7, 3:7] = 1
    >>> center = centerOfMass(mask)
    >>> center
    array([5, 5])
    """
    
    moments = cv2.moments(mask)
    return np.array([moments['m10'] // moments['m00'], moments['m01'] // moments['m00']]).astype(int)

def nearestPoint(origin: np.ndarray, mask: np.ndarray) -> int:
    """
    Calculate the nearest point in a mask to a given origin.

    This function computes the Euclidean distance from the origin to each point in the mask and returns the distance to the nearest point.

    Parameters
    ----------
    origin : np.ndarray
        A NumPy array containing the x and y coordinates of the origin point.
    mask : np.ndarray
        The input mask as a NumPy array of points.

    Returns
    -------
    int
        The Euclidean distance to the nearest point in the mask.

    Examples
    --------
    >>> import numpy as np
    >>> origin = np.array([0, 0])
    >>> mask = np.array([[1, 1], [2, 2], [3, 3]])
                            0       1       2
    >>> nearest = nearestPoint(origin, mask)
    >>> nearest
    1.4142135623730951
    """
    distances = np.sqrt((mask[:, 0] - origin[0]) ** 2 + (mask[:, 1] - origin[1]) ** 2)
    minDist = distances.min()
    return np.where(distances == minDist)[0][0]