# pyrotateqt

This is a small code I wrote to get screen rotation working the way I
like it on my Dell Inspiron laptop.

The rotation code is based on [this script](https://gist.githubusercontent.com/ei-grad/4d9d23b1463a99d24a8d/raw/rotate.py)
that is available on the Arch Linux Wiki page for [Tablet PCs](https://wiki.archlinux.org/index.php/Tablet_PC).

I made small modifications to it to get the touchscreen device correct.
You can modify by setting the `MY_TOUCHSCREEN` variable in `pyrotateqt/pyrotateqt.py`

I also wrapped it in a QT system tray icon that allows for turning the rotation
detection on and off.

I've only tested this on my own laptop, so I don't know if it'll work for anything else.

