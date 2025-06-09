using System;
using System.Text;
using System.Collections.Generic;
using System.Drawing;
using System.IO;

namespace ModuloESCPOS.Commands
{
    public static class EscPosCommands
    {
        // Comandos de inicialización y control
        public static byte[] InitializePrinter => new byte[] { 0x1B, 0x40 }; // ESC @
        public static byte[] Cut => new byte[] { 0x1D, 0x56, 0x41, 0x0A }; // GS V A + Line feed
        
        // Formato de texto
        public static byte[] AlignLeft => new byte[] { 0x1B, 0x61, 0x00 }; // ESC a 0
        public static byte[] AlignCenter => new byte[] { 0x1B, 0x61, 0x01 }; // ESC a 1
        public static byte[] AlignRight => new byte[] { 0x1B, 0x61, 0x02 }; // ESC a 2
        
        public static byte[] Bold => new byte[] { 0x1B, 0x45, 0x01 }; // ESC E 1
        public static byte[] BoldOff => new byte[] { 0x1B, 0x45, 0x00 }; // ESC E 0
        
        public static byte[] DoubleHeight => new byte[] { 0x1B, 0x21, 0x10 }; // ESC ! 16
        public static byte[] NormalHeight => new byte[] { 0x1B, 0x21, 0x00 }; // ESC ! 0
        
        public static byte[] CondensedMode => new byte[] { 0x1B, 0x21, 0x01 }; // ESC ! 1
        public static byte[] NormalMode => new byte[] { 0x1B, 0x21, 0x00 }; // ESC ! 0

        // Tamaño de fuente
        public static byte[] FontSizeNormal => new byte[] { 0x1D, 0x21, 0x00 }; // GS ! 0
        public static byte[] FontSizeDouble => new byte[] { 0x1D, 0x21, 0x11 }; // GS ! 17 (ancho y alto dobles)
        
        // Espaciado
        public static byte[] SetLineSpacing(byte spacing) => new byte[] { 0x1B, 0x33, spacing }; // ESC 3 n
        public static byte[] ResetLineSpacing => new byte[] { 0x1B, 0x32 }; // ESC 2
        
        // Utilidades
        public static byte[] NewLine => new byte[] { 0x0A }; // LF
        public static byte[] Feed(byte lines) => new byte[] { 0x1B, 0x64, lines }; // ESC d n

        // Comandos para códigos de barras
        public static byte[] PrintBarcode(string data, byte type, byte height, byte width, bool hri)
        {
            var commands = new List<byte>();
            
            // HRI position (below barcode)
            commands.Add(0x1D);
            commands.Add(0x48);
            commands.Add((byte)(hri ? 2 : 0));
            
            // Barcode height
            commands.Add(0x1D);
            commands.Add(0x68);
            commands.Add(height);
            
            // Barcode width
            commands.Add(0x1D);
            commands.Add(0x77);
            commands.Add(width);
            
            // Print barcode
            commands.Add(0x1D);
            commands.Add(0x6B);
            commands.Add(type); // Type (0-6: UPC-A,UPC-E,EAN13,EAN8,CODE39,ITF,CODABAR, 73: CODE128)
            commands.Add((byte)data.Length);
            commands.AddRange(Encoding.ASCII.GetBytes(data));
            
            return commands.ToArray();
        }

        // Comandos para QR Code
        public static byte[] PrintQRCode(string data, byte size, byte errorCorrection)
        {
            var commands = new List<byte>();
            var qrData = Encoding.UTF8.GetBytes(data);
            var length = qrData.Length + 3;
            
            // Select model (model 2)
            commands.AddRange(new byte[] { 0x1D, 0x28, 0x6B, 0x04, 0x00, 0x31, 0x41, 0x32, 0x00 });
            
            // Set size
            commands.AddRange(new byte[] { 0x1D, 0x28, 0x6B, 0x03, 0x00, 0x31, 0x43, size });
            
            // Set error correction
            commands.AddRange(new byte[] { 0x1D, 0x28, 0x6B, 0x03, 0x00, 0x31, 0x45, errorCorrection });
            
            // Store data
            commands.AddRange(new byte[] { 0x1D, 0x28, 0x6B });
            commands.Add((byte)(length & 0xFF));
            commands.Add((byte)((length >> 8) & 0xFF));
            commands.Add(0x31);
            commands.Add(0x50);
            commands.Add(0x30);
            commands.AddRange(qrData);
            
            // Print
            commands.AddRange(new byte[] { 0x1D, 0x28, 0x6B, 0x03, 0x00, 0x31, 0x51, 0x30 });
            
            return commands.ToArray();
        }

        // Comandos para imágenes
        private static int Clamp(int value, int min, int max)
        {
            return value < min ? min : (value > max ? max : value);
        }

