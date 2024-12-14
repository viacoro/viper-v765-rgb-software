import eel
import subprocess

VENDOR_ID = 0x04D9
PRODUCT_ID = 0xA1DF

bmRequestType = 0x21
bRequest = 0x09  # SET_REPORT request
wValue = 0x0300
wIndex = 3
wLength = 8
submit = False


def get_preset_packet():
    speed_val = 0x01
    color_val = 0x08
    brightness_val = 0x32
    direction_val = 0x01
    ###################
    ### CHOOSE MODE ###
    ###################
    print("Choose the mode [default=static]:")
    print("01: Static")
    print("02: Breath")
    print("03: Wave")
    print("04: Reactive")
    print("05: Sidewinder")
    print("06: Ripple")
    print("07: Reactive (duplicate smh)")
    print("08: Spectrum")
    print("09: Secret (Rainbow Sidewinder)")
    print("10: Rain")
    print("11: Whirl")
    print("12: Spotlight")
    print("51: Custom Preset 1")
    print("52: Custom Preset 2")
    print("53: Custom Preset 3")
    print("54: Custom Preset 4")
    print("55: Custom Preset 5")
    inp = "empty"
    while inp != "" and ((not inp.isdigit()) or int(inp) < 1 or int(inp) > 55 or (51 > int(inp) > 12)):
        inp = input("Input number: ")
    if inp == "":
        inp = "1"
    mode_val = int(inp)
    print()
    ####################
    ### CHOOSE COLOR ###
    ####################
    if mode_val != 8 and mode_val < 51:
        print("Choose the color [default=red]:")
        print("01: Red")
        print("02: Green")
        print("03: Yellow")
        print("04: Dark Blue")
        print("05: Light Blue")
        print("06: Pink")
        print("07: White")
        if mode_val != 1:
            print("08: RAINBOW")
        inp = "empty"
        while inp != "" and ((not inp.isdigit()) or int(inp) < 1 or int(inp) > 8 or (mode_val == 1 and int(inp) > 7)):
            inp = input("Input number: ")
        if inp == "":
            inp = "1"
        color_val = int(inp)
        print()

    #########################
    ### CHOOSE BRIGHTNESS ###
    #########################

    print("Choose the brightness (0 - 100) [default=100]:")
    print("00: Dimmest")
    print("    ...    ")
    print("100: Brightest")
    inp = "empty"
    while inp != "" and ((not inp.isdigit()) or int(inp) < 0 or int(inp) > 100):
        inp = input("Input number: ")
    if inp == "":
        inp = "100"
    brightness_val = int(brightness_val * (int(inp) / 100))
    print()

    ####################
    ### CHOOSE SPEED ###
    ####################

    if mode_val != 1 and mode_val < 51:
        print("Choose the speed (1 - 10) [default=5]:")
        print("01: Fastest")
        print("    ...    ")
        print("10: Slowest")
        inp = "empty"
        while inp != "" and ((not inp.isdigit()) or int(inp) < 1 or int(inp) > 10):
            inp = input("Input number: ")
        if inp == "":
            inp = "1"
        speed_val = int(inp)
        print()

    #########################
    ### CHOOSE DIRECTION  ###
    #########################
    if mode_val == 13 or mode_val == 3:
        print("Choose the direction [default=right]:")
        print("01: right")
        print("02: left")
        print("03: top")
        print("04: bottom")
        inp = "empty"
        while inp != "" and ((not inp.isdigit()) or int(inp) < 1 or int(inp) > 4):
            inp = input("Input number: ")
        if inp == "":
            inp = "1"
        direction_val = int(inp)
        print()
    packet = [0x08, 0x02, mode_val, speed_val, brightness_val, color_val, direction_val, 0x00]
    packet[7] = calculate_checksum(packet)
    return packet


@eel.expose
def submit_colors():
    global submit
    submit = True


def get_custom_packets():
    # QWERTZ layout
    eel.init('gui')
    eel.start("index.html", block=False)
    print("If the window doesn't appear open http://localhost:8000 in your browser.")
    while not submit:
        eel.sleep(1)
    data = eel.exportColors()()
    # data = ("0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;"
    #         "0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;"
    #         "0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;"
    #         "0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;"
    #         "0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;"
    #         "0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;"
    #         "0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;"
    #         "0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0;0,0,0")

    return data


def calculate_checksum(packet):
    checksum = sum(packet) & 0xFF  # Sum of all bytes modulo 256
    checksum = ~checksum & 0xFF  # One's complement
    return checksum


def main():
    preset = "aaaa"
    while preset != "1" and preset != "2":
        if (preset != "aaaa"):
            preset = input("Do you want to use an existing preset [1] or create a custom one [2]? Input '1' or '2': ")
        else:
            preset = input("Do you want to use an existing preset [1] or create a custom one [2]? ")
        preset = preset.lower()
    preset_packet = [0x08, 0x02, 0x02, 0x05, 0x32, 0x05, 0x02, 0xb5]
    if preset == "1":
        preset_packet = get_preset_packet()
        subprocess.run(['sudo', 'venv/bin/python3', 'packet-manager.py', "-p", str(preset_packet)], check=True)
    else:
        custom_packets = get_custom_packets()
        subprocess.run(['sudo', 'venv/bin/python3', 'packet-manager.py', "-c", custom_packets], check=True)


if __name__ == "__main__":
    main()
