#!/usr/bin/python3
#
# Copyright (C) 2019  k0np4ku
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

import sys
import os
import ntpath
import argparse
import k0np4ku.utils.binaryReader as binaryReader
import k0np4ku.lua.crypt as luacrypt
import k0np4ku.ab.crypt as ab
# File Types
_UNKNOWN = "Unknown"
_LUA = "Lua"
_BUNDLE = "AssetBundle"

# Tasks
_ENCRYPT = "Encrypt"
_DECRYPT = "Decrypt"
_COMPILE = "Compile"
_DECOMPILE = "Decompile"
_REPACK = "Repackage"
_UNPACK = "Unpackage"

class Main():
    def initialize(self):
        parser = argparse.ArgumentParser(description="-x- al-tools v1.0.0 -x-")

        parser.add_argument("--encrypt", nargs="+",
            help = "Encrypt Lua(s) or Asset Bundle(s). Can be a directory(s) that contains Lua(s) or Asset Bundle(s)")
        
        parser.add_argument("--decrypt", nargs="+",
            help = "Decrypt Lua(s) or Asset Bundle(s). Can be a directory(s) that contains Lua(s) or Asset Bundle(s)")
        
        parser.add_argument("--compile", nargs="+",
            help = "Compile Lua(s). Can be a directory(s) that contains Lua(s)")

        parser.add_argument("--decompile", nargs="+",
            help = "Decompile Lua(s). Can be a directory(s) that contains Lua(s)")

        parser.add_argument("--repack", nargs="+",
            help = "Repack Asset Bundle(s)")

        parser.add_argument("--unpack", nargs="+",
            help = "Unpack Asset Bundle(s)")

        parser.add_argument("--dir", default=None,
                    help = "Output directory. Will save to input's directory if not specified")

        args = parser.parse_args()

        if len(sys.argv) < 2:
            parser.print_help()
            return 1

        self.files = None
        self.mode = _UNKNOWN
        self.outDir = args.dir
    
        if args.encrypt:
            self.files = args.encrypt
            self.mode = _ENCRYPT
        if args.decrypt:
            self.files = args.decrypt
            self.mode = _DECRYPT
        if args.compile:
            self.files = args.compile
            self.mode = _COMPILE
        if args.decompile:
            self.files = args.decompile
            self.mode = _DECOMPILE
        if args.repack:
            self.files = args.repack
            self.mode = _REPACK
        if args.unpack:
            self.files = args.unpack
            self.mode = _UNPACK
        
        if self.files is not None and self.mode is not _UNKNOWN:
            self.validatePaths()
            
            if len(self.files) > 0:
                for f in self.files:
                    reader = binaryReader.BinaryReader()
                    reader.open(f)

                    fileType = self.determineFileType(reader)
                    reader.close()

                    if self.mode == _ENCRYPT:
                        if fileType == _LUA: self.encryptLua(f)
                        elif fileType == _BUNDLE: self.encryptBundle(f)
                    elif self.mode == _DECRYPT:
                        if fileType == _LUA: self.decryptLua(f)
                        elif fileType == _BUNDLE: self.decryptBundle(f)
                    elif self.mode == _COMPILE:
                        self.compileLua(f)
                    elif self.mode == _DECOMPILE:
                        if fileType == _LUA: self.decompileLua(f)
                        else: self.logWarning("Invalid file type for task", _DECOMPILE)
                    elif self.mode == _REPACK:
                        if fileType == _BUNDLE: self.repackBundle(f)
                        else: self.logWarning("Invalid file type for task", _REPACK)
                    elif self.mode == _UNPACK:
                        if fileType == _BUNDLE: self.unpackBundle(f)
                        else: self.logWarning("Invalid file type for task", _UNPACK)
            else:
                self.logCompleted("No valid file path found, tasks completed without doing anything...")
        return 0

    @staticmethod
    def logInfo(*message):
        print("[INFO]>", *message)

    @staticmethod
    def logWarning(*message):
        print("[WARNING]>", *message)
    
    @staticmethod
    def logCompleted(*message):
        print("[COMPLETED]>", *message)

    def validatePaths(self):
        validPaths = []
        for path in self.files:
            name = path
            path = os.path.abspath(name)
            if os.path.exists(path):
                isFile = os.path.isfile(path)
                if not isFile:
                    directory = os.listdir(path)
                    for f in directory:
                        p = os.path.join(path, f)
                        if os.path.isfile(p):
                            validPaths.append(p)
                        else: self.logWarning("Skipping", f, "inside folder", name, "because it's not a file")
                else: validPaths.append(path)
            else: self.logWarning("Skipping", ntpath.basename(path), "because it's either doesn't exists or invalid")
        self.files = validPaths

    @staticmethod
    def getHeader(reader, size = 16):
        path = None
        if isinstance(reader, str):
            path = reader
            reader = binaryReader.BinaryReader()
            reader.open(path)
        lastPos = reader.position
        if lastPos is not 0:
            reader.changePosition(0)
        header = reader.readBytes(size).hex()
        reader.changePosition(lastPos)
        if path is not None:
            reader.close()
        return header

    def determineFileType(self, reader):
        header = self.getHeader(reader)
        fileType = _UNKNOWN
        if luacrypt.isLuaEncrypted(header) or luacrypt.isLuaDecrypted(header):
            fileType = _LUA
        elif ab.isBundleEncrypted(header) or ab.isBundleDecrypted(header):
            fileType = _BUNDLE
        return fileType

    def compileLua(self, path):
        lua = luacrypt.Crypt(path, self.outDir, False)
        lua.compile()

    def decompileLua(self, path):
        lua = luacrypt.Crypt(path, self.outDir, True)
        header = self.getHeader(lua.reader)
        if luacrypt.isLuaEncrypted(header):
            self.logWarning("Lua is encrypted, decrypting...")
            #lua.decrypt()
        elif not luacrypt.isLuaEncrypted(header) and not luacrypt.isLuaDecrypted(header):
            self.logWarning("Skipping because it has an unknown header")
            return
        lua.decompile()

    def encryptLua(self, path):
        lua = luacrypt.Crypt(path, self.outDir, True)
        header = self.getHeader(lua.reader)
        if not luacrypt.isLuaDecrypted(header):
            self.logWarning("Skipping", lua.path, "because it's already encrypted")
            return
        elif not luacrypt.isLuaEncrypted(header) and not luacrypt.isLuaDecrypted(header):
            self.logWarning("Skipping", lua.path, "because it has an unknown header")
            return
        lua.encrypt()
        lua.reader.close()

    def decryptLua(self, path):
        lua = luacrypt.Crypt(path, self.outDir, True)
        header = self.getHeader(lua.reader)
        if not luacrypt.isLuaEncrypted(header):
            self.logWarning("Skipping", lua.path, "because it's already decrypted")
            return
        elif not luacrypt.isLuaEncrypted(header) and not luacrypt.isLuaDecrypted(header):
            self.logWarning("Skipping", lua.path, "because it has an unknown header")
            return
        lua.decrypt()
        lua.reader.close()

    def encryptBundle(self, path):
        bundle = ab.Crypt(path, self.outDir)
        header = self.getHeader(path)
        if not ab.isBundleDecrypted(header):
            self.logWarning("Skipping", bundle.path, "because it's already encrypted")
            return
        elif not ab.isBundleEncrypted(header) and not ab.isBundleDecrypted(header):
            self.logWarning("Skipping", bundle.path, "because it has an unknown header")
            return
        bundle.encrypt()

    def decryptBundle(self, path):
        bundle = ab.Crypt(path, self.outDir)
        header = self.getHeader(path)
        if not ab.isBundleEncrypted(header):
            self.logWarning("Skipping", bundle.path, "because it's already decrypted")
            return
        elif not ab.isBundleEncrypted(header) and not ab.isBundleDecrypted(header):
            self.logWarning("Skipping", bundle.path, "because it has an unknown header")
            return
        bundle.decrypt()

    def repackBundle(self, path):
        bundle = ab.Crypt(path, self.outDir)
        header = self.getHeader(path)
        if not ab.isBundleDecrypted(header) and ab.isBundleEncrypted(header):
            self.logWarning("Bundle is not decrypted, decrypting...")
            # bundle.decrypt()
        elif not ab.isBundleEncrypted(header) and not ab.isBundleDecrypted(header):
            self.logWarning("Skipping because it has an unknown header")
            return
        bundle.repack()

    def unpackBundle(self, path):
        bundle = ab.Crypt(path, self.outDir)
        header = self.getHeader(path)
        if not ab.isBundleDecrypted(header) and ab.isBundleEncrypted(header):
            self.logWarning("Bundle is not decrypted, decrypting...")
            # bundle.decrypt()
        elif not ab.isBundleEncrypted(header) and not ab.isBundleDecrypted(header):
            self.logWarning("Skipping because it has an unknown header")
            return
        bundle.unpack()

if __name__ == "__main__":
    main = Main()
    ret = main.initialize()
    sys.exit(ret)