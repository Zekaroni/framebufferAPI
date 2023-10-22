keyboard_device = "/dev/input/event2"
with open(keyboard_device, "rb") as f:
    event_size = 24 
    while True:
        event_data = f.read(event_size)
        if len(event_data) != event_size:
            break
        print(event_data)
        a,b,c = (int.from_bytes(event_data[i:i + 8], byteorder='little')for i in range(0, event_size, 8))
        print(
            f"A = {a}\n",
            f"B = {b}\n",
            f"C = {c}",
            sep="")