import usb.core
import usb.util
import time
import argparse
import sys
import ast

VENDOR_ID = 0x04D9
PRODUCT_ID = 0xA1DF

bmRequestType = 0x21
bRequest = 0x09  # SET_REPORT request
wValue = 0x0300
wIndex = 3
wLength = 8

INIT_PACKETS = [
    [0x15, 0x00, 0x03, 0x01, 0x03, 0x07, 0x00, 0xdc],
    [0x16, 0x00, 0x00, 0xff, 0x00, 0x00, 0x00, 0xea],
    [0x16, 0x00, 0x01, 0x00, 0xff, 0x00, 0x00, 0xe9],
    [0x16, 0x00, 0x02, 0xff, 0xff, 0x00, 0x00, 0xe9],
    [0x16, 0x00, 0x03, 0x00, 0x00, 0xff, 0x00, 0xe7],
    [0x16, 0x00, 0x04, 0x00, 0xff, 0xff, 0x00, 0xe7],
    [0x16, 0x00, 0x05, 0x00, 0xff, 0xff, 0x00, 0xe6],
    [0x16, 0x00, 0x06, 0xff, 0xff, 0xff, 0x00, 0xe6],
]


def send_custom_packets(dev, datas, slot=51):
    endpoint = 0x06
    start_packet = [0x08, 0x01, slot, 0x01, 0x00, 0x06, 0x01, 0xbb]
    record_packet = [0x12, 0x00, 0x00, 0x08, 0x00, 0x00, 0x00, 0xe5]
    end_packet = [0x08, 0x02, slot, 0x01, 0x1a, 0x06, 0x01, 0xa0]

    send_control_transfer(dev, start_packet)
    send_control_transfer(dev, record_packet)
    for data in datas:
        try:
            dev.write(endpoint, data)
            print("Interrupt transfer sent successfully")
        except usb.core.USBError as e:
            print(f"Error sending interrupt transfer: {e}")
    send_control_transfer(dev, end_packet)


def calculate_checksum(packet):
    checksum = sum(packet) & 0xFF  # Sum of all bytes modulo 256
    checksum = ~checksum & 0xFF  # One's complement
    return checksum


def send_control_transfer(dev, data):
    # Send a USB control transfer to the device
    dev.ctrl_transfer(bmRequestType, bRequest, wValue, wIndex, data)


