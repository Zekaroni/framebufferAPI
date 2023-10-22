keyboard_device = "/dev/input/eventX"  # Replace X with the appropriate device number

# Open the device file in binary mode
with open(keyboard_device, "rb") as f:
    event_size = 24  # Size of each input event

    while True:
        event_data = f.read(event_size)

        if len(event_data) != event_size:
            break

        # Extract values from the event data
        time, value, event_type, code, _ = (
            int.from_bytes(event_data[i:i + 8], byteorder='little')
            for i in range(0, event_size, 8)
        )

        if event_type == 1 and value == 1:
            # Key press event
            print(f"Key pressed: {code}")
