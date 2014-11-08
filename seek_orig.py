# You will need to have python 2.7 (3+ may work)
# and PyUSB 1.0
# and PIL 1.1.6 or better
# and numpy
# and scipy
# and ImageMagick

# Many thanks to the folks at eevblog, especially (in no particular order) 
#   miguelvp, marshallh, mikeselectricstuff, sgstair and many others
#     for the inspiration to figure this out
# This is not a finished product and you can use it if you like. Don't be
# surprised if there are bugs as I am NOT a programmer..... ;>))


import usb.core
import usb.util
import sys
import Image
import numpy
from scipy.misc import toimage

# find our Seek Thermal device  289d:0010
dev = usb.core.find(idVendor=0x289d, idProduct=0x0010)

# was it found?
if dev is None:
    raise ValueError('Device not found')

# set the active configuration. With no arguments, the first
# configuration will be the active one
dev.set_configuration()

# get an endpoint instance
cfg = dev.get_active_configuration()
intf = cfg[(0,0)]

ep = usb.util.find_descriptor(
    intf,
    # match the first OUT endpoint
    custom_match = \
    lambda e: \
        usb.util.endpoint_direction(e.bEndpointAddress) == \
        usb.util.ENDPOINT_OUT)

assert ep is not None


# Deinit the device

msg= '\x00\x00'
assert dev.ctrl_transfer(0x41, 0x3C, 0, 0, msg) == len(msg)
assert dev.ctrl_transfer(0x41, 0x3C, 0, 0, msg) == len(msg)
assert dev.ctrl_transfer(0x41, 0x3C, 0, 0, msg) == len(msg)


# Setup device

#msg = x01
assert dev.ctrl_transfer(0x41, 0x54, 0, 0, 0x01)

#  Some day we will figure out what all this init stuff is and
#  what the returned values mean.

msg = '\x00\x00'
assert dev.ctrl_transfer(0x41, 0x3C, 0, 0, msg) == len(msg)

ret1 = dev.ctrl_transfer(0xC1, 0x4E, 0, 0, 4)
ret2 = dev.ctrl_transfer(0xC1, 0x36, 0, 0, 12)

#print ret1
#print ret2

#

msg = '\x20\x00\x30\x00\x00\x00'
assert dev.ctrl_transfer(0x41, 0x56, 0, 0, msg) == len(msg)

ret3 = dev.ctrl_transfer(0xC1, 0x58, 0, 0, 0x40)
#print ret3

#

msg = '\x20\x00\x50\x00\x00\x00'
assert dev.ctrl_transfer(0x41, 0x56, 0, 0, msg) == len(msg)

ret4 = dev.ctrl_transfer(0xC1, 0x58, 0, 0, 0x40)
#print ret4

#

msg = '\x0C\x00\x70\x00\x00\x00'
assert dev.ctrl_transfer(0x41, 0x56, 0, 0, msg) == len(msg)

ret5 = dev.ctrl_transfer(0xC1, 0x58, 0, 0, 0x18)
#print ret5

#

msg = '\x06\x00\x08\x00\x00\x00'
assert dev.ctrl_transfer(0x41, 0x56, 0, 0, msg) == len(msg)

ret6 = dev.ctrl_transfer(0xC1, 0x58, 0, 0, 0x0C)
#print ret6

#

msg = '\x08\x00'
assert dev.ctrl_transfer(0x41, 0x3E, 0, 0, msg) == len(msg)

ret7 = dev.ctrl_transfer(0xC1, 0x3D, 0, 0, 2)
#print ret7

#

msg = '\x08\x00'
assert dev.ctrl_transfer(0x41, 0x3E, 0, 0, msg) == len(msg)
msg = '\x01\x00'
assert dev.ctrl_transfer(0x41, 0x3C, 0, 0, msg) == len(msg)

ret8 = dev.ctrl_transfer(0xC1, 0x3D, 0, 0, 2)
#print ret8

#

x=0

while x < 5:

# Send read frame request

    msg = '\xC0\x7E\x00\x00'
    assert dev.ctrl_transfer(0x41, 0x53, 0, 0, msg) == len(msg)

    ret9  = dev.read(0x81, 0x3F60, 1000)
    ret9 += dev.read(0x81, 0x3F60, 1000)
    ret9 += dev.read(0x81, 0x3F60, 1000)
    ret9 += dev.read(0x81, 0x3F60, 1000)

#  Let's see what type of frame it is
#  1 is a Normal frame, 3 is a Calibration frame
#  6 may be a pre-calibration frame
#  5, 10 other... who knows.

    status = ret9[20]

    if status == 1:

#  Convert the raw calibration data to a string array

	calimg = Image.fromstring("I", (208,156), ret9, "raw", "I;16")

#  Convert the string array to an unsigned numpy int16 array

	im2arr = numpy.asarray(calimg)
	im2arrF = im2arr.astype('uint16')

    if status == 3:

#  Convert the raw calibration data to a string array

	img = Image.fromstring("I", (208,156), ret9, "raw", "I;16")

#  Convert the string array to an unsigned numpy int16 array

	im1arr = numpy.asarray(img)
	im1arrF = im1arr.astype('uint16')

#  Subtract the calibration array from the image array and add an offset

	additionF = (im1arrF-im2arrF)+ 800

#  convert to an image and display with imagemagick

	toimage(additionF).show()
	x = x + 1
