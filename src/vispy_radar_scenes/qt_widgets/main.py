#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Main Window for visualization program
"""

import os
import numpy as np

from PyQt5 import QtCore, QtWidgets, QtGui

from .canvas import Canvas
from ..settings import Settings
from ..utils import set_stylesheet, package_resource_path, ColorOpts
from ..qt_objects import LoadSequenceWorker
from ..qt_theme import breeze_resources  # Loads stylesheet

from ..transform.coordinate_transformation import transform_detections_sequence_to_car, transform_detections_car_to_sequence
from radar_scenes.sensors import get_mounting


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, settings: Settings, canvas: Canvas):
        QtWidgets.QMainWindow.__init__(self)

        self.settings = settings
        self.canvas = canvas

        self.scene_buffer = []

        self.create_ui()

        icon_path = package_resource_path('res', 'icon.png')
        self.setWindowIcon(QtGui.QIcon(icon_path))

        self.showMaximized()
        self.sequence = None
        self.timestamps = []

        if self.settings.dark_mode:
            set_stylesheet(self.settings.dark_stylesheet)
        else:
            set_stylesheet(self.settings.light_stylesheet)

        self.timeline_spinbox.valueChanged.connect(self.timeline_slider.setValue)
        self.timeline_slider.valueChanged.connect(self.on_slider_value_changed)
        self.color_by_list.currentIndexChanged.connect(self.plot_frames)
        self.doppler_scale_slider.valueChanged.connect(self.plot_frames)
        self.doppler_arrows_cb.stateChanged.connect(self.on_doppler_cb_clicked)

    def toggle_stylesheet(self):
        self.canvas.on_toggle_dark_mode()
        if self.settings.dark_mode:
            set_stylesheet(self.settings.light_stylesheet)
        else:
            set_stylesheet(self.settings.dark_stylesheet)
        self.settings.dark_mode = not self.settings.dark_mode
        self.plot_frames()

    def create_ui(self):
        """
        Setup the whole UI of the radar data viewer. Creates several member variables for sliders, comboBoxes etc.
        :return: None
        """
        self.setWindowTitle(self.settings.program_title)

        self.main_grid_layout = QtWidgets.QGridLayout()
        self.central_widget = QtWidgets.QWidget()
        self.central_widget.setLayout(self.main_grid_layout)
        self.setCentralWidget(self.central_widget)

        # Vispy Canvas Widget
        self.main_grid_layout.addWidget(self.canvas.native, 0, 0)

        # Options Dock Widget
        self.options_layout = QtWidgets.QVBoxLayout()
        self.options_layout.setAlignment(QtCore.Qt.AlignTop)

        self.doppler_arrows_cb = QtWidgets.QCheckBox("Doppler Velocity Arrows")
        self.doppler_arrows_cb.setChecked(self.settings.draw_doppler_arrows)
        self.options_layout.addWidget(self.doppler_arrows_cb)

        # scaling of doppler arrows
        self.doppler_h_layout = QtWidgets.QHBoxLayout()
        self.doppler_h_layout.setContentsMargins(20, 0, 0, 10)
        self.doppler_scale_label = QtWidgets.QLabel()
        self.doppler_scale_label.setText("Scale")
        self.doppler_scale_label.setSizePolicy(
            QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))
        self.doppler_h_layout.addWidget(self.doppler_scale_label)

        self.doppler_scale_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.doppler_scale_slider.setMinimum(0)
        self.doppler_scale_slider.setMaximum(100)
        self.doppler_scale_slider.setValue(self.settings.doppler_arrow_scale * 100)
        self.doppler_scale_slider.setFixedWidth(150)
        self.doppler_h_layout.addWidget(self.doppler_scale_slider)

        self.options_layout.addLayout(self.doppler_h_layout)

        self.color_by_label = QtWidgets.QLabel()
        self.color_by_label.setText("Color Detections by")
        self.color_by_label.setStyleSheet(
            """
            QLabel {
            margin-top: 10px;
            }
            """
        )
        self.options_layout.addWidget(self.color_by_label)

        self.color_by_list = QtWidgets.QComboBox()
        self.color_by_list.setStyleSheet(
            """
            QComboBox::item:checked {
            height: 12px;
            border: 1px solid #32414B;
            margin-top: 0px;
            margin-bottom: 0px;
            padding: 4px;
            padding-left: 0px;
            }
            QComboBox {
            margin-left: 20px;
            }
            """
        )
        self.color_by_list.addItems([x.value for x in ColorOpts])
        self.color_by_list.setSizePolicy(
            QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))
        self.color_by_list.setCurrentIndex(0)
        self.options_layout.addWidget(self.color_by_list)

        #self.label_text_cb = QtWidgets.QCheckBox("Class Names of True Label")
        #self.label_text_cb.setChecked(True)
        #self.options_layout.addWidget(self.label_text_cb)

        options_widget = QtWidgets.QWidget()
        options_widget.setLayout(self.options_layout)
        self.options_dock = QtWidgets.QDockWidget("Options", self)
        self.options_dock.setWidget(options_widget)
        self.options_dock.setFloating(False)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.options_dock)

        # Detection Info Dock Widget
        self.info_dock = QtWidgets.QDockWidget("Information", self)
        self.info_dock.setMinimumWidth(350)
        self.info_dock.setMinimumHeight(200)
        self.detection_info_label = QtWidgets.QTextEdit("No detection selected.")
        self.detection_info_label.setMinimumWidth(200)
        flags = QtCore.Qt.TextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)
        self.detection_info_label.setTextInteractionFlags(flags)
        self.info_dock.setWidget(self.detection_info_label)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.info_dock)

        self.canvas.info_label = self.detection_info_label

        # Camera Dock Widget
        # TBD, use vispy.scene.widgets.viewbox

        # Timeline: Slider, Spinboxes, Labes
        self.timeline_grid_layout = QtWidgets.QGridLayout()
        self.timeline_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.timeline_slider.setStyleSheet("""
        .QSlider {
        min-height: 20px;
        max-height: 20px;
        }
        .QSlider::groove:horizontal {
        height: 15px;
        }
        """)

        self.timeline_spinbox = QtWidgets.QSpinBox()
        self.timeline_spinbox.setMaximum(10000)
        self.timeline_spinbox.setSizePolicy(
            QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))
        self.timeline_label = QtWidgets.QLabel()
        self.timeline_label.setText("Current Frame:")
        self.timeline_label.setSizePolicy(
            QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))

        self.timeline_grid_layout.addWidget(self.timeline_slider, 0, 0, 1, 8)
        self.timeline_grid_layout.addWidget(self.timeline_label, 1, 1)
        self.timeline_grid_layout.addWidget(self.timeline_spinbox, 1, 2)

        self.main_grid_layout.addLayout(self.timeline_grid_layout, 1, 0)

        # Menu
        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("File")
        self.view_menu = self.menu.addMenu("View")
        self.view_menu.addAction(self.options_dock.toggleViewAction())
        self.view_menu.addAction(self.info_dock.toggleViewAction())
        # self.view_menu.addAction(self.camera_dock.toggleViewAction())

        toggleDarkAction = QtWidgets.QAction('&Toggle Dark Mode', self)
        toggleDarkAction.setStatusTip('Toggle Dark Mode')
        toggleDarkAction.triggered.connect(lambda: self.toggle_stylesheet())

        self.settings_menu = self.menu.addMenu("Settings")
        self.settings_menu.addAction(toggleDarkAction)

        ## Exit QAction
        exit_action = QtWidgets.QAction("Exit", self)
        exit_action.setShortcut(QtGui.QKeySequence.Quit)
        exit_action.triggered.connect(self.close)

        # Open Sequence Action
        self.open_action = QtWidgets.QAction("Open Sequence", self)
        self.open_action.setShortcut(QtGui.QKeySequence.Open)
        self.open_action.triggered.connect(self.open_sequence)

        self.file_menu.addAction(self.open_action)
        self.file_menu.addAction(exit_action)

        # Status Bar
        self.status = self.statusBar()
        self.status_label = QtWidgets.QLabel()
        self.status_label.setText(
            "Frame {}/{}.\t\t Current Timestamp: {}.\t\t Time Window Size: {}s".format(0, 0, 0, 0.0))
        self.status.addPermanentWidget(self.status_label)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == QtCore.Qt.Key_Right:
            if self.timeline_slider.value() < self.timeline_slider.maximum():
                self.timeline_slider.setValue(self.timeline_slider.value() + 1)
        elif event.key() == QtCore.Qt.Key_Left:
            if self.timeline_slider.value() > self.timeline_slider.minimum():
                self.timeline_slider.setValue(self.timeline_slider.value() - 1)

    def on_doppler_cb_clicked(self, state):
        """
        Callback function which is called when the checkbox for displaying the Doppler arrows is clicked.
        Shows and hides the extra slider for scaling the Doppler arrows.
        Re-plots the scene.
        :param state: state of the checkbox
        :return: None
        """
        if self.doppler_arrows_cb.isChecked():
            self.doppler_h_layout.setContentsMargins(20, 0, 0, 10)
            self.doppler_scale_slider.setVisible(True)
            self.doppler_scale_label.setVisible(True)
        else:

            self.doppler_h_layout.setContentsMargins(20, 0, 0, 0)
            self.doppler_scale_slider.setVisible(False)
            self.doppler_scale_label.setVisible(False)
        self.plot_frames()

    def on_slider_value_changed(self, value: int):
        """
        Callback function which is called when the slider is moved.
        The value of the timeline spinbox is updated and the scene is plotted.
        :param value: Current value of the slider.
        :return:
        """
        self.timeline_spinbox.blockSignals(True)  # this is needed to avoid an infinite loop: setValue of the spin
        # box emits a signal that points back to this function. So we have to block signals temporarily for the spinbox
        self.timeline_spinbox.setValue(value)
        self.timeline_spinbox.blockSignals(False)  # unblock signals again

        self.detection_info_label.setText("No detection selected.")

        self.plot_frames()

    def open_sequence(self):
        """
        Dialog for opening a measurement sequence.
        Only json files can be loaded. Actual loading is done by the load_sequence function.
        :return: None
        """
        filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Open Sequence',
                                                         os.getcwd(), "Radar data files (*.json)",
                                                         options=QtWidgets.QFileDialog.DontUseNativeDialog)
        filename = filename[0]
        if filename != "" and filename is not None:
            self.load_sequence(filename)

    def on_sequence_loading_finished(self, sequence, timestamps):
        QtWidgets.QApplication.restoreOverrideCursor()
        self.sequence = sequence
        self.timestamps = timestamps
        # self.color_by_list.setCurrentIndex(6)
        self.timeline_slider.setMaximum(len(self.timestamps) - 1)
        self.timeline_spinbox.setMaximum(len(self.timestamps) - 1)
        self.timeline_slider.setMinimum(0)
        self.timeline_slider.setValue(0)
        # self.generate_colors_true_tracks()
        self.setWindowTitle("Radar Data Viewer - {}".format(self.sequence.sequence_name))
        self.plot_frames()

    def on_sequence_loading_failed(self):
        """
        Callback function for the case that loading of a sequence failed.
        Resets the cursor and prints and error box.
        :return:
        """
        QtWidgets.QApplication.restoreOverrideCursor()
        msg_box = QtWidgets.QMessageBox()
        msg_box.setIcon(QtWidgets.QMessageBox.Critical)
        msg_box.setText("Unable to open file.")
        msg_box.setWindowTitle("File Error")
        msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg_box.buttonClicked.connect(lambda: msg_box.close)
        msg_box.exec()

    def load_sequence(self, path: str):
        """
        Loads the contents of a json file which describes a measurement sequence.
        A timeline is created so that all scenes are in the correct order.
        The slider is initialized to the correct values and the first frame is plotted.
        :param path: full path to the json file.
        :return: None
        """
        if not path.endswith(".json") or not os.path.exists(path):
            return

        self.loader_worker = LoadSequenceWorker(path)
        self.thread = QtCore.QThread()
        self.loader_worker.loading_done.connect(self.on_sequence_loading_finished)
        self.loader_worker.loading_failed.connect(self.on_sequence_loading_failed)
        self.loader_worker.moveToThread(self.thread)
        self.loader_worker.finished.connect(self.thread.quit)
        self.thread.started.connect(self.loader_worker.load)
        self.thread.start()
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

    def get_current_scene(self):
        """
        Retrieves the scenes which should be displayed according to the current values of the time slider and the
        spinboxes for the past and future frames.
        Values of the spinboxes are retrieved and from the list of timestamps, the corresponding times are obtained.
        :return: The current frame (type Scene) and a list of other frames (type Scene) which should be displayed.
        """
        cur_idx = self.timeline_slider.value()
        cur_timestamp = self.timestamps[cur_idx]
        current_scene = self.sequence.get_scene(cur_timestamp)

        return current_scene

    def process_radar_data(self, current_scene):
        radar_data = current_scene.radar_data
        odometry_data = current_scene.odometry_data
        # TODO: Compute x_seq, y_seq, and yaw_seq ourselves from odometry data vx and yaw_rate
        # TODO: Use previous odometry and add delta

        if self.scene_buffer:
            for other_scene in self.scene_buffer:
                x_cc, y_cc = \
                    transform_detections_sequence_to_car(other_scene["x_seq"], other_scene["y_seq"], odometry_data)
                other_scene["x_cc"] = x_cc
                other_scene["y_cc"] = y_cc

        # Inputs:
        # Range, Azimuth Angle, Doppler Velocity, RCS/SNR, Sensor ID
        current_scenes = self.scene_buffer
        sensors_in_scene = np.unique(radar_data["sensor_id"])
        for unique_sensor_id in sensors_in_scene:
            # Clear any scenes with the same sensor ID as current one
            new_scene_buffer = []
            for i in current_scenes:
                if not i['sensor_id'][0] in radar_data['sensor_id']:
                    new_scene_buffer.append(i)
            current_scenes = new_scene_buffer

            sensor_radar_data = np.take(radar_data, np.argwhere(radar_data["sensor_id"] == unique_sensor_id).flatten())
            sensor_id = sensor_radar_data["sensor_id"]
            range_sc = sensor_radar_data["range_sc"]
            azimuth_sc = sensor_radar_data["azimuth_sc"]

            sensor_x = np.array([get_mounting(s_id)["x"] for s_id in sensor_id])
            sensor_y = np.array([get_mounting(s_id)["y"] for s_id in sensor_id])
            sensor_yaw = np.array([get_mounting(s_id)["yaw"] for s_id in sensor_id])

            x_cc = range_sc * np.cos(azimuth_sc + sensor_yaw) + sensor_x
            y_cc = range_sc * np.sin(azimuth_sc + sensor_yaw) + sensor_y

            x_seq, y_seq = transform_detections_car_to_sequence(x_cc, y_cc, odometry_data)

            sensor_radar_data['x_cc'] = x_cc
            sensor_radar_data['y_cc'] = y_cc
            sensor_radar_data['x_seq'] = x_seq
            sensor_radar_data['y_seq'] = y_seq

            current_scenes.append(sensor_radar_data)

        self.scene_buffer = current_scenes

        return np.hstack(self.scene_buffer)

    def update_status_bar(self, frame_idx, frame_timestamp, window_size):
        """
        Updates the text of the status bar
        :param frame_idx: current frame index
        :param frame_timestamp: Current timestamp of the frame
        :param window_size: Current size of the temporal time window. Depending on how many frames are displayed and
        how close these radar scans are in time, the value changes.
        :return: None
        """
        if len(self.timestamps) == 0:
            current_time = 0
        else:
            current_time = (frame_timestamp - self.timestamps[0]) / 10 ** 6

        self.status_label.setText \
            ("Frame {}/{}     Current Timestamp: {}     Time Window Size: {:.1f}ms     Time: {:.2f}s".format(
            frame_idx, len(self.timestamps) - 1, frame_timestamp, window_size, current_time))

    def trafo_radar_data_world_to_car(self, scene, other_scenes) -> np.ndarray:
        """
        Transforms the radar data listed in other_scenes into the same car coordinate system that is used in 'scene'.
        :param scene: Scene. Containing radar data and odometry information of one scene. The odometry information from
        this scene is used to transform the detections from the other timestamps into this scene.
        :param other_scenes: List of Scene items. All detections in these other scenes are transformed
        :return: A numpy array with all radar data from all scenes. The fields "x_cc" and "y_cc" are now relative to the
        current scene.
        """
        if len(other_scenes) == 0:
            return scene.radar_data
        other_radar_data = np.hstack([x.radar_data for x in other_scenes])
        x_cc, y_cc = transform_detections_sequence_to_car(other_radar_data["x_seq"], other_radar_data["y_seq"],
                                                          scene.odometry_data)
        other_radar_data["x_cc"] = x_cc
        other_radar_data["y_cc"] = y_cc
        return np.hstack([scene.radar_data, other_radar_data])

    def plot_frames(self):
        """
        Plot the current frames.
        This includes:
            - Detections as scatter points
            - Camera image
            - Text labels of all objects containing the class names
            - Doppler velocity arrows
            - Convex Hulls around ground truth objects
        :return: None
        """

        cur_idx = self.timeline_slider.value()
        if len(self.timestamps) == 0 or cur_idx >= len(self.timestamps):
            return
        cur_timestamp = self.timestamps[cur_idx]
        current_scene = self.get_current_scene()
        radar_data = self.process_radar_data(current_scene)

        self.update_status_bar(cur_idx, cur_timestamp,
                               (np.max(radar_data["timestamp"] - np.min(radar_data["timestamp"])) / 10 ** 3))

        # DOPPLER ARROWS
        if self.doppler_arrows_cb.isChecked():
            self.settings.doppler_arrow_scale = self.doppler_scale_slider.value() / 100
            self.settings.draw_doppler_arrows = True
        else:
            self.settings.draw_doppler_arrows = False

        # DRAW CANVAS
        self.canvas.update_scene(radar_data, color_by=self.color_by_list.currentText())
