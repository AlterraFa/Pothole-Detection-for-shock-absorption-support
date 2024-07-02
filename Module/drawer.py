import cv2
import numpy as np
from ultralytics.engine.results import Boxes


class Drawer:
    def __init__(self, frame: np.ndarray) -> None:
        self.frame = frame 

    def drawBox(self, box: Boxes, dim: tuple[float, float] = (None, None), frame: np.ndarray = None) -> None:
        """
        Draw a bounding box with confidence and dimension annotations on the frame.

        This function draws a bounding box around the detected object, along with the confidence score and dimensions
        (height and width) of the object. The bounding box and text annotations are drawn on the provided frame or the
        default frame if none is provided.

        Parameters
        ----------
        box : Boxes
            The bounding box object containing the coordinates and confidence score.
        dim : tuple of float, optional
            A tuple containing the height and width of the object in centimeters. Default is (None, None).
        frame : np.ndarray, optional
            The image frame on which to draw the bounding box. If not provided, the default frame is used.

        Returns
        -------
        None
        """
        frame = frame if frame is not None else self.frame
        # Extract the coordinates of the bounding box and convert them to integers
        x1, y1, x2, y2 = np.int32(box.xyxy[0].cpu())
        
        # Extract the confidence score and round it to 2 decimal places
        confidence = round(float(box.conf.cpu()[0]), 2)
        
        # Draw the bounding box on the frame
        cv2.rectangle(img = frame, pt1 = (x1, y1), pt2 = (x2, y2), color = (0, 0, 255), thickness = 2)
        
        # Draw a filled rectangle on the overlay for the text background
        cv2.rectangle(frame, (x1, y1 - 35), (x1 + 290, y1), (0, 0, 255), thickness = cv2.FILLED)
        
        # Put the confidence text on the overlay
        cv2.putText(frame, f"Pothole: {confidence}", (x1 + 3, y1 - 20), cv2.FONT_HERSHEY_DUPLEX, .5, (255, 255, 255), 1, cv2.LINE_AA)
            
        # Put the dimensions and area text on the overlay
        cv2.putText(frame, f"Height: {round(dim[0])} (cm), Width: {round(dim[1])} (cm)", (x1 + 3, y1 - 5), cv2.FONT_HERSHEY_DUPLEX, .5, (255, 255, 255), 1, cv2.LINE_AA)
        

    def drawMask(self, mask: np.ndarray, frame: np.ndarray = None) -> None:
        """
        Draw a semi-transparent mask overlay on the frame.

        This function draws a semi-transparent green mask overlay on the provided frame or the default frame if none is
        provided. The mask is filled with green color and polylines are drawn around the mask.

        Parameters
        ----------
        mask : np.ndarray
            The binary mask to be drawn on the frame.
        frame : np.ndarray, optional
            The image frame on which to draw the mask. If not provided, the default frame is used.

        Returns
        -------
        None
        """
        frame = frame if frame is not None else self.frame
        # Set the transparency level for the mask overlay
        alpha = .5
        
        # Create a copy of the frame to use as an overlay
        overlay = frame.copy()
        
        # Fill the area of the mask with green color on the overlay
        cv2.fillPoly(overlay, [mask], (0, 255, 0), cv2.LINE_AA)
        
        # Draw green polylines around the mask on the original frame
        cv2.polylines(img = frame, pts = [mask], isClosed = True, color = (0, 255, 0))
        
        # Blend the overlay with the original frame using the specified transparency level
        cv2.addWeighted(src1 = overlay, alpha = alpha, src2 = frame, beta = 1 - alpha, gamma = 0, dst = frame)
        
        
    def drawDist(self, origin: np.ndarray, targetPoint: np.ndarray, SIlength: float, frame: np.ndarray = None) -> None:
        """
        Draw a distance annotation between two points on the frame.

        This function draws a line between the origin and target point, and annotates the distance (SIlength) between
        the points on the provided frame or the default frame if none is provided. The text annotation is rotated to
        align with the angle of the line.

        Parameters
        ----------
        origin : np.ndarray
            A NumPy array containing the x and y coordinates of the origin point.
        targetPoint : np.ndarray
            A NumPy array containing the x and y coordinates of the target point.
        SIlength : float
            The distance between the origin and target point in centimeters.
        frame : np.ndarray, optional
            The image frame on which to draw the distance annotation. If not provided, the default frame is used.

        Returns
        -------
        None
        """
        # Use the provided frame if available, otherwise use the default frame
        frame = frame if frame is not None else self.frame
        
        # Calculate the differences in x and y coordinates between the origin and target point
        deltaX = origin[0] - targetPoint[0]
        deltaY = origin[1] - targetPoint[1]
        
        # Calculate the angle of the line connecting the origin and target point
        angle = - np.arctan2(deltaY, deltaX) * 180 / np.pi
        
        # Calculate the coordinates for the text annotation
        textX = int((targetPoint[0] + origin[0]) // 2)
        textY = int((targetPoint[1] + origin[1]) // 2 - 15)
        
        # Create a rotation matrix for the text annotation
        M = cv2.getRotationMatrix2D((textX, textY), angle, 1)
        
        # Create a canvas with the text annotation
        canvas = cv2.putText(np.zeros_like(frame), f"{SIlength}", (textX, textY), cv2.FONT_HERSHEY_DUPLEX, .5, (0, 0, 255), 1, cv2.LINE_AA)
        
        # Rotate the text annotation to align with the angle of the line
        rotatedText = cv2.warpAffine(canvas, M, (frame.shape[1], frame.shape[0]))
        
        # If the center point is to the right, rotate the text 180 degrees
        if (targetPoint[0] > origin[0]):
            M = cv2.getRotationMatrix2D((textX, textY), 180, 1)
            rotatedText = cv2.warpAffine(rotatedText, M, (frame.shape[1], frame.shape[0]))
        
        # Draw a line between the origin and target point on the frame
        cv2.line(frame, (targetPoint[0], targetPoint[1]), (origin[0], origin[1]), (255, 0, 0), 2, cv2.LINE_AA)
        
        # Create a mask for the text and overlay it on the frame
        textMask = cv2.cvtColor(rotatedText, cv2.COLOR_BGR2GRAY) > 0
        frame[:] = np.where(np.dstack([textMask] * 3) == 1, rotatedText, frame)