        private static Bitmap ApplyDithering(Bitmap source)
        {
            var result = new Bitmap(source.Width, source.Height);
            
            // Convertir a escala de grises y aplicar dithering Floyd-Steinberg
            for (int y = 0; y < source.Height; y++)
            {
                for (int x = 0; x < source.Width; x++)
                {
                    var pixel = source.GetPixel(x, y);
                    var alpha = pixel.A / 255.0;
                    // Convertir a escala de grises teniendo en cuenta la transparencia
                    var grayScale = (pixel.R * 0.299 + pixel.G * 0.587 + pixel.B * 0.114) * alpha + (1 - alpha) * 255;
                    var oldPixel = Clamp((int)grayScale, 0, 255);
                    var newPixel = oldPixel < 127 ? 0 : 255;
                    result.SetPixel(x, y, Color.FromArgb(255, newPixel, newPixel, newPixel));

                    var error = oldPixel - newPixel;

                    // Distribuir el error a los píxeles vecinos
                    if (x + 1 < source.Width)
                    {
                        var pixel1 = source.GetPixel(x + 1, y);
                        var gray1 = (pixel1.R * 0.299 + pixel1.G * 0.587 + pixel1.B * 0.114) * (pixel1.A / 255.0) + (1 - pixel1.A / 255.0) * 255;
                        gray1 = Clamp((int)(gray1 + error * 7 / 16.0), 0, 255);
                        source.SetPixel(x + 1, y, Color.FromArgb(pixel1.A, (int)gray1, (int)gray1, (int)gray1));
                    }

                    if (y + 1 < source.Height)
                    {
                        if (x - 1 >= 0)
                        {
                            var pixel2 = source.GetPixel(x - 1, y + 1);
                            var gray2 = (pixel2.R * 0.299 + pixel2.G * 0.587 + pixel2.B * 0.114) * (pixel2.A / 255.0) + (1 - pixel2.A / 255.0) * 255;
                            gray2 = Clamp((int)(gray2 + error * 3 / 16.0), 0, 255);
                            source.SetPixel(x - 1, y + 1, Color.FromArgb(pixel2.A, (int)gray2, (int)gray2, (int)gray2));
                        }

                        var pixel3 = source.GetPixel(x, y + 1);
                        var gray3 = (pixel3.R * 0.299 + pixel3.G * 0.587 + pixel3.B * 0.114) * (pixel3.A / 255.0) + (1 - pixel3.A / 255.0) * 255;
                        gray3 = Clamp((int)(gray3 + error * 5 / 16.0), 0, 255);
                        source.SetPixel(x, y + 1, Color.FromArgb(pixel3.A, (int)gray3, (int)gray3, (int)gray3));

                        if (x + 1 < source.Width)
                        {
                            var pixel4 = source.GetPixel(x + 1, y + 1);
                            var gray4 = (pixel4.R * 0.299 + pixel4.G * 0.587 + pixel4.B * 0.114) * (pixel4.A / 255.0) + (1 - pixel4.A / 255.0) * 255;
                            gray4 = Clamp((int)(gray4 + error * 1 / 16.0), 0, 255);
                            source.SetPixel(x + 1, y + 1, Color.FromArgb(pixel4.A, (int)gray4, (int)gray4, (int)gray4));
                        }
                    }
                }
            }

            return result;
        }

        public static byte[] PrintImage(string imagePath, int maxWidth)
        {
            using (var originalBitmap = new Bitmap(imagePath))
            {
                // Crear un bitmap con fondo blanco
                var bitmap = new Bitmap(originalBitmap.Width, originalBitmap.Height, System.Drawing.Imaging.PixelFormat.Format32bppArgb);
                using (var g = Graphics.FromImage(bitmap))
                {
                    g.Clear(Color.White);
                    g.DrawImage(originalBitmap, 0, 0, originalBitmap.Width, originalBitmap.Height);
                }

                // Redimensionar si es necesario
                var width = bitmap.Width;
                var height = bitmap.Height;
                
                if (width > maxWidth)
                {
                    var ratio = (double)maxWidth / width;
                    width = maxWidth;
                    height = (int)(height * ratio);
                }

                var resized = new Bitmap(bitmap, new Size(width, height));
                
                // Aplicar dithering
                var dithered = ApplyDithering(resized);
                
                // Convertir a formato de impresora
                var dots = new List<byte>();
                
                for (int y = 0; y < dithered.Height; y++)
                {
                    for (int x = 0; x < dithered.Width; x += 8)
                    {
                        byte dot = 0;
                        for (int b = 0; b < 8; b++)
                        {
                            if (x + b < dithered.Width)
                            {
                                var pixel = dithered.GetPixel(x + b, y);
                                if (pixel.R < 127) // Ya está en blanco y negro después del dithering
                                {
                                    dot |= (byte)(1 << (7 - b));
                                }
                            }
                        }
                        dots.Add(dot);
                    }
                }

                var commands = new List<byte>();
                var bytesPerLine = (width + 7) / 8;
                
                commands.Add(0x1D);
                commands.Add(0x76);
                commands.Add(0x30);
                commands.Add(0x00);
                commands.Add((byte)(bytesPerLine & 0xFF));
                commands.Add((byte)((bytesPerLine >> 8) & 0xFF));
                commands.Add((byte)(height & 0xFF));
                commands.Add((byte)((height >> 8) & 0xFF));
                commands.AddRange(dots);
                
                return commands.ToArray();
            }
        }

        // Método para combinar comandos
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

        // Método para convertir texto a bytes
        public static byte[] GetTextBytes(string text)
        {
            return Encoding.GetEncoding(850).GetBytes(text + "\n");
        }

        // Método para crear una línea de caracteres
        public static byte[] CreateLine(char character = '-', int length = 42)
        {
            return GetTextBytes(new string(character, length));
        }
    }
}
