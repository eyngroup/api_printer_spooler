using System;
using System.Text;
using System.Collections.Generic;

namespace ApiPrinterServer.Utils
{
    public static class EscposCommands
    {
        private static readonly byte[] _initialize = new byte[] { 0x1B, 0x40 };
        private static readonly byte[] _cut = new byte[] { 0x1D, 0x56, 0x41, 0x00 };
        private static readonly byte[] _newLine = new byte[] { 0x0A };
        private static readonly byte[] _feed = new byte[] { 0x1B, 0x64, 0x01 };
        
        // Alineación
        private static readonly byte[] _alignLeft = new byte[] { 0x1B, 0x61, 0x00 };
        private static readonly byte[] _alignCenter = new byte[] { 0x1B, 0x61, 0x01 };
        private static readonly byte[] _alignRight = new byte[] { 0x1B, 0x61, 0x02 };
        
        // Estilos de texto
        private static readonly byte[] _bold = new byte[] { 0x1B, 0x45, 0x01 };
        private static readonly byte[] _boldOff = new byte[] { 0x1B, 0x45, 0x00 };
        private static readonly byte[] _doubleHeight = new byte[] { 0x1B, 0x21, 0x10 };
        private static readonly byte[] _normalSize = new byte[] { 0x1B, 0x21, 0x00 };
        
        // Propiedades públicas
        public static byte[] Initialize { get { return _initialize; } }
        public static byte[] Cut { get { return _cut; } }
        public static byte[] NewLine { get { return _newLine; } }
        public static byte[] Feed { get { return _feed; } }
        public static byte[] AlignLeft { get { return _alignLeft; } }
        public static byte[] AlignCenter { get { return _alignCenter; } }
        public static byte[] AlignRight { get { return _alignRight; } }
        public static byte[] Bold { get { return _bold; } }
        public static byte[] BoldOff { get { return _boldOff; } }
        public static byte[] DoubleHeight { get { return _doubleHeight; } }
        public static byte[] NormalSize { get { return _normalSize; } }
        
        // Métodos de utilidad
        public static byte[] GetText(string text, Encoding encoding = null)
        {
            if (encoding == null)
                encoding = Encoding.GetEncoding(850); // CP850 para caracteres especiales
            return encoding.GetBytes(text);
        }

        public static byte[] CombineCommands(params byte[][] commands)
        {
            var combinedLength = 0;
            foreach (var cmd in commands)
            {
                combinedLength += cmd.Length;
            }

            var result = new byte[combinedLength];
            var offset = 0;
            foreach (var cmd in commands)
            {
                Buffer.BlockCopy(cmd, 0, result, offset, cmd.Length);
                offset += cmd.Length;
            }

            return result;
        }
    }
}
