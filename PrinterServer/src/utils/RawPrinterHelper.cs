using System;
using System.Runtime.InteropServices;

namespace ApiPrinterServer.Utils
{
    public class RawPrinterHelper : IDisposable
    {
        private IntPtr _printer = IntPtr.Zero;

        [DllImport("winspool.drv", CharSet = CharSet.Auto, SetLastError = true)]
        private static extern bool OpenPrinter(string pPrinterName, out IntPtr phPrinter, IntPtr pDefault);

        [DllImport("winspool.drv", SetLastError = true)]
        private static extern bool ClosePrinter(IntPtr hPrinter);

        [DllImport("winspool.drv", SetLastError = true)]
        private static extern bool WritePrinter(IntPtr hPrinter, IntPtr pBytes, int dwCount, out int dwWritten);

        public bool SendBytesToPrinter(string printerName, byte[] bytes)
        {
            try
            {
                if (OpenPrinter(printerName.Normalize(), out _printer, IntPtr.Zero))
                {
                    var pBytes = Marshal.AllocCoTaskMem(bytes.Length);
                    Marshal.Copy(bytes, 0, pBytes, bytes.Length);
                    
                    int written = 0;
                    var success = WritePrinter(_printer, pBytes, bytes.Length, out written);
                    Marshal.FreeCoTaskMem(pBytes);
                    
                    return success && written == bytes.Length;
                }
                return false;
            }
            catch
            {
                return false;
            }
        }

        public void Dispose()
        {
            if (_printer != IntPtr.Zero)
            {
                ClosePrinter(_printer);
                _printer = IntPtr.Zero;
            }
            GC.SuppressFinalize(this);
        }

        ~RawPrinterHelper()
        {
            Dispose();
        }
    }
}
