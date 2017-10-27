
from keyboard_alike import reader
import usb.core


data_size = 32
chunk_size = 8

class BarCodeReader(reader.Reader):
    """
    This class supports a USB bar code scanner configured to work as a keyboard
    """
    pass

def get_scanner():
    usb_dev = usb.core.find(find_all=True)
    for d in usb_dev:
        if d.bDeviceClass==0:   
            for cfg in d:       
               if usb.util.find_descriptor(cfg, bInterfaceClass=3) is not None:
                   if cfg.bInterfaceProtocol != 1:
                       print usb.util.get_string(d,d.iManufacturer)
                       print usb.util.get_string(d,d.iProduct)
                       print (d.idProduct,d.idVendor)     
                   return (d)
    return(0)
               
               
if __name__ == "__main__":
   unit=get_scanner()
   if unit:
       vendor_id = unit.idVendor
       product_id = unit.idProduct
    
       reader = BarCodeReader(vendor_id, product_id, data_size, chunk_size, should_reset=True)
       reader.initialize()
       print ("Reader ready...")
       print(reader.read().strip())
       reader.disconnect()
   else:
       print ("Barcode Scanner not found") 
       
