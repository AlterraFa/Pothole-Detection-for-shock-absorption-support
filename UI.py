import cv2
import time

import numpy as np

from Module.calculation import *
from Module.drawer import Drawer
from scipy.io  import matlab

from ultralytics import YOLO

import sys
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QImage, QPixmap, QIcon
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget, QFileDialog, QLineEdit, QComboBox, QStackedWidget, QFrame, QSlider, QTableWidget, QScrollArea


class video_Capture(QMainWindow): # Get all library from QMainWindow library
    def __init__(self, main_Path, window_Resolution, window_Scale = 1, fraction = (1, 1)):
        super().__init__() 

        self.main_Path = main_Path
        self.icon_image_Path = fr"{self.main_Path}Icon"
        self.matlab_Path = fr"{self.main_Path}Resources/CameraIntrinsic.mat"
        self.model_Path = fr"{self.main_Path}Train/Pothole_Detector/Cook_Station_3/weights/best.pt"
        
        # Initialize AI 
        self.model = YOLO(self.model_Path, task = 'segment')

        # Getting camera internal parameters
        mat = matlab.loadmat(self.matlab_Path)
        self.intrinsicMatrix = mat["IntrinsicMatrix"].T

        # Create window
        self.setWindowTitle("Pothole Detection") # Name of window
        self.setGeometry(100, 100, window_Resolution[0] , window_Resolution[1] )# Resolution of window
        
        # Initial mode
        self.current_Mode = "Video Mode"
        self.length_List = []
        self.fraction = fraction 
        self.window_Scale = window_Scale
        self.window_Resolution = window_Resolution
        
        self.UI_setup()

    def UI_setup(self):
        ## Setup main layout
        
        self.central_widget = QWidget(self) # central_widget: name
        self.setCentralWidget(self.central_widget)

        ## Create element
        # Button to start and restart the video/capture devic_s
        self.button_Start = QPushButton(self)
        self.button_Start.clicked.connect(self.BUTTON_start_Video)
        self.button_Start.setEnabled(False)
        self.first_Initialize_Video = False # For checking if it is the first time video is started
        self.first_Initialize_Camera = False # For checking if it is the first time the camera is started
        self.STATE_button_Start = "Start"
        self.ICON_start = QIcon(fr"{self.icon_image_Path}/ICON_start.png")
        self.ICON_restart = QIcon(fr"{self.icon_image_Path}/ICON_restart.png")
        self.button_Start.setIcon(self.ICON_start)
        self.button_Start.setText(self.STATE_button_Start)
        self.change_Font_Properties(self.button_Start, 13 * self.window_Scale, False)
        self.button_Start.setStyleSheet("""
                                                QPushButton 
                                                {
                                                    background-color:#3c3c3c; 
                                                    border-radius: 5px;
                                                }
                                            """)
        
        # button to play/pause video capture
        self.button_Play = QPushButton('Pause', self)
        self.button_Play.clicked.connect(self.BUTTON_toggle_video)    
        self.ICON_pause = QIcon(fr"{self.icon_image_Path}/ICON_pause.png")
        self.button_Play.setIcon(self.ICON_pause)
        self.change_Font_Properties(self.button_Play, int(13 * self.window_Scale), False)
        self.STATE_play_Pause = "Pause"
        self.button_Play.setEnabled(False)  
        self.button_Play.setStyleSheet("""
                                                QPushButton 
                                                {
                                                    background-color:#3c3c3c; 
                                                    border-radius: 5px;
                                                }
                                            """)

        # Select mode button
        self.button_selectMode = QPushButton(self)
        self.button_selectMode.clicked.connect(self.BUTTON_toggle_mode)
        self.ICON_selectMode_Video = QIcon(fr"{self.icon_image_Path}/ICON_mode_Video.png")
        self.ICON_selectMode_Camera = QIcon(fr"{self.icon_image_Path}/ICON_mode_Camera.png")
        self.change_Font_Properties(self.button_selectMode, int(13 * self.window_Scale), False)
        self.button_selectMode.setStyleSheet("""
                                                QPushButton 
                                                {
                                                    text-align: center;
                                                    padding-bottom: 4px;
                                                    background-color:#19386e; 
                                                    border-radius: 5px;
                                                }
                                                QPushButton:hover
                                                {
                                                    background-color: #142a52;
                                                    border-radius: 5px;
                                                }
                                            """)
        self.button_selectMode.setText(self.current_Mode)
        self.button_selectMode.setIcon(self.ICON_selectMode_Video)

        # Speed down button
        self.button_speedDown = QPushButton("Speed", self)
        self.button_speedDown.clicked.connect(self.BUTTON_toggle_speedDown)
        self.ICON_speedDown = QIcon(fr"{self.icon_image_Path}/ICON_speedDown.png")
        self.change_Font_Properties(self.button_speedDown, int(10 * self.window_Scale), False)
        self.button_speedDown.setIcon(self.ICON_speedDown)
        self.button_speedDown.setEnabled(False)
        self.button_speedDown.setStyleSheet("""
                                                QPushButton 
                                                {
                                                    background-color:#3c3c3c; 
                                                    border-radius: 5px;
                                                }
                                            """)

        # Speed up button
        self.button_speedUp = QPushButton("Speed", self)
        self.button_speedUp.clicked.connect(self.BUTTON_toggle_speedUp)
        self.ICON_speedUp = QIcon(fr"{self.icon_image_Path}/ICON_speedUp.png")
        self.change_Font_Properties(self.button_speedUp, int(10 * self.window_Scale), False)
        self.button_speedUp.setIcon(self.ICON_speedUp)
        self.button_speedUp.setEnabled(False)
        self.button_speedUp.setStyleSheet("""
                                                QPushButton 
                                                {
                                                    background-color:#3c3c3c; 
                                                    border-radius: 5px;
                                                }
                                            """)

        # Return speed button
        self.button_speedInitial = QPushButton("Return speed", self)
        self.button_speedInitial.clicked.connect(self.BUTTON_toggle_speedIni)
        self.change_Font_Properties(self.button_speedInitial, int(10 * self.window_Scale), False)
        self.button_speedInitial.setEnabled(False)
        self.button_speedInitial.setStyleSheet("""
                                                QPushButton 
                                                {
                                                    background-color:#3c3c3c; 
                                                    border-radius: 5px;
                                                }
                                            """)


        # Speed display box
        self.current_Speed = QLineEdit(self)
        self.current_Speed.setText("0")
        self.change_Font_Properties(self.current_Speed, int(8 * self.window_Scale), False)
        self.current_Speed.setEnabled(False)

        # Quit window button
        self.button_Quit = QPushButton('Quit', self)
        self.button_Quit.clicked.connect(QApplication.instance().quit)
        self.ICON_Quit = QIcon(fr"{self.icon_image_Path}/ICON_quit.png")
        self.change_Font_Properties(self.button_Quit, int(13 * self.window_Scale), True)
        self.button_Quit.setStyleSheet("""
                                                QPushButton 
                                                {
                                                    text-align: center;
                                                    padding-bottom: 4px;
                                                    background-color:#9c1f1f; 
                                                    border-radius: 5px;

                                                }
                                                QPushButton:hover
                                                {
                                                    background-color: #701515;
                                                    border-radius: 5px;

                                                }
                                            """)
        self.button_Quit.setIcon(self.ICON_Quit)

        # MODE-Video: add a text box and a browser button to add video path
        # text box
        self.path_Input = QLineEdit(self)
        self.path_Input.setPlaceholderText("Enter path to video")
        self.path_Input.textChanged.connect(self.check_Input)
        self.change_Font_Properties(self.path_Input, 10 * self.window_Scale, False)

        # browser button
        self.button_Browser =  QPushButton("Browse", self)
        self.button_Browser.clicked.connect(self.file_Manager)
        self.ICON_fileManager = QIcon(fr"{self.icon_image_Path}/ICON_browser.png")
        self.change_Font_Properties(self.button_Browser, 10 * self.window_Scale, False)
        self.button_Browser.setStyleSheet("""
                                                QPushButton 
                                                {
                                                    text-align: center;
                                                    padding-bottom: 4px;
                                                    background-color:#4f3a34; 
                                                    border-radius: 5px;
                                                }
                                                QPushButton:hover
                                                {
                                                    background-color: #382a26;
                                                    border-radius: 5px;
                                                }
                                            """)
        self.button_Browser.setIcon(self.ICON_fileManager)

        # Text box for input 3 parameter of the camera
        self.AI_Parameters = QPushButton(self)
        self.AI_Parameters.clicked.connect(self.BUTTON_toggle_change_camera_Parameters)
        self.ICON_camera_Parameters_Show = QIcon(fr"{self.icon_image_Path}/ICON_camera_Parameter_Show.png")
        self.ICON_AI_parameters = QIcon(fr"{self.icon_image_Path}/ICON_AI_Parameters.png")
        self.AI_Parameters.setIcon(self.ICON_AI_parameters)
        self.change_Font_Properties(self.AI_Parameters, 14 * self.window_Scale, bold=False)
        self.STATE_camera_Parameters = "Camera Parameters"
        self.AI_Parameters.setText(self.STATE_camera_Parameters)
        self.AI_Parameters.setEnabled(False)
        self.AI_Parameters.setStyleSheet("""
                                                QPushButton 
                                                {
                                                    text-align: center;
                                                    padding-bottom: 2px;
                                                    background-color:#19386e; 
                                                    border-radius: 5px;
                                                }
                                                QPushButton:hover
                                                {
                                                    background-color: #142a52;
                                                    border-radius:5px;
                                                }
                                            """)

        self.input_fx = QLabel(self)
        self.change_Font_Properties(self.input_fx, 13 * self.window_Scale, bold=False)
        self.input_fx.setText(f"fx= {str(round(self.intrinsicMatrix[0][0],2))}")
        self.input_fx.hide()
        
        self.input_fy = QLabel(self)
        self.change_Font_Properties(self.input_fy, 13 * self.window_Scale, bold=False)
        self.input_fy.setText(f"fy= {str(round(self.intrinsicMatrix[1][1],2))}")
        self.input_fy.hide()
        
        self.input_cx = QLabel(self)
        self.change_Font_Properties(self.input_cx, 13 * self.window_Scale, bold=False)
        self.input_cx.setText(f"cx= {str(round(self.intrinsicMatrix[0][2],2))}")
        self.input_cx.hide()

        self.input_cy = QLabel(self)
        self.change_Font_Properties(self.input_cy, 13 * self.window_Scale, bold=False)
        self.input_cy.setText(f"cy= {str(round(self.intrinsicMatrix[1][2],2))}")
        self.input_cy.hide()

        # MODE-Capture: add a box contain all available capture devices
        self.capture_Devices = QComboBox(self)
        self.capture_Devices.hide()
        self.find_capture_Devices()
        self.capture_Devices.currentIndexChanged.connect(self.check_Input)
        self.change_Font_Properties(self.capture_Devices, 10 * self.window_Scale, False)

        # Button turn on and off UI
        self.button_AI = QPushButton("Stop detection", self)
        self.button_AI.clicked.connect(self.BUTTON_toggle_AI)
        self.STATE_AI = "Stop detection"
        self.ICON_AI = QIcon(fr"{self.icon_image_Path}/ICON_AI.png")
        self.button_AI.setIcon(self.ICON_AI)
        self.button_AI.setEnabled(False)
        self.button_AI.setStyleSheet("""
                                        QPushButton 
                                        {
                                            background-color:#3c3c3c; 
                                            border-radius: 5px;
                                        }
                                    """)
        self.change_Font_Properties(self.button_AI, 13 * self.window_Scale, bold=False)
     

        # Button change detect mode from nearest to center of potholes
        self.button_detectMode = QPushButton(self) 
        self.button_detectMode.clicked.connect(self.BUTTON_toggle_detectMode)
        self.STATE_detectMode = "Center of\npothole"
        self.button_detectMode.setText(self.STATE_detectMode)
        self.change_Font_Properties(self.button_detectMode, 10 * self.window_Scale, bold=False)
        self.button_detectMode.setEnabled(False)

        # Horizontal slider for confidence level
        self.horiSli_ConfidenceThreshold = QSlider(Qt.Orientation.Horizontal, self)
        self.horiSli_ConfidenceThreshold.setMinimum(1)
        self.horiSli_ConfidenceThreshold.setMaximum(100)
        self.horiSli_ConfidenceThreshold.setValue(20)
        self.horiSli_ConfidenceThreshold.setTickPosition(QSlider.TickPosition.TicksBothSides)
        self.horiSli_ConfidenceThreshold.setTickInterval(1)
        self.horiSli_ConfidenceThreshold.valueChanged.connect(self.SLIDER_confidence)
        self.current_Threshold = self.horiSli_ConfidenceThreshold.value()
        self.horiSli_ConfidenceThreshold.setEnabled(False)

        self.label_ConfidenceThreshold = QLabel("Confidence threshold:",self)
        self.change_Font_Properties(self.label_ConfidenceThreshold, 11 * self.window_Scale, bold=False)
        self.label_ConfidenceThreshold.setEnabled(False)

        self.text_ConfidenceThreshold = QLineEdit("20", self)
        self.change_Font_Properties(self.text_ConfidenceThreshold, 9 * self.window_Scale, bold=False)
        self.text_ConfidenceThreshold.setEnabled(False)

        ## Create a table layout for 3 output log
        self.table_Layout = QTableWidget(3,3, self)
        
        self.table_Layout.verticalHeader().hide()
        self.table_Layout.horizontalHeader().hide()

        self.table_Layout.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table_Layout.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        

        self.table_Layout.setShowGrid(True)


        # Create 2x2 table and merge the first row
        self.table_Layout.setSpan(0,0,2,1) # Span 2 row from column 1, row 1 -> 2
        self.table_Layout.setSpan(0,1,1,2) # span 2 column from row 1, col 2-> 3

        self.table_Layout.setColumnWidth(0, int(97 * self.window_Scale))
        self.table_Layout.setColumnWidth(1, int(97 * self.window_Scale))
        self.table_Layout.setColumnWidth(2, int(97 * self.window_Scale))

        self.table_Layout.setRowHeight(0, int(50 * self.window_Scale))
        self.table_Layout.setRowHeight(1, int(50 * self.window_Scale))
        self.table_Layout.setRowHeight(2, int(300 * self.window_Scale))

        # Row 1, column 1
        self.table_Label_Row1_Col1 = QLabel("Length from camera to pothole (cm)", self)
        self.change_Font_Properties(self.table_Label_Row1_Col1, 12 * self.window_Scale, bold=False)
        self.table_Label_Row1_Col1.setWordWrap(True)

        self.table_Layout.setCellWidget(0,0, self.table_Label_Row1_Col1)
        
        # Row 1, column 2-3
        self.table_Label_Row1_Col23 = QLabel("Pothole's Dimensions", self)
        self.change_Font_Properties(self.table_Label_Row1_Col23, 12 * self.window_Scale, bold=False)
        self.table_Label_Row1_Col23.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.table_Layout.setCellWidget(0,1, self.table_Label_Row1_Col23)

        # Row 2, column 2
        self.table_Label_Row2_Col2 = QLabel("Width (cm)", self)
        self.change_Font_Properties(self.table_Label_Row2_Col2, 10 * self.window_Scale, bold=False)
        self.table_Label_Row2_Col2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.table_Layout.setCellWidget(1,1, self.table_Label_Row2_Col2)

        # Row 2, column 3
        self.table_Label_Row2_Col3 = QLabel("Height (cm)", self)
        self.change_Font_Properties(self.table_Label_Row2_Col3, 10 * self.window_Scale, bold=False)
        self.table_Label_Row2_Col3.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table_Layout.setCellWidget(1,2, self.table_Label_Row2_Col3)
        
        # Row 3, column 1 
        self.scroll_Row3_Col1_Widget = QWidget()
        self.scroll_Row3_Col1_Layout = QVBoxLayout(self.scroll_Row3_Col1_Widget)
        

        self.scroll_Row3_Col1 = QScrollArea()
        self.scroll_Row3_Col1.setWidgetResizable(True)   
        self.scroll_Row3_Col1.setWidget(self.scroll_Row3_Col1_Widget)

        self.table_Layout.setCellWidget(2,0, self.scroll_Row3_Col1)
   
        # # Row 3, column 2
        self.scroll_Row3_Col2_Widget = QWidget()
        self.scroll_Row3_Col2_Layout = QVBoxLayout(self.scroll_Row3_Col2_Widget)
        

        self.scroll_Row3_Col2 = QScrollArea()
        self.scroll_Row3_Col2.setWidgetResizable(True)   
        self.scroll_Row3_Col2.setWidget(self.scroll_Row3_Col2_Widget)

        self.table_Layout.setCellWidget(2,1, self.scroll_Row3_Col2)

        # # Row 3, Column 3
        self.scroll_Row3_Col3_Widget = QWidget()
        self.scroll_Row3_Col3_Layout = QVBoxLayout(self.scroll_Row3_Col3_Widget)
        

        self.scroll_Row3_Col3 = QScrollArea()
        self.scroll_Row3_Col3.setWidgetResizable(True)   
        self.scroll_Row3_Col3.setWidget(self.scroll_Row3_Col3_Widget)

        self.table_Layout.setCellWidget(2,2, self.scroll_Row3_Col3)

        # Row 3 Col 4

        # ------------- Table style

        self.table_Layout.setStyleSheet("""
                                            QTableWidget{
                                                background-color: transparent; /* Ensures the table background is transparent */
                                                border: 0px; /* Removes the border around the table */
                                                gridline-color: white;
                                            }
                                            QTableWidget::item {
                                                background-color: transparent; /* Ensures cell background is transparent */
                                                border: 0px; /* Removes borders around individual cells */
                                            }
                                        """)



        #  --------------------Add element layout

        self.button_selectMode.setGeometry(int(360 * self.window_Scale), int(10 * self.window_Scale), int(200 * self.window_Scale), int(50 * self.window_Scale))
        self.button_Browser.setGeometry(int(567 * self.window_Scale), int(20 * self.window_Scale), int(80 * self.window_Scale), int(30 * self.window_Scale))
        self.path_Input.setGeometry(int(655 * self.window_Scale), int(10 * self.window_Scale), int(400 * self.window_Scale), int(50 * self.window_Scale))
        self.capture_Devices.setGeometry(int(567 * self.window_Scale), int(10 * self.window_Scale), int(200 * self.window_Scale), int(50 * self.window_Scale))

        self.button_Quit.setGeometry(int(self.width() -110 * self.window_Scale), int(10 * self.window_Scale), int(100 * self.window_Scale), int(50 * self.window_Scale)) 
        # self.button_fullScreen.setGeometry(self.width()-230, 10, 100, 50)

        self.AI_Parameters.setGeometry(int(35 * self.window_Scale), int(10 * self.window_Scale), int(230 * self.window_Scale), int(40 * self.window_Scale))

        self.input_fx.setGeometry(int(60 * self.window_Scale), int(50 * self.window_Scale), int(100 * self.window_Scale), int(30 * self.window_Scale))
        self.input_fy.setGeometry(int(60 * self.window_Scale), int(75 * self.window_Scale), int(100 * self.window_Scale), int(20 * self.window_Scale))

        self.input_cx.setGeometry(int(165* self.window_Scale), int(50 * self.window_Scale), int(100 * self.window_Scale), int(30 * self.window_Scale))
        self.input_cy.setGeometry(int(165 * self.window_Scale), int(75 * self.window_Scale), int(100 * self.window_Scale), int(20 * self.window_Scale))

        self.label_ConfidenceThreshold.setGeometry(int(55 * self.window_Scale), int(40 * self.window_Scale), int(300 * self.window_Scale), int(50 * self.window_Scale))
        self.text_ConfidenceThreshold.setGeometry(int(205 * self.window_Scale), int(55 * self.window_Scale), int(38 * self.window_Scale), int(20 * self.window_Scale))
        self.horiSli_ConfidenceThreshold.setGeometry(int(10 * self.window_Scale), int(75 * self.window_Scale), int(290 * self.window_Scale), int(60 * self.window_Scale))


        
        self.button_Start.setGeometry(int(368 * self.window_Scale), int(70 * self.window_Scale), int(90 * self.window_Scale), int(40 * self.window_Scale))
        self.button_Play.setGeometry(int(463 * self.window_Scale), int(70 * self.window_Scale), int(90 * self.window_Scale), int(40 * self.window_Scale))

        self.button_speedUp.setGeometry(int(565 * self.window_Scale), int(66 * self.window_Scale), int(87 * self.window_Scale), int(25 * self.window_Scale))
        self.button_speedDown.setGeometry(int(565 * self.window_Scale), int(93 * self.window_Scale), int(87 * self.window_Scale), int(25 * self.window_Scale))
        self.current_Speed.setGeometry(int(655 * self.window_Scale), int(80 * self.window_Scale), int(30 * self.window_Scale), int(20 * self.window_Scale))
        self.button_speedInitial.setGeometry(int(687 * self.window_Scale), int(76* self.window_Scale), int(87 * self.window_Scale), int(25 * self.window_Scale))

        self.button_AI.setGeometry(int(20 * self.window_Scale), int(155 * self.window_Scale), int(150 * self.window_Scale), int(40 * self.window_Scale))
        self.button_detectMode.setGeometry(int(180 * self.window_Scale), int(155 * self.window_Scale), int(110 * self.window_Scale), int(40 * self.window_Scale))
    
        self.table_Layout.setGeometry(int(10 * self.window_Scale), int(215 * self.window_Scale), int(285 * self.window_Scale), int(400 * self.window_Scale))

        # Add video layout
        self.label = QLabel(self)
        self.label_StyleSheet = ("""
                                    border: 5px solid #707070;  
                                    border-radius: 10px 
                                """)       
        self.label.setGeometry(int(305 * self.window_Scale), int(125 * self.window_Scale), 1280, 720 )
        
    def initialize_Video(self, path_mode):
        # Initialize video capture from path
        self.cap = cv2.VideoCapture(path_mode)

        # Get frame rate 
        self.frame_Period =  33 # =30hz = 30frame/second

        # Read each frame of video
        _, frame = self.cap.read()

        ## Change video size 
        # Proportion variable
        fractionw, fractionh = self.fraction 

        self.useNearest = False
        # Get properties each frame of video
        h, w, self.ch = frame.shape
        
        # Change video size by changing each frame proportion
        self.resizedh = int(h * fractionh)
        self.resizedw = int(w * fractionw)

        frame = cv2.resize(frame, (self.resizedw, self.resizedh))
        self.xMapper, self.yMapper = SIApproxMapping(frame, tilt = 16 * np.pi / 180, height = 110, intrinsicMatrix = self.intrinsicMatrix)


        # Setup timer for counting frame
        self.frame_Timer = time.time()
        self.REAL_frame_Cnt = 0
        self.REAL_frame_Max = 0

        # Setup timer for capture video frames
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame) # Turn on function if timeout occur

        self.timer.start(self.frame_Period) # Capture a frame every frame_Period (ms)
        self.label.resize(self.resizedw, self.resizedh) 
        
        self.label.setStyleSheet(self.label_StyleSheet)

        # Turn on video running flag
        self.is_running = True

        self.button_AI.setEnabled(True)
        self.button_AI.setStyleSheet("""
                                                QPushButton 
                                                {
                                                    text-align: center;
                                                    padding-bottom: 2px;
                                                    background-color:#b87f3b; 
                                                    border-radius: 5px;
                                                }
                                                QPushButton:hover
                                                {
                                                    background-color: #915a19;
                                                    border-radius: 5px;
                                                }
                                            """)
        self.button_detectMode.setEnabled(True)

        

    def update_frame(self): 
        # Read a frame from the video capture
        ret, frame = self.cap.read()
        
        # Check if one second has passed since the last frame timer reset
        if time.time() - self.frame_Timer >= 1:
            # Update the current speed display with the real frame count
            self.current_Speed.setText(str(self.REAL_frame_Cnt))
            # Store the maximum frame count for the last second
            self.REAL_frame_Max = self.REAL_frame_Cnt
            # Reset the frame timer to the current time
            self.frame_Timer = time.time()
            # Reset the real frame count to zero
            self.REAL_frame_Cnt = 0

        # Assign the x and y mappers to local variables
        xMapper = self.xMapper
        yMapper = self.yMapper
        
        self.REAL_frame_Cnt += 1
        if ret: 
            # Resize the frame to the specified width and height
            frame = cv2.resize(frame, (self.resizedw, self.resizedh))
            # Define the origin point at the bottom center of the frame
            origin = np.array([frame.shape[1] // 2, frame.shape[0] - 1]) 
            # Create a Drawer object to draw on the frame
            drawer = Drawer(frame)
            
            # Check if AI detection is enabled
            if self.STATE_AI == "Stop detection":
                # Perform model prediction on the frame
                result = self.model.predict(frame,
                                            verbose = False, 
                                            nms = True, 
                                            half = True, 
                                            conf = self.current_Threshold / 100,
                                            device = 'cuda')[0]
                
                # Extract bounding boxes and masks from the prediction result
                boxes = result.boxes
                masks = result.masks    
                                
                # Clear previous layouts if there are any detected boxes
                if len(boxes) != 0:
                    self.clear_Layout(self.scroll_Row3_Col1_Layout)
                    self.clear_Layout(self.scroll_Row3_Col2_Layout)
                    self.clear_Layout(self.scroll_Row3_Col3_Layout)



                # Iterate through each detected box
                for idx, box in enumerate(boxes):
                    if masks:
                        # Retrieve the mask for the current index
                        mask = masks[idx]
                        # Convert mask coordinates to integer and adjust y-coordinates
                        convertMask = np.int32(mask.xy[0]) # mask.xy is a 3D array
                        
                        # Extract x and y coordinates from the mask
                        x_coords = convertMask[:, 0]
                        y_coords = convertMask[:, 1]
                        
                        # Clip coordinates to be within the frame boundaries
                        x_coords = np.clip(x_coords, 0, frame.shape[1] - 1)
                        y_coords = np.clip(y_coords, 0, frame.shape[0] - 1)
                        xMapper[0, 0]

                        # Map the mask coordinates to real-world coordinates
                        maskSI = np.array([xMapper[y_coords, x_coords], yMapper[y_coords, x_coords]]).T
                        originSI = np.array([xMapper[origin[1], origin[0]], yMapper[origin[1], origin[0]]])
                        
                        # Determine the target point based on the nearest point or center of mass
                        if self.useNearest:
                            nearIdx = nearestPoint(originSI, maskSI)
                            Cx = x_coords[nearIdx]
                            Cy = y_coords[nearIdx]
                        else:
                            center = centerOfMass(convertMask)
                            Cx = center[0]
                            Cy = center[1]
                        
                        targetPoint = np.array([Cx, Cy])            
                        
                        # Calculate the length from the center to the bottom center using real-world coordinates
                        length = round(np.sqrt(xMapper[Cy, Cx] ** 2 + yMapper[Cy, Cx] ** 2), 2)

                        # Calculate bounding box coordinates in real-world scale
                        xmax = x_coords.max()
                        xmin = x_coords.min()
                        ymax = y_coords.max()
                        ymin = y_coords.min()
                        
                        Ymax = yMapper[ymax, (xmax + xmin) // 2]
                        Ymin = yMapper[ymin, (xmin + xmax) // 2]
                        Xmax = xMapper[(ymax + ymin) // 2, xmax]
                        Xmin = xMapper[(ymin + ymax) // 2, xmin]
                        
                        # Draw distance, bounding box, and mask on the frame
                        try:
                            drawer.drawDist(origin, targetPoint, length)
                            drawer.drawBox(box, (Ymin - Ymax, Xmax - Xmin))
                            drawer.drawMask(convertMask)
                        except:...
                    else:
                        # Draw only the bounding box if no mask is available
                        drawer.drawBox(box) 
                    
                        # Adding into table                    
                    self.table_Output_Row3_Col1 = QLabel(str(round(length, 2)), self)
                    self.table_Output_Row3_Col2 = QLabel(str(round(Xmax - Xmin, 2)), self)
                    self.table_Output_Row3_Col3 = QLabel(str(round(Ymin - Ymax, 2 )), self)

                    self.change_Font_Properties(self.table_Output_Row3_Col1, 12 * self.window_Scale, bold= False)
                    self.change_Font_Properties(self.table_Output_Row3_Col2, 12 * self.window_Scale, bold= False)
                    self.change_Font_Properties(self.table_Output_Row3_Col3, 12 * self.window_Scale, bold= False)

                    self.scroll_Row3_Col1_Layout.addWidget(self.table_Output_Row3_Col1)
                    self.scroll_Row3_Col2_Layout.addWidget(self.table_Output_Row3_Col2)
                    self.scroll_Row3_Col3_Layout.addWidget(self.table_Output_Row3_Col3)

                    self.scroll_Row3_Col1_Layout.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
                    self.scroll_Row3_Col2_Layout.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
                    self.scroll_Row3_Col3_Layout.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            bytes_per_line = self.ch * self.resizedw
            q_img = QImage(rgb_frame.data, self.resizedw, self.resizedh, bytes_per_line, QImage.Format.Format_RGB888)
            
            self.label.setStyleSheet(self.label_StyleSheet)
            self.label.setPixmap(QPixmap.fromImage(q_img))

    @staticmethod
    def clear_Layout(layout):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()
    
    def BUTTON_toggle_AI(self):
        if self.STATE_AI == "Start detection":
            self.STATE_AI = "Stop detection"
        else:
            self.STATE_AI = "Start detection"
        
        self.button_AI.setText(self.STATE_AI)

    def BUTTON_toggle_detectMode(self):
        if self.STATE_detectMode == "Center of\npothole":
            self.STATE_detectMode = "Nearest pothole"
            self.useNearest = True
        else: 
            self.STATE_detectMode = "Center of\npothole"
            self.useNearest = False
        self.button_detectMode.setText(self.STATE_detectMode)
            
    def BUTTON_start_Video(self):
        if self.current_Mode == "Video Mode" and self.path_Input.text() and not self.first_Initialize_Video:
            self.initialize_Video(self.path_Input.text())
            self.STATE_button_Start= "Restart"
            self.button_Start.setStyleSheet("""
                                                QPushButton 
                                                {
                                                    text-align: center;
                                                    padding-bottom: 4px;
                                                    background-color:#9e9644; 
                                                    border-radius: 5px;
                                                }
                                                QPushButton:hover
                                                {
                                                    background-color: #827b38;
                                                    border-radius: 5px;
                                                }
                                            """)
            self.button_Play.setEnabled(True)
            self.button_Play.setStyleSheet("""
                                                QPushButton 
                                                {
                                                    text-align: center;
                                                    padding-bottom: 4px;
                                                    background-color:#262626; 
                                                    border-radius: 5px;
                                                }
                                                QPushButton:hover
                                                {
                                                    background-color: #1a1a1a;
                                                    border-radius: 5px;
                                                }
                                            """)
            self.button_Start.setIcon(self.ICON_restart)
            self.first_Initialize_Video = True
            self.first_Initialize_Camera = False
            self.BUTTON_toggle_video()

        elif self.current_Mode == "Capture Mode" and self.capture_Devices.currentIndex() != -1 and not self.first_Initialize_Camera:
            self.initialize_Video(self.capture_Devices.currentData())
            self.STATE_button_Start = "Restart"
            self.button_Start.setStyleSheet("""
                                                QPushButton 
                                                {
                                                    text-align: center;
                                                    padding-bottom: 4px;
                                                    background-color:#9e9644; 
                                                    border-radius: 5px; 
                                                }
                                                QPushButton:hover
                                                {
                                                    background-color: #827b38;
                                                    border-radius: 5px;
                                                }
                                            """)
            self.button_Play.setEnabled(True)
            self.button_Play.setStyleSheet("""
                                                QPushButton 
                                                {
                                                    text-align: center;
                                                    padding-bottom: 4px;
                                                    background-color:#262626; 
                                                    border-radius: 5px;
                                                }
                                                QPushButton:hover
                                                {
                                                    background-color: #1a1a1a;
                                                    border-radius: 5px;
                                                }
                                            """)

            self.button_Start.setIcon(self.ICON_restart)
            self.first_Initialize_Camera = True
            self.first_Initialize_Video = False
            self.BUTTON_toggle_video()

        elif self.first_Initialize_Video and not self.first_Initialize_Camera:
            self.timer.stop()
            self.initialize_Video(self.path_Input.text())
            self.BUTTON_toggle_video()

        elif not self.first_Initialize_Video and self.first_Initialize_Camera:
            self.timer.stop()
            self.initialize_Video(self.capture_Devices.currentData())
            self.BUTTON_toggle_video()

        self.frame_Period = 33
        self.frame_Rate = int(1000/self.frame_Period)

        self.current_Speed.setText(str(self.frame_Rate))
        self.button_Start.setText(self.STATE_button_Start)

    def BUTTON_toggle_video(self):
        if self.is_running:
            self.timer.stop()
            self.STATE_play_Pause = "Play"
            self.button_Play.setText(self.STATE_play_Pause)
            self.button_Play.setStyleSheet("""
                                                QPushButton 
                                                {
                                                    text-align: center;
                                                    padding-bottom: 4px;
                                                    background-color:#442D60; 
                                                    border-radius: 5px;
                                                }
                                                QPushButton:hover
                                                {
                                                    background-color: #2f1e42;
                                                    border-radius: 5px;
                                                }
                                            """)
            self.ICON_play = QIcon(fr"{self.icon_image_Path}/ICON_play.png")
            self.button_Play.setIcon(self.ICON_play)
        
        else:
            self.timer.start(self.frame_Period)
            self.STATE_play_Pause = "Pause"
            self.button_Play.setText(self.STATE_play_Pause)
            self.button_Play.setStyleSheet("""
                                                QPushButton 
                                                {
                                                    text-align: center;
                                                    padding-bottom: 4px;
                                                    background-color:#262626; 
                                                    border-radius: 5px;
                                                }
                                                QPushButton:hover
                                                {
                                                    background-color: #1a1a1a;
                                                    border-radius: 5px;
                                                }
                                            """)
            self.button_Play.setIcon(self.ICON_pause)
        
        self.is_running = not self.is_running

            
    def BUTTON_toggle_mode(self):
        if self.current_Mode== 'Video Mode':
            self.current_Mode="Capture Mode"
            self.button_selectMode.setIcon(self.ICON_selectMode_Camera)
            self.path_Input.hide()
            self.button_Browser.hide()
            self.capture_Devices.show()
        else :
            self.current_Mode= 'Video Mode'
            self.button_selectMode.setIcon(self.ICON_selectMode_Video)
            self.path_Input.show()
            self.button_Browser.show()
            self.capture_Devices.hide()

        if self.STATE_button_Start=="Restart" and self.first_Initialize_Camera and not self.first_Initialize_Video:
            self.STATE_button_Start = "Start"
            self.button_Start.setIcon(self.ICON_start)

        elif self.STATE_button_Start=="Restart" and not self.first_Initialize_Camera and self.first_Initialize_Video:
            self.STATE_button_Start = "Start"
            self.button_Start.setIcon(self.ICON_start)

        self.button_Start.setText(self.STATE_button_Start)
        self.button_selectMode.setText(self.current_Mode)
        self.check_Input()

    def BUTTON_toggle_speedDown(self):
        if self.is_running:
            cal_Frame = max(self.REAL_frame_Max - 10, 1) # Adjusting current frame rate -> the smaller -> bigger period -> the less image frame per sec
            self.current_Speed.setText(str(cal_Frame)) # print out calculate frame rate
            self.frame_Period = int(1/(cal_Frame*10**(-3)))
            self.timer.start(self.frame_Period)
        
    def BUTTON_toggle_speedUp(self):
        if self.is_running:
            cal_Frame = min(self.REAL_frame_Max +10, 70)   # Adjusting current frame rate -> the larger -> smaller period -> the more image frame per sec
            self.current_Speed.setText(str(cal_Frame))
            self.frame_Period = int(1/(cal_Frame*10**(-3)))
            self.timer.start(self.frame_Period)
        
    def BUTTON_toggle_speedIni(self):
        if self.is_running:
            self.frame_Period = 33
            self.frame_Rate = int(1000/self.frame_Period)

            self.current_Speed.setText(str(self.frame_Rate))
            self.timer.start(self.frame_Period)

    
    def BUTTON_toggle_change_camera_Parameters(self):
        if self.STATE_camera_Parameters == "Confidence Threshold":
            self.horiSli_ConfidenceThreshold.show()
            self.label_ConfidenceThreshold.show()
            self.text_ConfidenceThreshold.show()

            self.input_fx.hide()
            self.input_fy.hide()

            self.input_cx.hide()
            self.input_cy.hide()

            self.STATE_camera_Parameters = "Camera Parameters"
        
        else:
            self.horiSli_ConfidenceThreshold.hide()
            self.label_ConfidenceThreshold.hide()
            self.text_ConfidenceThreshold.hide()

            self.input_fx.show()
            self.input_fy.show()

            self.input_cx.show()
            self.input_cy.show()


            self.AI_Parameters.setIcon(self.ICON_AI_parameters)
            self.STATE_camera_Parameters = "Confidence Threshold"
        
        self.AI_Parameters.setText(self.STATE_camera_Parameters)

    def BUTTON_toggle_fullScreen(self):
        if self.isFullScreen():
            self.showNormal()
            self.button_fullScreen.setText("Full screen")
        else:
            self.showFullScreen()
            self.button_fullScreen.setText("Exit full screen")

    def file_Manager(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Video File", fr"{self.main_Path}Resources", "All Files (*);;Video Files (*.mp4 *.avi)")
        if file_name:
            self.path_Input.setText(file_name)
            self.path_mode = file_name

    def find_capture_Devices(self):
        index = 0
        while True:
            cap = cv2.VideoCapture(index)
            if not cap.read()[0]:
                break
            self.capture_Devices.addItem(f"Device {index}", index)
            cap.release()
            index += 1

    def check_Input(self):
        if self.current_Mode=="Video Mode" and self.path_Input.text():
            self.AI_Parameters.setEnabled(True)
            self.horiSli_ConfidenceThreshold.setEnabled(True)
            self.label_ConfidenceThreshold.setEnabled(True)
            self.text_ConfidenceThreshold.setEnabled(True)

            self.button_Start.setEnabled(True)
            self.button_Start.setStyleSheet("""
                                            QPushButton{
                                                text-align: center;
                                                padding-bottom: 4px;
                                                background-color:#39663C;
                                                border-radius: 5px;
                                            } 
                                            QPushButton:hover {
                                                background-color: #2d522f;
                                                border-radius: 5px;
                                            }""")

            self.button_speedInitial.setStyleSheet("""
                                                QPushButton 
                                                {
                                                    text-align: center;
                                                    padding-bottom: 4px;
                                                    background-color: #0d0a36; 
                                                    border-radius: 5px;
                                                }
                                                QPushButton:hover
                                                {
                                                    background-color: #131057;
                                                    border-radius: 5px;
                                                }
                                            """)
            self.button_speedUp.setStyleSheet("""
                                                QPushButton 
                                                {
                                                    text-align: center;
                                                    padding-bottom: 4px;
                                                    background-color: #1b184a; 
                                                    border-radius: 5px;
                                                }
                                                QPushButton:hover
                                                {
                                                    background-color:  #131057;
                                                    border-radius: 5px;
                                                }
                                            """)
            self.button_speedDown.setStyleSheet("""
                                                QPushButton 
                                                {
                                                    text-align: center;
                                                    padding-bottom: 4px;
                                                    background-color:#0c0a29; 
                                                    border-radius: 5px;
                                                }
                                                QPushButton:hover
                                                {
                                                    background-color: #131057;
                                                    border-radius: 5px;
                                                }
                                            """)
            
           


            self.button_speedDown.setEnabled(True)
            self.button_speedUp.setEnabled(True)
            self.button_speedInitial.setEnabled(True)
            self.current_Speed.setEnabled(True)

        elif self.current_Mode== "Capture Mode" and self.capture_Devices.currentIndex() !=-1:
            self.button_Start.setEnabled(True)

            self.AI_Parameters.setEnabled(True)
            self.horiSli_ConfidenceThreshold.setEnabled(True)
            self.label_ConfidenceThreshold.setEnabled(True)
            self.text_ConfidenceThreshold.setEnabled(True)

            self.button_Start.setStyleSheet("""
                                            QPushButton{
                                                text-align: center;
                                                padding-bottom: 4px;
                                                background-color:#39663C;
                                                border-radius: 5px;
                                            } 
                                            QPushButton:hover {
                                                background-color: #2d522f;
                                                border-radius: 5px;
                                            }""")

            self.button_speedInitial.setStyleSheet("""
                                                QPushButton 
                                                {
                                                    text-align: center;
                                                    padding-bottom: 4px;
                                                    background-color: #0d0a36; 
                                                    border-radius: 5px;
                                                }
                                                QPushButton:hover
                                                {
                                                    background-color: #131057;
                                                    border-radius: 5px;
                                                }
                                            """)
            self.button_speedUp.setStyleSheet("""
                                                QPushButton 
                                                {
                                                    text-align: center;
                                                    padding-bottom: 4px;
                                                    background-color: #1b184a; 
                                                    border-radius: 5px;
                                                }
                                                QPushButton:hover
                                                {
                                                    background-color:  #131057;
                                                    border-radius: 5px;
                                                }
                                            """)
            self.button_speedDown.setStyleSheet("""
                                                QPushButton 
                                                {
                                                    text-align: center;
                                                    padding-bottom: 4px;
                                                    background-color:#0c0a29; 
                                                    border-radius: 5px;
                                                }
                                                QPushButton:hover
                                                {
                                                    background-color: #131057;
                                                    border-radius: 5px;
                                                }
                                            """)

           

            self.button_speedDown.setEnabled(True)
            self.button_speedUp.setEnabled(True)
            self.button_speedInitial.setEnabled(True)
            self.current_Speed.setEnabled(True)

        else:
            self.button_Start.setEnabled(False)
            self.button_Start.setStyleSheet("""
                                                QPushButton 
                                                {
                                                    background-color:#3c3c3c; 
                                                    border-radius: 5px;
                                                }
                                            """)

            self.button_speedInitial.setStyleSheet("""
                                                QPushButton 
                                                {
                                                    background-color:#3c3c3c; 
                                                    border-radius: 5px;
                                                }
                                                """)

            self.button_speedUp.setStyleSheet("""
                                                QPushButton 
                                                {
                                                    background-color:#3c3c3c; 
                                                    border-radius: 5px;
                                                }
                                            """)

            self.button_speedDown.setStyleSheet("""
                                                QPushButton 
                                                {
                                                    background-color:#3c3c3c; 
                                                    border-radius: 5px;
                                                }
                                            """)

            self.button_Play.setEnabled(False)
            self.button_Play.setStyleSheet("""
                                                QPushButton 
                                                {
                                                    background-color:#3c3c3c; 
                                                    border-radius: 5px;
                                                }
                                            """)

            self.button_speedDown.setEnabled(False)
            self.button_speedUp.setEnabled(False)
            self.button_speedInitial.setEnabled(False)
            self.current_Speed.setEnabled(False)

    def SLIDER_confidence(self, value):
        self.text_ConfidenceThreshold.setText(str(value))
        self.current_Threshold = self.horiSli_ConfidenceThreshold.value()

    def change_Font_Properties(self, widget, size, bold = False):
        font = widget.font()
        font.setPointSize(int(size))
        font.setBold(bold)
        widget.setFont(font)

    def closeEvent(self, event):
        # Prevent attribute error if initialize_Window has not been called
        if hasattr(self, 'cap'):
            self.cap.release()
        event.accept() # Close event
    
class hard_Cover(QMainWindow,) :
    def __init__(self,main_Path, window_Resolution, window_Scale=1):
        super().__init__()
        self.setWindowTitle("Hardcover Presentation")
        self.setGeometry(100, 100, window_Resolution[0], window_Resolution[1])
        self.window_Scale = window_Scale
        self.main_Path = main_Path
        self.icon_image_Path = main_Path + "Icon"
        self.setupUI()

    def setupUI(self):
        # Make a central widget
        self.central_Widget = QWidget(self)
        self.setCentralWidget(self.central_Widget)
        
        # HCMUTE logo and text box
        self.SIZEw_logo_HCMUTE = int(120 * self.window_Scale)
        self.SIZEh_logo_HCMUTE = int(154 * self.window_Scale)
        self.logo_HCMUTE= QLabel(self)
        self.logo_HCMUTE.setPixmap(QPixmap(fr"{self.icon_image_Path}/IMAGE_HCMUTE.png").scaled(self.SIZEw_logo_HCMUTE, self.SIZEh_logo_HCMUTE, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio, transformMode=Qt.TransformationMode.SmoothTransformation))
        
        self.label_HCMUTE = QLabel("Ho Chi Minh City University of Technology and Education",self)
        self.label_HCMUTE.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.label_HCMUTE.setWordWrap(True)
        self.change_Font_Properties(self.label_HCMUTE, 21 * self.window_Scale, True)

        # Gray box for hightlight HCMUTE logo
        self.background_HCMUTE = QFrame(self.central_Widget)
        self.background_HCMUTE.setStyleSheet("background-color:#fefefe; border-radius: 5px;")

        # FME logo and text box
        self.SIZEw_logo_FME = self.SIZEh_logo_FME = int(120 * self.window_Scale)
        self.logo_FME = QLabel(self)
        self.logo_FME.setPixmap(QPixmap(fr"{self.icon_image_Path}/IMAGE_FME.png").scaled(self.SIZEw_logo_FME, self.SIZEh_logo_FME, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio, transformMode=Qt.TransformationMode.SmoothTransformation))
        
        self.label_FME_under = QLabel("FME", self)
        self.change_Font_Properties(self.label_FME_under, 21 * self.window_Scale, True)
        self.label_FME_under.setStyleSheet("color: #3fbbe4;")
        
        self.label_FME = QLabel("Faculty of Mechanical\nEngineering",self)
        self.label_FME.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.label_FME.setWordWrap(True)
        self.change_Font_Properties(self.label_FME, 21 * self.window_Scale, True)  

        # Major and subject, teacher
        self.label_Major = QLabel("Major:", self)
        self.change_Font_Properties(self.label_Major, 18 * self.window_Scale, bold=False, underline=True)
        self.text_Major = QLabel("Robotics and Artificial Intelligence", self)
        self.change_Font_Properties(self.text_Major, 18 * self.window_Scale, bold=False, underline=False)

        self.label_Subject = QLabel("Subject:", self)
        self.change_Font_Properties(self.label_Subject, 18 * self.window_Scale, bold=False, underline=True)
        self.text_Subject = QLabel("Machine Vision", self)
        self.change_Font_Properties(self.text_Subject, 18 * self.window_Scale, bold=False, underline=False)

        self.label_Teacher = QLabel("Lecturer:",self)
        self.change_Font_Properties(self.label_Teacher, 18 * self.window_Scale, bold=False, underline=True)
        self.text_Teacher = QLabel("Ph.D Nguyen Van Thai",self)
        self.change_Font_Properties(self.text_Teacher, 18 * self.window_Scale, bold=False, underline=False)

        # Project
        self.label_Project = QLabel("Final Term Project", self)
        self.change_Font_Properties(self.label_Project, 26 * self.window_Scale, bold=True, underline=True)
        self.label_Project.setStyleSheet("color: #db382c; ")

        self.text_Project_Desc = QLabel("Detect Pothole to Support vehicle\nshock absorption system", self)
        self.text_Project_Desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.change_Font_Properties(self.text_Project_Desc, 22 * self.window_Scale)

        # Performer
        self.label_Performer = QLabel("Performer", self)
        self.change_Font_Properties(self.label_Performer, 17 * self.window_Scale, bold=True)

        self.SIZE_text_students_ID = int(15 * self.window_Scale)
        self.text_Student_1 = QLabel("Nguyen Trinh Tra Giang", self)
        self.change_Font_Properties(self.text_Student_1, self.SIZE_text_students_ID)

        self.text_Student_2 = QLabel("Pham Thanh Tri", self)
        self.change_Font_Properties(self.text_Student_2, self.SIZE_text_students_ID)

        self.text_Student_3 = QLabel("Nguyen Quoc Trung", self)
        self.change_Font_Properties(self.text_Student_3, self.SIZE_text_students_ID)

        # ID
        self.label_ID = QLabel("ID", self)
        self.change_Font_Properties(self.label_ID, 17 * self.window_Scale, bold=True)

        self.text_ID_1 = QLabel("22134002", self)
        self.change_Font_Properties(self.text_ID_1, self.SIZE_text_students_ID)

        self.text_ID_2 = QLabel("22134015", self)
        self.change_Font_Properties(self.text_ID_2, self.SIZE_text_students_ID)

        self.text_ID_3 = QLabel("22134016", self)
        self.change_Font_Properties(self.text_ID_3, self.SIZE_text_students_ID)

        # gray background for ID and performer
        self.background_Frame = QFrame(self.central_Widget)
        self.background_Frame.setStyleSheet("background-color: #363535; border-radius: 5px;")

        # Button to open VideoCapture UI
        self.open_VideoCapture = QPushButton("Start", self)
        self.open_VideoCapture.clicked.connect(self.BUTTON_toggle_VideoCapture)
        self.change_Font_Properties(self.open_VideoCapture, 15 * self.window_Scale, False)
        self.ICON_start = QIcon(fr"{self.icon_image_Path}/ICON_start.png")
        self.open_VideoCapture.setIcon(self.ICON_start)
        self.open_VideoCapture.setStyleSheet("""
                                                QPushButton 
                                                {
                                                    text-align: center;
                                                    padding-bottom: 4px;
                                                    background-color: #39663C; 
                                                    border-radius: 5px;
                                                }
                                                QPushButton:hover
                                                {
                                                    background-color: #2d522f;
                                                    border-radius: 5px;
                                                }
                                            """)
        
        # Pothole interface image
        self.PATH_pothole_Interface = fr"{self.icon_image_Path}/IMAGE_Pothole_Int_small.png"
        self.pothole_Interface = cv2.imread(self.PATH_pothole_Interface)
        
        self.pothole_Interface = cv2.resize(self.pothole_Interface, (int(self.pothole_Interface.shape[1]/1.8),int(self.pothole_Interface.shape[0]/1.8)))
        self.pothole_Interface = cv2.cvtColor(self.pothole_Interface, cv2.COLOR_BGR2RGB)

        self.SIZEh_Pothole_Interface, self.SIZEw_Pothole_Interface, self.channel_Pothole_Interface = self.pothole_Interface.shape
        self.bytesPerLine_pothole_Interface = 3 * self.SIZEw_Pothole_Interface

        self.qImg_Pothole_Interface = QImage(self.pothole_Interface, self.SIZEw_Pothole_Interface, self.SIZEh_Pothole_Interface, self.bytesPerLine_pothole_Interface, QImage.Format.Format_RGB888)
        self.pixmap_Pothole_Interface = QPixmap.fromImage(self.qImg_Pothole_Interface)

        self.picture_Pothole_Interface  = QLabel(self)
        self.picture_Pothole_Interface.setPixmap(self.pixmap_Pothole_Interface.scaled(self.SIZEw_Pothole_Interface, self.SIZEh_Pothole_Interface, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio, transformMode=Qt.TransformationMode.SmoothTransformation))
        self.picture_Pothole_Interface.setStyleSheet("QLabel { border: 5px solid #707070; border-radius: 6px; }")
        
        # Teacher image
        self.PATH_teacher_Interface = fr"{self.icon_image_Path}/IMAGE_teacher_small.png"
        self.teacher_Interface = cv2.imread(self.PATH_teacher_Interface)
        
        self.teacher_Interface = cv2.resize(self.teacher_Interface, (int(self.teacher_Interface.shape[1]/4),int(self.teacher_Interface.shape[0]/4)), interpolation=cv2.INTER_AREA)
        self.teacher_Interface = cv2.cvtColor(self.teacher_Interface, cv2.COLOR_BGR2RGB)

        self.SIZEh_teacher_Interface, self.SIZEw_teacher_Interface, self.channel_teacher_Interface = self.teacher_Interface.shape
        self.bytesPerLine_teacher_Interface = 3 * self.SIZEw_teacher_Interface

        self.qImg_teacher_Interface = QImage(self.teacher_Interface, self.SIZEw_teacher_Interface, self.SIZEh_teacher_Interface, self.bytesPerLine_teacher_Interface, QImage.Format.Format_RGB888)
        self.pixmap_teacher_Interface = QPixmap.fromImage(self.qImg_teacher_Interface)

        self.picture_teacher_Interface  = QLabel(self)
        self.picture_teacher_Interface.setPixmap(self.pixmap_teacher_Interface.scaled(self.SIZEw_teacher_Interface, self.SIZEh_teacher_Interface, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio, transformMode=Qt.TransformationMode.SmoothTransformation))
        self.picture_teacher_Interface.setStyleSheet("QLabel { border: 5px solid #707070; border-radius: 6px; }")

        # #Add widgets to layout
        self.logo_HCMUTE.setGeometry(int(80 * self.window_Scale), int(50 * self.window_Scale), self.SIZEw_logo_HCMUTE, self.SIZEh_logo_HCMUTE)
        self.label_HCMUTE.setGeometry(int(210 * self.window_Scale), int(70 * self.window_Scale), int(400 * self.window_Scale), int(100 * self.window_Scale))

        self.background_HCMUTE.setGeometry(int(74 * self.window_Scale), int(177 * self.window_Scale),int(130 * self.window_Scale), int(30 * self.window_Scale))

        self.picture_teacher_Interface.setGeometry(int(300 *self.window_Scale), int(320 * self.window_Scale), self.SIZEw_teacher_Interface, self.SIZEh_teacher_Interface)

        self.label_Major.setGeometry(int(80 * self.window_Scale), int(190 * self.window_Scale), int(700 * self.window_Scale), int(100 * self.window_Scale))
        self.text_Major.setGeometry(int(150* self.window_Scale), int(190 * self.window_Scale), int(700 * self.window_Scale), int(100 * self.window_Scale))

        self.label_Teacher.setGeometry(int(80 * self.window_Scale), int(220 * self.window_Scale), int(400 * self.window_Scale), int(100 * self.window_Scale))
        self.text_Teacher.setGeometry(int(180 * self.window_Scale), int(220 * self.window_Scale), int(400 * self.window_Scale), int(100 * self.window_Scale))

        self.label_Subject.setGeometry(int(80 * self.window_Scale), int(250 * self.window_Scale), int(400 * self.window_Scale), int(100 * self.window_Scale))
        self.text_Subject.setGeometry(int(170 * self.window_Scale), int(250 * self.window_Scale), int(400 * self.window_Scale), int(100 * self.window_Scale))
        
        self.label_Performer.setGeometry(int(240 * self.window_Scale), int(430 * self.window_Scale), int(400 * self.window_Scale), int(100 * self.window_Scale))
        self.label_ID.setGeometry(int(500 * self.window_Scale), int(430 * self.window_Scale), int(300 * self.window_Scale), int(100 * self.window_Scale))

        self.text_Student_1.setGeometry(int(180 * self.window_Scale), int(460 * self.window_Scale), int(400 * self.window_Scale), int(100 * self.window_Scale))
        self.text_Student_2.setGeometry(int(180 * self.window_Scale), int(490 * self.window_Scale), int(400 * self.window_Scale), int(100 * self.window_Scale))
        self.text_Student_3.setGeometry(int(180 * self.window_Scale), int(520 * self.window_Scale), int(400 * self.window_Scale), int(100 * self.window_Scale))

        self.text_ID_1.setGeometry(int(470 * self.window_Scale), int(460 * self.window_Scale), int(400 * self.window_Scale), int(100 * self.window_Scale))
        self.text_ID_2.setGeometry(int(470 * self.window_Scale), int(490 * self.window_Scale), int(400 * self.window_Scale), int(100 * self.window_Scale))
        self.text_ID_3.setGeometry(int(470 * self.window_Scale), int(520 * self.window_Scale), int(400 * self.window_Scale), int(100 * self.window_Scale))

        self.background_Frame.setGeometry(int(160 * self.window_Scale), int(460 * self.window_Scale), int(415 * self.window_Scale), int(135 * self.window_Scale))


        self.logo_FME.setGeometry(int(self.width()-510 * self.window_Scale), int(40 * self.window_Scale), self.SIZEw_logo_FME, self.SIZEh_logo_FME) 
        self.label_FME_under.setGeometry(int(self.width()-475 * self.window_Scale), int(135 * self.window_Scale), int(400 * self.window_Scale), int(100 * self.window_Scale))
        self.label_FME.setGeometry(int(self.width()-380 * self.window_Scale), int(65 * self.window_Scale), int(500 * self.window_Scale), int(100 * self.window_Scale))

        self.label_Project.setGeometry(int(self.width() - 480 * self.window_Scale), int(175 * self.window_Scale), int(400 * self.window_Scale), int(100 * self.window_Scale))
        self.text_Project_Desc.setGeometry(int(self.width()-700 * self.window_Scale), int(230 * self.window_Scale), int(700 * self.window_Scale), int(100 * self.window_Scale))

        self.picture_Pothole_Interface.setGeometry(int(self.width()-530 *self.window_Scale), int(320 * self.window_Scale), self.SIZEw_Pothole_Interface, self.SIZEh_Pothole_Interface)

                


        self.open_VideoCapture.setGeometry(int(self.width()-680 * self.window_Scale), int(610 * self.window_Scale), int(100 * self.window_Scale), int(50 * self.window_Scale))
    
    def BUTTON_toggle_VideoCapture(self):
        self.centralWidget().hide()

    def change_Font_Properties(self, widget, size, bold = False, underline = False):
        font = widget.font()
        font.setPointSize(int(size))
        font.setBold(bold)
        font.setUnderline(underline)
        widget.setFont(font)


class main_Application(QMainWindow):
    def __init__(self,main_Path, window_Resolution, window_Scale = 1):
        super().__init__()
        self.setWindowTitle("Main Application")

        self.window_ResolutionW = int(window_Resolution[0] * window_Scale)
        self.window_ResolutionH = int(window_Resolution[1] * window_Scale)

        self.setGeometry(100, 100, self.window_ResolutionW, self.window_ResolutionH)

        self.window_Scale = window_Scale
        self.main_Path = main_Path
        # Create a stack widget for 2 layouts
        self.stack_Widget = QStackedWidget()
        self.setCentralWidget(self.stack_Widget)

        # Create individual layouts
        self.hard_Cover = hard_Cover(self.main_Path, (self.window_ResolutionW, self.window_ResolutionH),window_Scale=self.window_Scale)
        self.video_Capture = None

        # Make hard cover layout view exist first
        self.stack_Widget.addWidget(self.hard_Cover)

        # Connect the button from hard cover to switch views
        self.hard_Cover.open_VideoCapture.clicked.connect(self.switch_To_Video_Capture)

    def switch_To_Video_Capture(self):
        if self.video_Capture is None:
            self.video_Capture = video_Capture(self.main_Path, fraction=(.6, .6),window_Resolution = (self.window_ResolutionW, self.window_ResolutionH), window_Scale= self.window_Scale)
            self.stack_Widget.addWidget(self.video_Capture)
        self.stack_Widget.setCurrentWidget(self.video_Capture)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    presentation = main_Application(main_Path = "" ,window_Resolution=(1280, 670), window_Scale=1.2)
    presentation.show()
    # presentation.show()
    # window = VideoCapture("Pothole_Detection_Iter_1_v8s-seg/Cook_Station_11/weights/best.pt",(0.75,0.75))
    # window.show()
    sys.exit(app.exec())
