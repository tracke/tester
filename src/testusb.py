import usb.core
import usb.util
import sys
import os

from keyboard_alike import reader
from keyboard_alike import mapping

global barcode_scanner
global chunk_size

def prt_scanner():
	global barcode_scanner
        print(barcode_scanner)

def set_bc_scanner(dev):
	global barcode_scanner
	barcode_scanner = usb.core.find(dev)

def is_printer(dev):
        import usb.util
        if dev.bDeviceClass == 7:
            return True
        for cfg in dev:
            if usb.util.find_descriptor(cfg, bInterfaceClass=7) is not None:
                return True
print ("Detected Printers:")
for printer in usb.core.find(find_all=True, custom_match = is_printer):
 	print usb.util.get_string(printer,printer.iManufacturer)
	print usb.util.get_string(printer,printer.iProduct)
#        print (printer)

print ("Detected Scanners")

def is_scanner(dev):
	if dev.bDeviceClass != 0:
	    return False
	for cfg in dev:
	    if usb.util.find_descriptor(cfg,bInterfaceClass = 3) is not none:
	        return True

def get_scanner():
    usb_dev = usb.core.find(find_all=True)
    for d in usb_dev:
	if d.bDeviceClass==0:   
	    for cfg in d:	   
	       if usb.util.find_descriptor(cfg, bInterfaceClass=3) is not None:
                   print usb.util.get_string(d,d.iManufacturer)
                   print usb.util.get_string(d,d.iProduct)
                   print (d.idProduct,d.idVendor)
# 	           print d           
		   return (d)

def get_usb_device():
	usb_dev = usb.core.find(find_all=True)
	for d in usb_dev:
		print d           
	return (d)



def decode_raw_data(raw_data):
        data = extract_meaningful_data_from_chunk(raw_data)
        return raw_data_to_keys(data)

def extract_meaningful_data_from_chunk(raw_data):
        shift_indicator_index = 0
        raw_key_value_index = 2
        for chunk in get_chunked_data(raw_data):
            yield (chunk[shift_indicator_index], chunk[raw_key_value_index])

def get_chunked_data(raw_data):
	chunk_size = len(raw_data)
        return mapping.chunk_data(raw_data,chunk_size)

#@staticmethod
def raw_data_to_keys(extracted_data):
        return ''.join(map(mapping.raw_to_key, extracted_data))






def scanner_loop():		  
  global chunk_size
  DATA_SIZE = 16   

  NO_SCAN_CODE = {0x1E:'1', 0x1F:'2', 0x20:'3', 0x21:'4', 0x22:'5', 0x23:'6', 0x24:'7'
    , 0x25:'8', 0x26:'9', 0x27:'0', 0x28:''} # 28=enter
  
  scanner=get_scanner()
  print "using"
  print scanner.iProduct
  print scanner.iVendorId 
  data_size = 16  
  should_reset = True
  print scanner

  if scanner.is_kernel_driver_active(0):   # On dtache le priphrique du kernel, plus d'envoi sur stdin
      try:
        scanner.detach_kernel_driver(0)
      except usb.core.USBError as e:
        sys.exit("Could not detatch kernel driver: %s" % str(e))


#endpoints
  endpoint=scanner[0][0,0][0]
  data=[]
  print "Reading from Endpoint "
  print endpoint.bEndpointAddress
  print "Max packet size ="
  print endpoint.wMaxPacketSize

  lu = False
  print "Waiting to read..."
  lecture=''
  buff=[]
  data_read=False
  while 1:
    try:
        data += scanner.read(endpoint.bEndpointAddress, endpoint.wMaxPacketSize)
# 	print data
	data_read=True
        if not lu:
            print "Waiting to read..."
        lu = True

    except usb.core.USBError as e:
        if e.args[0] == 110 and data_read:
            if len(data) < DATA_SIZE:
                print "Lecture incorrecte, recommencez. (%d bytes)" % len(data)
                print "Data: %s" % ''.join(map(hex, data))
                data = []
                lu = False
		data_read=False
                continue
            else:		
#                for n in range(0,len(data),16):
#                     print '  '.join(map(hex,data[n:n+16]))
#                     lecture+=NO_SCAN_CODE[data[n+2]]		    
                chunk_data = len(data)
                return decode_raw_data(data)
#                break   # Code lu
#  return lecture
 #   return decode_raw_data(data) 

if __name__ == '__main__':
  get_usb_device()

