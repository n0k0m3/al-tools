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
import k0np4ku.utils.binaryReader as binaryReader
import ljd.rawdump.parser
import ljd.ast.builder
import ljd.ast.validator
import ljd.ast.locals
import ljd.ast.slotworks
import ljd.ast.unwarper
import ljd.ast.mutator
import ljd.lua.writer


_luaEncryptedPattern = "1b4c4a80"
_luaDecryptedPattern = "1b4c4a02"

_enc = open("k0np4ku/lua/bin/enc", "rb")
enc = _enc.read()
_enc.close()

_dec = open("k0np4ku/lua/bin/dec", "rb")
dec = _dec.read()
_dec.close()

class Crypt():
    def __init__(self, path, outDir, u = False):
        self.path = path
        self.outDir = outDir
        if u:
            self.reader = binaryReader.BinaryReader()
            self.reader.open(path)
            self.bytes = self.reader.readAllBytes()

    def encrypt(self):
        self._readHeader()
        self.bytes[3] = 128
        self._readPrototype(self._encrypt)
        self.reader.write(self._buildPath("_enc"), self.bytes)

    def decrypt(self):
        self._readHeader()
        self.bytes[3] = 2
        self._readPrototype(self._decrypt)
        self.reader.write(self._buildPath(), self.bytes)

    def compile(self):
        args = ["k0np4ku/lua/bin/luajit/luajit", "-b", self.path, self.path]
        subprocess.call(args)

    def decompile(self):
        header, prototype = ljd.rawdump.parser.parse(self.path)
        if not prototype:
            return
        ast = ljd.ast.builder.build(prototype)
        assert ast is not None
        ljd.ast.validator.validate(ast, warped=True)
        ljd.ast.mutator.pre_pass(ast)
        ljd.ast.locals.mark_locals(ast)
        try:
            ljd.ast.slotworks.eliminate_temporary(ast)
        except:
            raise
        ljd.ast.unwarper.unwarp(ast)
        ljd.ast.locals.mark_local_definitions(ast)
        try:
            ljd.ast.validator.validate(ast, warped=False)
        except:
            raise
        with open(self.path, "w", encoding="utf8") as out:
            ljd.lua.writer.write(out, ast)

    def _readHeader(self):
        magic = self.reader.readBytes(3)
        version = self.reader.readByte()
        bits = self.reader.readUleb128()
        is_stripped = bits & 0b00000010
        if not is_stripped:
            length = self.reader.readUleb128()
            header.name = self.reader.read_bytes(length).decode("utf8")

    def _readPrototype(self, callback = None):
        while self.reader.position < self.reader.size:
            size = self.reader.readUleb128()
            if size == 0:
                break
            nextPos = self.reader.position + size
            bits = self.reader.readByte()

            arguments_count = self.reader.readByte()
            framesize = self.reader.readByte()
            upvalues_count = self.reader.readByte()
            complex_constants_count = self.reader.readUleb128()
            numeric_constants_count = self.reader.readUleb128()
            instructions_count = self.reader.readUleb128()

            start = self.reader.position
            callback(start, instructions_count)

            self.reader.changePosition(nextPos)

    def _encrypt(self, start, count):
        result = start + 4
        for i in range(count):
            v3 = self.bytes[result - 4]
            result += 4
            v4 = self.bytes[result - 7] ^ i
            self.bytes[result - 8] = enc[v3] ^ (v4 & 0xFF)

    def _decrypt(self, start, count):
        result = start + 4
        for i in range(count):
            v1 = self.bytes[result - 4]
            result += 4
            v2 = self.bytes[result - 7] ^ v1 ^ (i & 0xFF)
            self.bytes[result - 8] = dec[v2]

    def _buildPath(self):
        outputDirectory = os.path.dirname(self.path)
        if self.outDir is not None:
            outputDirectory = os.path.abspath(self.outDir)
            if not os.path.exists(outputDirectory):
                os.makedirs(outputDirectory)
        fileName = ntpath.basename(self.path)
        out = os.path.join(outputDirectory, fileName)
        return out

def isLuaEncrypted(header):
    return header[:8] == _luaEncryptedPattern

def isLuaDecrypted(header):
    return header[:8] == _luaDecryptedPattern