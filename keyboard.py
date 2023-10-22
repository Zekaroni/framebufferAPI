keyboard_device = "/dev/input/event2"

# Open the device file in binary mode
with open(keyboard_device, "rb") as f:
    event_size = 24  # Size of each input event (bytes)

    while True:
        event_data = f.read(event_size)

        if len(event_data) != event_size:
            break

        # Parse the event data into its components
        # Each component has a specific size in bytes
        time_sec = int.from_bytes(event_data[0:4], byteorder='little')
        time_usec = int.from_bytes(event_data[4:8], byteorder='little')
        event_type = int.from_bytes(event_data[8:10], byteorder='little')
        event_code = int.from_bytes(event_data[10:12], byteorder='little')
        event_value = int.from_bytes(event_data[12:16], byteorder='little')

        print(f"Key pressed: Event Code {event_code}")