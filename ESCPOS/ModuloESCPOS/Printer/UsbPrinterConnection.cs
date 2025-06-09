using System;
using System.IO;
using System.Runtime.InteropServices;
using System.ComponentModel;
using System.Text;

namespace ModuloESCPOS.Printer
{
    public class UsbPrinterConnection : IDisposable
    {
        private IntPtr handle;
        private string printerName;
        public string LastError { get; private set; }

        [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Ansi)]
        private struct DOCINFOA
        {
            [MarshalAs(UnmanagedType.LPStr)]
            public string pDocName;
            [MarshalAs(UnmanagedType.LPStr)]
            public string pOutputFile;
            [MarshalAs(UnmanagedType.LPStr)]
            public string pDataType;
        }

        [DllImport("winspool.drv", EntryPoint = "OpenPrinterA", CharSet = CharSet.Ansi, SetLastError = true)]
        private static extern bool OpenPrinter([MarshalAs(UnmanagedType.LPStr)] string szPrinter, out IntPtr hPrinter, IntPtr pd);

        [DllImport("winspool.drv", EntryPoint = "ClosePrinter", SetLastError = true)]
        private static extern bool ClosePrinter(IntPtr hPrinter);

        [DllImport("winspool.drv", EntryPoint = "StartDocPrinterA", CharSet = CharSet.Ansi, SetLastError = true)]
        private static extern bool StartDocPrinter(IntPtr hPrinter, int level, ref DOCINFOA di);

        [DllImport("winspool.drv", EntryPoint = "EndDocPrinter", SetLastError = true)]
        private static extern bool EndDocPrinter(IntPtr hPrinter);

        [DllImport("winspool.drv", EntryPoint = "StartPagePrinter", SetLastError = true)]
        private static extern bool StartPagePrinter(IntPtr hPrinter);

        [DllImport("winspool.drv", EntryPoint = "EndPagePrinter", SetLastError = true)]
        private static extern bool EndPagePrinter(IntPtr hPrinter);

        [DllImport("winspool.drv", EntryPoint = "WritePrinter", SetLastError = true)]
        private static extern bool WritePrinter(IntPtr hPrinter, byte[] pBytes, int dwCount, out int dwWritten);

        public bool Connect(string printerName = "POS-80C")
        {
            try
            {
                this.printerName = printerName;
                Console.WriteLine($"Intentando conectar a impresora: {printerName}");

                if (!OpenPrinter(printerName, out handle, IntPtr.Zero))
                {
                    int error = Marshal.GetLastWin32Error();
                    LastError = new Win32Exception(error).Message;
                    Console.WriteLine($"Error al abrir impresora: {LastError} (Código: {error})");
                    return false;
                }

                Console.WriteLine("Conexión exitosa!");
                return true;
            }
            catch (Exception ex)
            {
                LastError = ex.Message;
                Console.WriteLine($"Excepción al conectar: {ex.Message}");
                return false;
            }
        }

        public bool Write(byte[] data)
        {
            if (handle == IntPtr.Zero)
            {
                LastError = "No hay conexión con la impresora";
                Console.WriteLine(LastError);
                return false;
            }

            try
            {
                // Iniciar el documento
                DOCINFOA di = new DOCINFOA
                {
                    pDocName = "Ticket ESC/POS",
                    pDataType = "RAW"
                };

                if (!StartDocPrinter(handle, 1, ref di))
                {
                    int error = Marshal.GetLastWin32Error();
                    LastError = new Win32Exception(error).Message;
                    Console.WriteLine($"Error en StartDocPrinter: {LastError} (Código: {error})");
                    return false;
                }

                // Iniciar la página
                if (!StartPagePrinter(handle))
                {
                    EndDocPrinter(handle);
                    int error = Marshal.GetLastWin32Error();
                    LastError = new Win32Exception(error).Message;
                    Console.WriteLine($"Error en StartPagePrinter: {LastError} (Código: {error})");
                    return false;
                }

                // Escribir los datos
                int bytesWritten;
                bool success = WritePrinter(handle, data, data.Length, out bytesWritten);
                
                if (!success)
                {
                    EndPagePrinter(handle);
                    EndDocPrinter(handle);
                    int error = Marshal.GetLastWin32Error();
                    LastError = new Win32Exception(error).Message;
                    Console.WriteLine($"Error al escribir: {LastError} (Código: {error})");
                    return false;
                }

                Console.WriteLine($"Bytes escritos: {bytesWritten}");

                // Finalizar la página y el documento
                if (!EndPagePrinter(handle))
                {
                    EndDocPrinter(handle);
                    int error = Marshal.GetLastWin32Error();
                    LastError = new Win32Exception(error).Message;
                    Console.WriteLine($"Error en EndPagePrinter: {LastError} (Código: {error})");
                    return false;
                }

                if (!EndDocPrinter(handle))
                {
                    int error = Marshal.GetLastWin32Error();
                    LastError = new Win32Exception(error).Message;
                    Console.WriteLine($"Error en EndDocPrinter: {LastError} (Código: {error})");
                    return false;
                }

                return true;
            }
            catch (Exception ex)
            {
                LastError = ex.Message;
                Console.WriteLine($"Excepción al escribir: {ex.Message}");
                return false;
            }
        }

        public void Dispose()
        {
            if (handle != IntPtr.Zero)
            {
                ClosePrinter(handle);
                handle = IntPtr.Zero;
            }
        }
    }
}
