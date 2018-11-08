# Redefine pack() and unpack() function to follow the order the data are sent by the Myo.
# Data are somehow inverted (start from the end)

import struct


def pack(fmt, *args):
    return struct.pack('<' + fmt, *args)  # < is for little-endian, see https://docs.python.org/2/library/struct.html


def unpack(fmt, *args):
    return struct.unpack('<' + fmt, *args)


def text(scr, font, txt, pos, clr=(255, 255, 255)):
    scr.blit(font.render(txt, True, clr), pos)
