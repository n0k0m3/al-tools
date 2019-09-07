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

import os
import ntpath
import subprocess
from shutil import copyfile

_bundleEncryptedPattern = "c7d5fc1f4c929455850316a37f7b8b55"
_bundleDecryptedPattern = "556e69747946530000000006352e782e"

class Crypt():
    def __init__(self, path, outDir):
        self.path = path
        self.outDir = outDir

    def encrypt(self):
        args = ["k0np4ku/ab/bin/crypt-cli/crypt-cli", "-i", self.path, "-e", "-l"]
        if self.outDir is not None:
            args.append("--dir")
            args.append(self.outDir)
        subprocess.call(args)

    def decrypt(self):
        args = ["k0np4ku/ab/bin/crypt-cli/crypt-cli", "-i", self.path, "-d", "-l"]
        if self.outDir is not None:
            args.append("--dir")
            args.append(self.outDir)
        subprocess.call(args)

    def repack(self):
        if self.outDir is not None:
            self._buildPath()
        args = ["k0np4ku/ab/bin/unityex/unityex", "import", self.path]
        subprocess.call(args)

    def unpack(self):
        if self.outDir is not None:
            self._buildPath()
        args = ["k0np4ku/ab/bin/unityex/unityex", "export", self.path]
        subprocess.call(args)

    def _buildPath(self):
        outputDirectory = os.path.dirname(self.path)
        if self.outDir is not None:
            outputDirectory = os.path.abspath(self.outDir)
            if not os.path.exists(outputDirectory):
                os.makedirs(outputDirectory)
        fileName = ntpath.basename(self.path)
        out = os.path.join(outputDirectory, fileName)
        copyfile(self.path, out)
        self.path = out

def isBundleEncrypted(header):
    return header[:32] == _bundleEncryptedPattern

def isBundleDecrypted(header):
    return header[:32] == _bundleDecryptedPattern