using System;
using System.Text;

namespace ApiPrinterServer.Utils
{
    public static class MatrixCommands
    {
        // Comandos básicos para Epson
        private static readonly byte[] _initialize = new byte[] { 0x1B, 0x40 }; // ESC @
        private static readonly byte[] _newLine = new byte[] { 0x0D, 0x0A }; // CR LF
        private static readonly byte[] _formFeed = new byte[] { 0x0C }; // FF
        
        // Modo condensado
        private static readonly byte[] _condensedOn = new byte[] { 0x0F }; // SI
        private static readonly byte[] _condensedOff = new byte[] { 0x12 }; // DC2
        
        // Modo expandido
        private static readonly byte[] _expandedOn = new byte[] { 0x1B, 0x57, 0x01 }; // ESC W 1
        private static readonly byte[] _expandedOff = new byte[] { 0x1B, 0x57, 0x00 }; // ESC W 0
        
        // Modo énfasis (negrita)
        private static readonly byte[] _boldOn = new byte[] { 0x1B, 0x45 }; // ESC E
        private static readonly byte[] _boldOff = new byte[] { 0x1B, 0x46 }; // ESC F
        
        // Modo subrayado
        private static readonly byte[] _underlineOn = new byte[] { 0x1B, 0x2D, 0x01 }; // ESC - 1
        private static readonly byte[] _underlineOff = new byte[] { 0x1B, 0x2D, 0x00 }; // ESC - 0
        
        // Control de líneas
        private static readonly byte[] _setLineSpacing1_6 = new byte[] { 0x1B, 0x32 }; // ESC 2
        private static readonly byte[] _setLineSpacing1_8 = new byte[] { 0x1B, 0x30 }; // ESC 0
        
        // Tabulación
        private static readonly byte[] _tab = new byte[] { 0x09 }; // HT
        
        // Propiedades públicas
        public static byte[] Initialize { get { return _initialize; } }
        public static byte[] NewLine { get { return _newLine; } }
        public static byte[] FormFeed { get { return _formFeed; } }
        public static byte[] CondensedOn { get { return _condensedOn; } }
        public static byte[] CondensedOff { get { return _condensedOff; } }
        public static byte[] ExpandedOn { get { return _expandedOn; } }
        public static byte[] ExpandedOff { get { return _expandedOff; } }
        public static byte[] BoldOn { get { return _boldOn; } }
        public static byte[] BoldOff { get { return _boldOff; } }
        public static byte[] UnderlineOn { get { return _underlineOn; } }
        public static byte[] UnderlineOff { get { return _underlineOff; } }
        public static byte[] SetLineSpacing1_6 { get { return _setLineSpacing1_6; } }
        public static byte[] SetLineSpacing1_8 { get { return _setLineSpacing1_8; } }
        public static byte[] Tab { get { return _tab; } }
        
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

        // Formato de tabla
        public static string FormatTableRow(string description, decimal quantity, decimal price, decimal subtotal)
        {
            // Formato para impresora matriz usando caracteres de ancho fijo
            return string.Format("{0,-40} {1,8:N2} {2,10:N2} {3,10:N2}",
                description.Length > 40 ? description.Substring(0, 37) + "..." : description,
                quantity,
                price,
                subtotal);
        }
    }
}
