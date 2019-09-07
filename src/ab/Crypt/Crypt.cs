/*
 * Copyright (C) 2019  k0np4ku
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

using CommandLine;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text.RegularExpressions;

// ReSharper disable AssignNullToNotNullAttribute
// ReSharper disable PossibleNullReferenceException

namespace k0np4ku
{
    internal class Options
    {
        [Option('i', "input", Required = true, HelpText = "File(s) to be processed")]
        public IEnumerable<string> InputFiles { get; set; }

        [Option('o', "output", HelpText = "Output file(s) name")]
        public IEnumerable<string> OutputName { get; set; }

        [Option("dir", HelpText = "Output directory. Will save to input's directory if not specified")]
        public string OutputDirectory { get; set; }

        [Option('l', "log", Default = false, HelpText = "Print logs to console")]
        public bool Log { get; set; }

        [Option('e', "encrypt", HelpText = "Encrypt Asset Bundle(s)")]
        public bool Encrypt { get; set; }

        [Option('d', "decrypt", HelpText = "Decrypt Asset Bundle(s)")]
        public bool Decrypt { get; set; }
    }

    internal class Crypt
    {
        private static readonly byte[] Decrypted, Encrypted;
        private static readonly object Instance;
        private static bool _isLog;

        static Crypt()
        {
            if (Decrypted == null)
            {
                Decrypted = new byte[] {
                    0x55, 0x6E, 0x69, 0x74, 0x79, 0x46, 0x53, 0x00,
                    0x00, 0x00, 0x00, 0x06, 0x35, 0x2E, 0x78, 0x2E
                };
            }

            if (Encrypted == null)
            {
                Encrypted = new byte[] {
                    0xC7, 0xD5, 0xFC, 0x1F, 0x4C, 0x92, 0x94, 0x55,
                    0x85, 0x03, 0x16, 0xA3, 0x7F, 0x7B, 0x8B, 0x55
                };
            }

            if (Instance == null)
            {
                var assembly = Assembly.Load(Properties.Resources.Salt);
                Instance = Activator.CreateInstance(assembly.GetType("LL.Salt"));
            }
        }

        private static void Main(string[] args)
        {
            Parser.Default.ParseArguments<Options>(args).WithParsed(ParseOptions);
        }

        private static void Print(string message)
        {
            if (_isLog)
                Console.Write(message);
        }

        private static void PrintInfo(string message)
        {
            if (_isLog)
                Console.Write($@"[INFO]> {message}");
        }

        private static void PrintWarning(string message)
        {
            if (_isLog)
                Console.WriteLine($@"[WARNING]> {message}");
        }

        private static void PrintCompleted(string message)
        {
            if (_isLog)
                Console.WriteLine($@"[COMPLETED]> {message}");
        }

        private static void ParseOptions(Options options)
        {
            _isLog = options.Log;

            bool isEncrypt = options.Encrypt,
                isDecrypt = options.Decrypt;

            if (isEncrypt && isDecrypt)
                throw new Exception("You can only use one task mode");

            var filePaths = options.InputFiles;
            var validFilePaths = new List<string>();

            foreach (var path in filePaths)
            {
                var filePath = Path.GetFullPath(path);
                var fileName = Path.GetFileName(filePath);
                var isExists = File.Exists(filePath);

                if (!isExists)
                {
                    PrintWarning($"Skipping {fileName} because it's either doesn't exists or invalid");
                    filePath = Path.Combine(Path.GetDirectoryName(Assembly.GetEntryAssembly().Location), filePath);
                    isExists = File.Exists(filePath);
                }

                if (isExists)
                    validFilePaths.Add(filePath);
            }

            if (validFilePaths.Count > 0)
            {
                if (isEncrypt)
                    DoEncryption(validFilePaths, options.OutputName.ToList(), options.OutputDirectory);
                else
                    DoDecryption(validFilePaths, options.OutputName.ToList(), options.OutputDirectory);

                PrintCompleted("Asset Bundle operation has been completed");
            }
            else
                PrintCompleted("No valid file path found, tasks completed without doing anything...");
        }

        private static void DoEncryption(IReadOnlyList<string> files, IReadOnlyList<string> output, string outDir)
        {
            var fileCount = files.Count;
            for (var i = 0; i < fileCount; i++)
            {
                var currentFilePath = files[i];
                var fileName = Path.GetFileName(currentFilePath);

                PrintInfo($"Encrypting {fileName}");
                var bytes = File.ReadAllBytes(currentFilePath);
                var skip = false;

                if (Compare(bytes, Encrypted) || !Compare(bytes, Decrypted))
                {
                    Print(" <Skipped>\n");
                    PrintWarning($"The following file is already encrypted or has a header that doesn't match the pattern of an encrypted file: {fileName}");
                    skip = true;
                }

                if (skip)
                    continue;

                var method = Instance.GetType().GetMethod("Make", BindingFlags.Static | BindingFlags.Public);
                bytes = (byte[])method.Invoke(Instance, new object[] { bytes, true });

                var finalOutDir = !string.IsNullOrEmpty(outDir) ? Path.GetFullPath(outDir) : Path.GetDirectoryName(currentFilePath);
                if (!Directory.Exists(finalOutDir))
                    Directory.CreateDirectory(finalOutDir);

                var finalFileName = i < output.Count ? output[i] : fileName;
                var saveDir = Path.Combine(finalOutDir, finalFileName);

                File.WriteAllBytes(saveDir, bytes);
                Print(" <OK>\n");
            }
        }

        private static void DoDecryption(IReadOnlyList<string> files, IReadOnlyList<string> output, string outDir)
        {
            var fileCount = files.Count;
            for (var i = 0; i < fileCount; i++)
            {
                var currentFilePath = files[i];
                var fileName = Path.GetFileName(currentFilePath);

                PrintInfo($"Decrypting {fileName}");
                var bytes = File.ReadAllBytes(currentFilePath);
                var skip = false;

                if (Compare(bytes, Decrypted) || !Compare(bytes, Encrypted))
                {
                    Print(" <Skipped>\n");
                    PrintWarning($"The following file is already decrypted or has a header that doesn't match the pattern of an encrypted file: {fileName}");
                    skip = true;
                }

                if (skip)
                    continue;

                var method = Instance.GetType().GetMethod("Make", BindingFlags.Static | BindingFlags.Public);
                bytes = (byte[])method.Invoke(Instance, new object[] { bytes, false });

                var finalOutDir = !string.IsNullOrEmpty(outDir) ? Path.GetFullPath(outDir) : Path.GetDirectoryName(currentFilePath);
                if (!Directory.Exists(finalOutDir))
                    Directory.CreateDirectory(finalOutDir);

                var finalFileName = i < output.Count ? output[i] : fileName;
                var saveDir = Path.Combine(finalOutDir, finalFileName);

                File.WriteAllBytes(saveDir, bytes);
                Print(" <OK>\n");
            }
        }

        private static bool Compare(IReadOnlyList<byte> b1, byte[] b2)
        {
            var length = b2.Length;
            for (var i = 0; i < length; i++)
            {
                if (b1[i] != b2[i])
                    return false;
            }

            return true;
        }
    }
}