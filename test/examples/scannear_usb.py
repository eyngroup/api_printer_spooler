import usb.core
import usb.util

devices = usb.core.find(find_all=True)

for dev in devices:
    print(f"Device: {usb.util.get_string(dev, dev.iProduct)}")
    print(f"  VID: {dev.idVendor:04x}")
    print(f"  PID: {dev.idProduct:04x}")
    print(f"  Manufacturer: {usb.util.get_string(dev, dev.iManufacturer)}")
    print(f"  Serial Number: {usb.util.get_string(dev, dev.iSerialNumber)}")
    print()
