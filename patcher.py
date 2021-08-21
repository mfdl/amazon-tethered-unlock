#!/usr/bin/env python3
#
# Copyright 2021 Roger Ortiz
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import os

if sys.version_info[1] < 9:
    raise RuntimeError("[!] Python 3.9+ is required.")

help_message = f"[?] Usage: {sys.argv[0]} [pl|lk] <input> <output>"

# PL 0 -> Android 9 (sheldon, maverick, onyx) - OK - mov.W R4,#0x0
# PL 1 -> Android 7 (cupcake, mantis, karnak) - OK - MOV.W R5,#0x0
# PL 2 -> Android 5 (suez, douglas, sloane) - OK - MOV.W R4,#0x0
LK_VERIFY_ON = [b'yDY\x9aO\xf0\xff4', b'\x01\xe0O\xf0\xff5(F', b'\x01\xe0O\xf0\xff4 F']
LK_VERIFY_OFF = [b'yDY\x9aO\xf0\x00\x04', b'\x01\xe0O\xf0\x00\x05(F', b'\x01\xe0O\xf0\x00\x04 F']

# LK 1 -> Android 7 (cupcake, mantis, karnak) - TBD - MOV.W R8,#0x0
# PL 2 -> Android 5 (suez, douglas, sloane) - OK - MOV.EQ r0,#0x1
# LK 3 -> Android 9 (sheldon, maverick, onyx) - TBD - ???
AMZN_IMAGE_VERIFY_ON = [b'O\xf0\x00\x08\x10\xe0)F']
AMZN_IMAGE_VERIFY_OFF = [b'O\xf0\x01\x08\x10\xe0)F']

def quit(i, o, e):
    """
    Custom wrapper for the exit() function.
    :param i: input file
    :param o: output file
    :param e: exit text/code
    """
    i.close()
    o.close()
    sys.exit(e)

def is_pl_verify_enabled(data):
    """
    Checks whether LK verification is enabled on given PL data.
    :param data: VERIFY_LK return value
    :returns: True/False
    """
    return (True if data == b'\xff' else False)

def is_amzn_image_verify_enabled(data):
    """
    Checks whether amzn_image_verify is enabled on given LK data.
    :param data: amzn_image_verify return value
    :returns: True/False
    """
    return (True if data == b'\x00' else False)

def patch_bit(input_file, output_file, offset, bit):
    """
    Modify the specified bit from the specified file and 
    write the output data to the specified file
    :param input_file: Input file
    :param output_file: Output file
    :offset: Offset of the bit you want to modify
    :bit: New data
    """
    input_file.seek(0)
    output_file.seek(0)

    output_file.write(input_file.read()) # orig_data
    output_file.seek(offset) # to
    output_file.write(bit) # bit

def patch_lk(input_file, output_file):
    """
    Patches the given Preloader image to disable boot/recovery images verification.
    :returns: nothing
    """
    input_file.seek(0)
    DATA = input_file.read()
    OFFSET = -1

    for _off in AMZN_IMAGE_VERIFY_ON:
        OFFSET = DATA.find(_off)
        if OFFSET != -1:
            TYPE = (0 if b'O\xf0' in _off else 1)
            break
    
    if OFFSET == -1:
        for _off in AMZN_IMAGE_VERIFY_OFF:
            OFFSET = DATA.find(_off)
            if OFFSET != -1:
                TYPE = (0 if b'O\xf0' in _off else 1)
                break
        
        if OFFSET == -1:
            quit(input_file, output_file, "[-] Couldn't find amzn_image_verify")

    print(f"[?] LK with type {TYPE} detected.")

    input_file.seek(OFFSET + 8)
    amzn_image_verify = is_amzn_image_verify_enabled(input_file.read(1))

    print(f"[?] amzn_image_verify: {amzn_image_verify} ({hex(OFFSET)})")

    if amzn_image_verify:
        print("[*] Disabling amzn_image_verify...")
        patch_bit(input_file, output_file, OFFSET, AMZN_IMAGE_VERIFY_OFF[TYPE])
    else:
        print("[*] Enabling amzn_image_verify...")
        patch_bit(input_file, output_file, OFFSET, AMZN_IMAGE_VERIFY_ON[TYPE])

    print(f"[+] Successfully patched LK and saved it as {sys.argv[3]}!")
    quit(input_file, output_file, 0)

def patch_pl(input_file, output_file):
    """
    Patches the given Preloader image to disable LK verification.
    :returns: nothing
    """
    input_file.seek(0)
    DATA = input_file.read()
    OFFSET = -1

    for _off in LK_VERIFY_ON:
        OFFSET = DATA.find(_off)
        if OFFSET != -1:
            TYPE = (0 if _off == LK_VERIFY_ON[0] else 1 if _off == LK_VERIFY_ON[1] else 2 if _off == LK_VERIFY_ON[2] else -1)
            break
    
    if OFFSET == -1:
        for _off in LK_VERIFY_OFF:
            OFFSET = DATA.find(_off)
            if OFFSET != -1:
                TYPE = (0 if _off == LK_VERIFY_OFF[0] else 1 if _off == LK_VERIFY_OFF[1] else 2 if _off == LK_VERIFY_OFF[2] else -1)
                break
        
        if OFFSET == -1:
            quit(input_file, output_file, "[-] Couldn't find LK_VERIFY")

    print(f"[?] PL with type {TYPE} detected.")

    input_file.seek(OFFSET + 4)
    lk_verify = is_pl_verify_enabled(input_file.read(1))

    print(f"[?] LK verification: {lk_verify} ({hex(OFFSET)})")

    if lk_verify:
        print("[*] Disabling LK verification...")
        patch_bit(input_file, output_file, OFFSET, LK_VERIFY_OFF[TYPE])
    else:
        print("[*] Enabling LK verification...")
        patch_bit(input_file, output_file, OFFSET, LK_VERIFY_ON[TYPE])

    print(f"[+] Successfully patched PL and saved it as {sys.argv[3]}!")
    quit(input_file, output_file, 0)

def main():
    input_file = sys.argv[2]
    output_file = sys.argv[3]
    
    if not os.path.isfile(input_file):
        sys.exit(f"[-] Couldn't find {input_file}!")

    try:
        input_file = open(input_file, "rb")
        output_file = open(output_file, "wb")
    except Exception as e:
        sys.exit(f"[-] Couldn't open files ({e}!")

    if sys.argv[1] == "lk":
        patch_lk(input_file, output_file)
    elif sys.argv[1] == "pl":
        patch_pl(input_file, output_file)
    else:
        sys.exit(f"[-] Unsupported opperation {sys.argv[1]}!")

if __name__ == "__main__":
    if(len(sys.argv) < 4):
    	sys.exit(help_message)
    else:
        main()
