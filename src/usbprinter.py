import usb.core

dev = usb.core.find(idVendor=0xfffe, idProduct=0x0001)
if dev is None:
    print('Our device is not connected')
# actually this is not the whole history, keep reading
if usb.core.find(bDeviceClass=7) is None:
    print('No printer found')
# this is not the whole history yet...
printers = usb.core.find(find_all=True, bDeviceClass=7)

# Python 2, Python 3, to be or not to be
import sys
sys.stdout.write('There are ' + len(printers) + ' in the system\n.')



