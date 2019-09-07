#  Copyright (C) 2019  k0np4ku
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import io
import os
import sys

class BinaryReader():
    def __init__(self):
        self.stream = None
        self.name = None
        self.size = 0
        self.position = 0

    def open(self, fileName):
        self.stream = io.open(fileName, "rb")
        self.name = fileName
        self.size = os.stat(fileName).st_size
        return self.stream

    def write(self, fileName, byteArr):
        file = io.open(fileName, "wb")
        file.write(byteArr)
        file.close()

    def close(self):
        self.stream.close()
        self.size = 0
        self.position = 0

    def isIndexInRange(self, size = 1):
        return self.position + size <= self.size

    def readBytes(self, size = 1):
        if not self.isIndexInRange(size):
            raise IOError("Unexpected EOF while trying to read {0} bytes".format(size))
        data = self.stream.read(size)
        self.position += len(data) #size
        return data

    def readByte(self, size = 1):
        if not self.isIndexInRange(size):
            raise IOError("Unexpected EOF while trying to read {0} bytes".format(size))
        data = self.stream.read(size)
        self.position += len(data)
        return int.from_bytes(data, byteorder=sys.byteorder, signed=False)

    def readUleb128(self):
        value = self.readByte()
        if value >= 0x80:
            bitshift = 0
            value &= 0x7F
            while True:
                byte = self.readByte()
                bitshift += 7
                value |= (byte & 0x7F) << bitshift
                if byte < 0x80:
                    break
        return value

    def readAllBytes(self):
        lastPos = self.position
        self.stream.seek(0)
        data = self.stream.read()
        self.changePosition(lastPos)
        return bytearray(data)

    def changePosition(self, position):
        self.position = position
        self.stream.seek(self.position)