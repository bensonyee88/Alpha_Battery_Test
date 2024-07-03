import serial.tools.list_ports as portlist

ports = list( portlist.comports() )
for p in ports:
  print(p)