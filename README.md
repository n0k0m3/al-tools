# Azur Lane Tools
A small tool for working with Azur Lane Lua and Asset Bundle. Still need a bit adjustment, but whatever. It's still usable.

For the autopatcher, refer to the following repository:\
https://github.com/n0k0m3/Archive-Azur-Lane-Scripts-Autopatcher \ (or archived repo from k0np4ku)

Azur Lane has changed its scripting backend from **Mono** to **il2cpp**, meaning that you couldn't modify their `Assembly-CSharp.dll` and inject a third-party dll. However, you can still use hook method, which I've and will never try because I'm not a muh h4x0r. So, unless they actually care about cheaters, the old autopatcher will still works.

## Prerequisites
- Python 3+ (Probably 3.5 or newer)
- .NET Framework 4.6.1 or newer

## Download
https://github.com/k0np4ku/al-tools/releases

## Commands
```usage: main.py [-h] [--encrypt ENCRYPT [ENCRYPT ...]]
               [--decrypt DECRYPT [DECRYPT ...]]
               [--compile COMPILE [COMPILE ...]]
               [--decompile DECOMPILE [DECOMPILE ...]]
               [--repack REPACK [REPACK ...]] [--unpack UNPACK [UNPACK ...]]
               [--dir DIR] [--rewrite]

-x- al-tools v1.0.0 -x-

optional arguments:
  -h, --help            show this help message and exit
  --encrypt ENCRYPT [ENCRYPT ...]
                        Encrypt Lua(s) or Asset Bundle(s). Can be a
                        directory(s) that contains Lua(s) or Asset Bundle(s)
  --decrypt DECRYPT [DECRYPT ...]
                        Decrypt Lua(s) or Asset Bundle(s). Can be a
                        directory(s) that contains Lua(s) or Asset Bundle(s)
  --compile COMPILE [COMPILE ...]
                        Compile Lua(s). Can be a directory(s) that contains
                        Lua(s)
  --decompile DECOMPILE [DECOMPILE ...]
                        Decompile Lua(s). Can be a directory(s) that contains
                        Lua(s)
  --repack REPACK [REPACK ...]
                        Repack Asset Bundle(s)
  --unpack UNPACK [UNPACK ...]
                        Unpack Asset Bundle(s)
  --dir DIR             Output directory. Will save to input's directory if
                        not specified
  --rewrite             (Default: False) Rewrite if a file with the same name
                        as output is exists, else will add a suffix
```

## Example
```
// Encrypt Asset Bundle
$ py main.py --encrypt scripts

// Decrypt Asset Bundle
$ py main.py --decrypt scripts

// Unpack Asset Bundle
$ py main.py --unpack scripts --dir tmp

// Repack Asset Bundle
$ py main.py --repack tmp/scripts

// Encrypt lua
$ py main.py --encrypt tmp/*/*/*/weapon_property.lua.txt

// Decrypt lua
$ py main.py --decrypt tmp/*/*/*/weapon_property.lua.txt

// Compile lua
$ py main.py --compile tmp/*/*/*/weapon_property.lua.txt

// Decompile lua
$ py main.py --decompile tmp/*/*/*/weapon_property.lua.txt
```

## License
```
Copyright (C) 2019  k0np4ku

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
```
