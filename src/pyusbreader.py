from keyboard_alike import reader

reader = reader.Reader(0x08ff, 0x0009, 84, 16, should_reset=False)
reader.initialize()
print(reader.read().strip())
reader.disconnect()
