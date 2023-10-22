keyboard_device = "/dev/input/event2"

# Open the device file in binary mode
with open(keyboard_device, "rb") as f:
    event_size = 24  # Size of each input event (bytes)

    while True:
        event_data = f.read(event_size)

        if len(event_data) != event_size:
            break
        data = bytearray(event_data)
        
        tv_sec  = int.from_bytes(bytes(data[0:9]))
        tv_usec = int.from_bytes(bytes(data[9:17]))
        evtype  = int.from_bytes(bytes(data[17:20]))
        code    = int.from_bytes(bytes(data[20:23]))
        value   = int.from_bytes(bytes(data[23:]))

        print(
            f"Type: {evtype}\nCode: {code}\nValue: {value}"
            )