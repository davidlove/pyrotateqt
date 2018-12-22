#!/usr/bin/env python

from setuptools import setup

setup(name='pyrotateqt'
     ,version='1.0'
     ,description='Screen rotation system tray icon for QT'
     ,author='David Love'
     ,author_email='love.david.k@gmail.com  '
     ,url=''
     ,license='MIT'
     ,packages=['pyrotateqt']
     ,install_requires=['PyQt5']
     ,scripts=['bin/pyrotateqt']
     ,include_package_data=True
     )

