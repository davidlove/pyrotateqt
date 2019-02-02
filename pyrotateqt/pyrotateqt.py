#!/usr/bin/env /usr/bin/python

from glob import glob
from math import sqrt
import os.path as op
import sys
from subprocess import check_call, check_output
from time import time

from PyQt5.QtWidgets import QApplication, QMainWindow, QSystemTrayIcon, QMenu, QAction, qApp
from PyQt5.QtCore import QSize, QTimer
from PyQt5.QtGui import QIcon

DIR = op.dirname(op.realpath(__file__))


# The variable MY_TOUCHSCREEN lets you manually configure the name of
# your touchscreen. Otherwise the script attempts automatic detection
# of devices names "touchscreen" or "wacom".
# To enable automatic detection, simply comment the variable out
#MY_TOUCHSCREEN = 'ELAN2097:00 04F3:2501'
MY_TOUCHSCREEN = '13'


class MainWindow(QMainWindow):
    """
         Сheckbox and system tray icons.
         Will initialize in the constructor.
    """
    check_box = None
    tray_icon = None
 
    # Override the class constructor
    def __init__(self):
        # Be sure to call the super class method
        QMainWindow.__init__(self)
 
        #self.setMinimumSize(QSize(480, 80))             # Set sizes
        #self.setWindowTitle("QT Rotate Screen")         # Set a title

        self.current_state = None
 
        # Init QSystemTrayIcon
        self.tray_icon = QSystemTrayIcon(self)
        self.timer = QTimer()
        self.timer.timeout.connect(self.rotate_step)
        self.icon_rotate = QIcon(op.join(DIR, 'rotate.png'))
        self.icon_lock = QIcon(op.join(DIR, 'rotate_lock.png'))
        self.mode = 'rotate'
        self.tray_click()
        self.tray_click()
        self.tray_icon.activated.connect(self.tray_click)
 
        '''
            Define and add steps to work with the system tray icon
            show - show window
            hide - hide window
            exit - exit from application
        '''
        normal_action = QAction("Normal", self)
        left_action = QAction("Left", self)
        invert_action = QAction("Invert", self)
        right_action = QAction("Right", self)
        quit_action = QAction("Exit", self)
        normal_action.triggered.connect(self.rotate_normal)
        left_action.triggered.connect(self.rotate_left)
        invert_action.triggered.connect(self.rotate_inverted)
        right_action.triggered.connect(self.rotate_right)
        quit_action.triggered.connect(qApp.quit)
        tray_menu = QMenu()
        tray_menu.addAction(normal_action)
        tray_menu.addAction(left_action)
        tray_menu.addAction(invert_action)
        tray_menu.addAction(right_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
    def tray_click(self):
        if self.mode == 'rotate':
            self.to_lock_mode()
            #self.tray_icon.setIcon(self.icon_lock)
            #self.mode = 'lock'
            #self.initialize_screen()
            #self.timer.stop()
        elif self.mode == 'lock':
            self.to_rotate_mode()
            #self.tray_icon.setIcon(self.icon_rotate)
            #self.mode = 'rotate'
            ##self.timer.start(1000)
            #self.timer.start(500)

    def to_rotate_mode(self):
        self.tray_icon.setIcon(self.icon_rotate)
        self.mode = 'rotate'
        #self.timer.start(1000)
        self.timer.start(500)

    def to_lock_mode(self):
        self.tray_icon.setIcon(self.icon_lock)
        self.mode = 'lock'
        self.initialize_screen()
        self.timer.stop()
            
    def initialize_screen(self):
        for basedir in glob('/sys/bus/iio/devices/iio:device*'):
            if 'accel' in self.read(basedir, 'name'):
                break
        else:
            sys.stderr.write("Can't find an accellerator device!\n")
            sys.exit(1)
        self.basedir = basedir

        try:
            self.touchscreens = [MY_TOUCHSCREEN]
        except (NameError, UnboundLocalError):
            # These lines are from the original script for identifying the
            # touchscreen, but they don't work for my laptop
            devices = [str(xx) for xx in check_output(['xinput', '--list', '--name-only']).splitlines()]
            touchscreen_names = ['touchscreen', 'wacom']
            self.touchscreens = [i for i in devices if any(j in i.lower() for j in touchscreen_names)]


        #self.disable_touchpads = True

        #touchpad_names = ['touchpad', 'trackpoint']
        #self.touchpads = [i for i in devices if any(j in i.lower() for j in touchpad_names)]

        self.scale = float(self.read(self.basedir, 'in_accel_scale'))

        self.g = 7.0  # (m^2 / s) sensibility, gravity trigger

        self.STATES = [
            {'rot': 'normal', 'coord': '1 0 0 0 1 0 0 0 1', 'touchpad': 'enable',
             'check': lambda x, y: y <= -self.g},
            {'rot': 'inverted', 'coord': '-1 0 1 0 -1 1 0 0 1', 'touchpad': 'disable',
             'check': lambda x, y: y >= self.g},
            {'rot': 'left', 'coord': '0 -1 1 1 0 0 0 0 1', 'touchpad': 'disable',
             'check': lambda x, y: x >= self.g},
            {'rot': 'right', 'coord': '0 1 0 -1 0 1 0 0 1', 'touchpad': 'disable',
             'check': lambda x, y: x <= -self.g},
        ]
        
        self.accel_x = self.bdopen(self.basedir, 'in_accel_x_raw')
        self.accel_y = self.bdopen(self.basedir, 'in_accel_y_raw')
        self.accel_z = self.bdopen(self.basedir, 'in_accel_z_raw')
        
    def rotate_step(self):
        fail = False
        #t = time()
        x = self.read_accel(self.accel_x)
        #tx = time() - t
        y = self.read_accel(self.accel_y)
        z = self.read_accel(self.accel_z)
        if x == 0 and y == 0 and z == 0:
            #self.tray_icon.showMessage('Accelerometer Failure', 'Accelerometer took too long to respond')
            self.tray_icon.showMessage('Accelerometer Failure', 'Total acceleration = 0')
            self.tray_click()
            self.rotate_normal()
            return
        g_read = sqrt(x**2 + y**2 + z**2)
        if g_read > 11:
            return
        for i in range(4):
            if i == self.current_state:
                continue
            if self.STATES[i]['check'](x, y):
                self.current_state = i
                self.rotate(i)
                break
    
    def rotate(self, state):
        s = self.STATES[state]
        check_call(['xrandr', '-o', s['rot']])
        #for dev in self.touchscreens if self.disable_touchpads else (self.touchscreens + self.touchpads):
        for dev in self.touchscreens:
            check_call([
                'xinput', 'set-prop', dev,
                'Coordinate Transformation Matrix',
            ] + s['coord'].split())

    def rotate_normal(self):
        if self.current_state != 0:
            self.rotate(0)
            self.to_lock_mode()

    def rotate_inverted(self):
        self.rotate(1)
        self.to_lock_mode()

    def rotate_left(self):
        self.rotate(2)
        self.to_lock_mode()

    def rotate_right(self):
        self.rotate(3)
        self.to_lock_mode()
        
    # Override closeEvent, to intercept the window closing event
    # The window will be closed only if there is no check mark in the check box
    def closeEvent(self, event=None):
        if event is not None:
            event.ignore()
        self.hide()

    def bdopen(self, basedir, fname):
        return open(op.join(basedir, fname))

    def read(self, basedir, fname):
        return self.bdopen(basedir, fname).read()
    
    def read_accel(self, fp):
        fp.seek(0)
        return float(fp.read()) * self.scale


def run():
    """Run the QT app"""
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    mw.closeEvent()
    sys.exit(app.exec())


if __name__ == "__main__":
    run()