def main():
    parser = argparse.ArgumentParser(description="Keyboard Packet Manager",
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-p', '--preset', type=str,
                        help="Takes an hex array with the size of 8. Has to look like this to be valid: "
                             "\n[08, 02, EF, SP, BR, PC, DN, CS]"
                             "\nEF... Effect Number 0x01 - 0x0D"
                             "\nSP... Effect Speed (01=highest, 0A=slowest)"
                             "\nBR... Brightness (0x00 - 0x32)"
                             "\nPC... Preset Color Number (0x01 - 0x08)"
                             "\nDN... Direction Number (1=right,2=left,3=top,4=bottom); can be anything if not relevant"
                             "\nCS... Checksum")
    parser.add_argument('-c', '--custom', type=str, help="Takes a csv string with RGB (e.g. '255,255,255') "
                                                         "seperated by ';'. Has to have 8 * 16 colors.")
    parser.add_argument('-o', '--overwrite', type=int, help="Specifies the custom preset number (1-5) to overwrite. "
                                                            "If none is provided defaults to 1.", choices=range(1, 5),
                        default=1)
    parser.add_argument('-l', '--lock', action='store_true',
                        help="Locks or unlocks the Super/Windows Key. Unsure if it works on linux [COMING SOON]")
    args = parser.parse_args()
    # Find the USB device
    dev = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
    if dev is None:
        raise ValueError('Device not found')
    i = 0
    try:
        while dev.is_kernel_driver_active(i):
            print(f"Detaching kernel driver {i}...")
            dev.detach_kernel_driver(i)
            i = i + 1
        print("Detached all kernel drivers")
        # Set the active configuration. This step is device-specific.
        print("Setting device configuration...")
        dev.set_configuration()
        # Send the USB control transfer
        print("Sending initialization packets...")
        for packet in INIT_PACKETS:
            if packet[0] == 0x08 and packet[1] == 0x02:
                packet[7] = calculate_checksum(packet)
            send_control_transfer(dev, packet)
            time.sleep(0.1)

        if args.preset:
            packet_data = ast.literal_eval(args.preset)
        elif args.custom:
            color_packets = []
            colors_csv = str(args.custom)
            colors = colors_csv.split(";")
            cnt = 16
            for c in colors:
                if cnt == 16:
                    color_packets.append(bytearray())
                    cnt = 0
                rgb = c.split(",")
                if len(rgb) != 3:
                    print("Colors have to be groups of three in RGB format")
                    sys.exit(1)
                # the packet needs a 4th value per color.
                # idk what it is, it might be refresh rate. but it doesn't really change anything
                color_packets[-1].append(255)
                for value in rgb:
                    val_int = int(value)
                    if val_int < 0 or val_int > 255:
                        print("Colors can't be less than 0 or bigger than 255.")
                        sys.exit(1)
                    color_packets[-1].append(val_int)
                cnt += 1
            if len(color_packets) != 8 or len(color_packets[7]) != 16 * 4:
                print("Not enough packets or colors. There have to be 8 packets with 16 RGB colors.")
                sys.exit(1)
            custom_slot = 50 + args.overwrite
            send_custom_packets(dev, color_packets, custom_slot)
            packet_data = [0x08, 0x02, custom_slot, 0x0a, 0x32, 0x08, 0x04, 0]
            packet_data[7] = calculate_checksum(packet_data)
        else:
            print("No packet data found. Please start this program from index.py or provide your own data (--help)")
            sys.exit(1)
        if args.lock:
            print("Locking or unlocking Super key")
            send_control_transfer(dev, [0x0e, 0, 0, 0x12, 0, 0, 0, 0xdf])

        send_control_transfer(dev, packet_data)
        print("Packets sent successfully.")

    except usb.core.USBError as e:
        print(f"USB error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Reattach the kernel driver if it was detached
        for cnt in range(i):
            if not dev.is_kernel_driver_active(cnt):
                try:
                    print("Reattaching kernel driver...")
                    dev.attach_kernel_driver(cnt)
                except usb.core.USBError as e:
                    print(f"Could not reattach kernel driver: {e}")
        # Dispose of the USB resources
        usb.util.dispose_resources(dev)


if __name__ == "__main__":
    main()

#
# packet1 = bytearray([
#     0x00, 0x00, 0x00, 0x00,  # L_CTRL
#     0x00, 0x00, 0x00, 0x00,  # L_SHIFT
#     0x00, 0x00, 0x00, 0x00,  # CAPS
#     0x00, 0x00, 0x00, 0x00,  # TAB
#     0x00, 0x00, 0x00, 0x00,  # ^/°
#     0x00, 0x00, 0x00, 0x00,  # ESC
#     0x00, 0x00, 0x00, 0x00,  # SUPER/WIN
#     0x00, 0x00, 0x00, 0x00,  # Y
#     0x00, 0x00, 0x00, 0x00,  # A
#     0x00, 0x00, 0x00, 0x00,  # Q
#     0x00, 0x00, 0x00, 0x00,  # 1
#     0x00, 0x00, 0x00, 0x00,  # < >
#     0x00, 0x00, 0x00, 0x00,  # L_ALT
#     0x00, 0x00, 0x00, 0x00,  # X
#     0x00, 0x00, 0x00, 0x00,  # S
#     0x00, 0x00, 0x00, 0x00  # W
# ])
# packet2 = bytearray([
#     0x00, 0x00, 0x00, 0x00,  # 2
#     0x00, 0x00, 0x00, 0x00,  # F1
#     0x00, 0x00, 0x00, 0x00,  # ???
#     0x00, 0x00, 0x00, 0x00,  # C
#     0x00, 0x00, 0x00, 0x00,  # D
#     0x00, 0x00, 0x00, 0x00,  # E
#     0x00, 0x00, 0x00, 0x00,  # 3
#     0x00, 0x00, 0x00, 0x00,  # F2
#     0x00, 0x00, 0x00, 0x00,  # ???
#     0x00, 0x00, 0x00, 0x00,  # V
#     0x00, 0x00, 0x00, 0x00,  # F
#     0x00, 0x00, 0x00, 0x00,  # R
#     0x00, 0x00, 0x00, 0x00,  # 4
#     0x00, 0x00, 0x00, 0x00,  # F3
#     0x00, 0x00, 0x00, 0x00,  # SPACE
#     0x00, 0x00, 0x00, 0x00  # B
# ])
# packet3 = bytearray([
#     0x00, 0x00, 0x00, 0x00,  # G
#     0x00, 0x00, 0x00, 0x00,  # T
#     0x00, 0x00, 0x00, 0x00,  # 5
#     0x00, 0x00, 0x00, 0x00,  # F4
#     0x00, 0x00, 0x00, 0x00,  # ???
#     0x00, 0x00, 0x00, 0x00,  # N
#     0x00, 0x00, 0x00, 0x00,  # H
#     0x00, 0x00, 0x00, 0x00,  # Z
#     0x00, 0x00, 0x00, 0x00,  # 6
#     0x00, 0x00, 0x00, 0x00,  # F5
#     0x00, 0x00, 0x00, 0x00,  # ???
#     0x00, 0x00, 0x00, 0x00,  # M
#     0x00, 0x00, 0x00, 0x00,  # J
#     0x00, 0x00, 0x00, 0x00,  # U
#     0x00, 0x00, 0x00, 0x00,  # 7
#     0x00, 0x00, 0x00, 0x00  # F6
# ])
# packet4 = bytearray([
#     0x00, 0x00, 0x00, 0x00,  # ???
#     0x00, 0x00, 0x00, 0x00,  # ,
#     0x00, 0x00, 0x00, 0x00,  # K
#     0x00, 0x00, 0x00, 0x00,  # I
#     0x00, 0x00, 0x00, 0x00,  # 8
#     0x00, 0x00, 0x00, 0x00,  # F7
#     0x00, 0x00, 0x00, 0x00,  # ALT GR
#     0x00, 0x00, 0x00, 0x00,  # .
#     0x00, 0x00, 0x00, 0x00,  # L
#     0x00, 0x00, 0x00, 0x00,  # O
#     0x00, 0x00, 0x00, 0x00,  # 9
#     0x00, 0x00, 0x00, 0x00,  # F8
#     0x00, 0x00, 0x00, 0x00,  # FN
#     0x00, 0x00, 0x00, 0x00,  # -
#     0x00, 0x00, 0x00, 0x00,  # Ö
#     0x00, 0x00, 0x00, 0x00  # P
# ])
# packet5 = bytearray([
#     0x00, 0x00, 0x00, 0x00,  # 0
#     0x00, 0x00, 0x00, 0x00,  # F9
#     0x00, 0x00, 0x00, 0x00,  # MENU
#     0x00, 0x00, 0x00, 0x00,  # ???
#     0x00, 0x00, 0x00, 0x00,  # Ä
#     0x00, 0x00, 0x00, 0x00,  # Ü
#     0x00, 0x00, 0x00, 0x00,  # ß
#     0x00, 0x00, 0x00, 0x00,  # F10
#     0x00, 0x00, 0x00, 0x00,  # ???
#     0x00, 0x00, 0x00, 0x00,  # R_SHIFT
#     0x00, 0x00, 0x00, 0x00,  # #
#     0x00, 0x00, 0x00, 0x00,  # +
#     0x00, 0x00, 0x00, 0x00,  # ´ (the one next to ß and backspace)
#     0x00, 0x00, 0x00, 0x00,  # F11
#     0x00, 0x00, 0x00, 0x00,  # R_CTRL
#     0x00, 0x00, 0x00, 0x00  # ???
# ])
# packet6 = bytearray([
#     0x00, 0x00, 0x00, 0x00,  # ENTER
#     0x00, 0x00, 0x00, 0x00,  # ???
#     0x00, 0x00, 0x00, 0x00,  # BACKSPACE
#     0x00, 0x00, 0x00, 0x00,  # F12
#     0x00, 0x00, 0x00, 0x00,  # ARROW LEFT
#     0x00, 0x00, 0x00, 0x00,  # ???
#     0x00, 0x00, 0x00, 0x00,  # ???
#     0x00, 0x00, 0x00, 0x00,  # DELETE / ENTF
#     0x00, 0x00, 0x00, 0x00,  # INSERT / EINFG
#     0x00, 0x00, 0x00, 0x00,  # ???
#     0x00, 0x00, 0x00, 0x00,  # ARROW DOWN
#     0x00, 0x00, 0x00, 0x00,  # ARROW UP
#     0x00, 0x00, 0x00, 0x00,  # ??? (maybe print?)
#     0x00, 0x00, 0x00, 0x00,  # END
#     0x00, 0x00, 0x00, 0x00,  # POS 1
#     0x00, 0x00, 0x00, 0x00  # SCROLL / ROLLEN
# ])
# packet7 = bytearray([
#     0x00, 0x00, 0x00, 0x00,  # ARROW RIGHT
#     0x00, 0x00, 0x00, 0x00,  # ???
#     0x00, 0x00, 0x00, 0x00,  # ???
#     0x00, 0x00, 0x00, 0x00,  # PAGE DOWN / BILD RUNTER
#     0x00, 0x00, 0x00, 0x00,  # PAGE UP / BILD HOCH
#     0x00, 0x00, 0x00, 0x00,  # PAUSE
#     0x00, 0x00, 0x00, 0x00,  # NUM0
#     0x00, 0x00, 0x00, 0x00,  # NUM1
#     0x00, 0x00, 0x00, 0x00,  # NUM4
#     0x00, 0x00, 0x00, 0x00,  # NUM7
#     0x00, 0x00, 0x00, 0x00,  # NUM LOCK
#     0x00, 0x00, 0x00, 0x00,  # ???
#     0x00, 0x00, 0x00, 0x00,  # ???
#     0x00, 0x00, 0x00, 0x00,  # NUM2
#     0x00, 0x00, 0x00, 0x00,  # NUM5
#     0x00, 0x00, 0x00, 0x00  # NUM8
# ])
# packet8 = bytearray([
#     0x00, 0x00, 0x00, 0x00,  # NUM DIVIDE (/)
#     0x00, 0x00, 0x00, 0x00,  # ???
#     0x00, 0x00, 0x00, 0x00,  # NUM COMMA (,)
#     0x00, 0x00, 0x00, 0x00,  # NUM3
#     0x00, 0x00, 0x00, 0x00,  # NUM6
#     0x00, 0x00, 0x00, 0x00,  # NUM9
#     0x00, 0x00, 0x00, 0x00,  # NUM MULTIPLY (*)
#     0x00, 0x00, 0x00, 0x00,  # ???
#     0x00, 0x00, 0x00, 0x00,  # NUM ENTER
#     0x00, 0x00, 0x00, 0x00,  # ???
#     0x00, 0x00, 0x00, 0x00,  # NUM PLUS (+)
#     0x00, 0x00, 0x00, 0x00,  # ???
#     0x00, 0x00, 0x00, 0x00,  # NUM MINUS (-)
#     0x00, 0x00, 0x00, 0x00,  # ???
#     0x00, 0x00, 0x00, 0x00,  # ???
#     0x00, 0x00, 0x00, 0x00  # ???
# ])
