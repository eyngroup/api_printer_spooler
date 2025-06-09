using System;
using System.Text;
using System.Threading.Tasks;
using System.Runtime.InteropServices;
using Newtonsoft.Json.Linq;
using Microsoft.Extensions.Logging;
using ApiPrinterServer.Interfaces;

namespace ApiPrinterServer.Fiscal
{
    public class PnpFiscalPrinter : IFiscalPrinter
    {
        private readonly ILogger _logger;
        private IntPtr _dllHandle;
        private bool _isInitialized;
        private string _port;
        private bool _isOpen;

        // Delegados para los métodos del DLL
        private delegate int OpenPortDelegate(string port);
        private delegate int ClosePortDelegate();
        private delegate int CheckPrinterStatusDelegate();
        private delegate int GetStatusErrorDelegate(ref int status, ref int error);
        private delegate int SendCommandDelegate(string cmd);
        private delegate int GetResponseDelegate(StringBuilder response, int size);

        private OpenPortDelegate _OpenPort;
        private ClosePortDelegate _ClosePort;
        private CheckPrinterStatusDelegate _CheckPrinterStatus;
        private GetStatusErrorDelegate _GetStatusError;
        private SendCommandDelegate _SendCommand;
        private GetResponseDelegate _GetResponse;

        [DllImport("pnpdll.dll", CharSet = CharSet.Ansi, EntryPoint = "OpenPort")]
        private static extern int NativeOpenPort(string portName);

        [DllImport("pnpdll.dll", CharSet = CharSet.Ansi, EntryPoint = "ClosePort")]
        private static extern int NativeClosePort();

        [DllImport("kernel32.dll")]
        private static extern IntPtr LoadLibrary(string dllToLoad);

        [DllImport("kernel32.dll")]
        private static extern IntPtr GetProcAddress(IntPtr hModule, string procedureName);

        [DllImport("kernel32.dll")]
        private static extern bool FreeLibrary(IntPtr hModule);

        public PnpFiscalPrinter(ILogger logger)
        {
            _logger = logger;
            _isInitialized = false;
            _isOpen = false;
            LoadDll();
        }

        private IntPtr GetDelegatePointer(string procName)
        {
            IntPtr procAddress = GetProcAddress(_dllHandle, procName);
            if (procAddress == IntPtr.Zero)
                throw new Exception(string.Format("Failed to get address for {0}", procName));
            return procAddress;
        }

        private void LoadDll()
        {
            try
            {
                _dllHandle = LoadLibrary("pnpdll.dll");
                if (_dllHandle == IntPtr.Zero)
                    throw new Exception("Failed to load pnpdll.dll");

                // Cargar los métodos del DLL usando Marshal directamente
                _OpenPort = (OpenPortDelegate)Marshal.GetDelegateForFunctionPointer(
                    GetDelegatePointer("OpenPort"),
                    typeof(OpenPortDelegate));
                    
                _ClosePort = (ClosePortDelegate)Marshal.GetDelegateForFunctionPointer(
                    GetDelegatePointer("ClosePort"),
                    typeof(ClosePortDelegate));
                    
                _CheckPrinterStatus = (CheckPrinterStatusDelegate)Marshal.GetDelegateForFunctionPointer(
                    GetDelegatePointer("CheckPrinterStatus"),
                    typeof(CheckPrinterStatusDelegate));
                    
                _GetStatusError = (GetStatusErrorDelegate)Marshal.GetDelegateForFunctionPointer(
                    GetDelegatePointer("GetStatusError"),
                    typeof(GetStatusErrorDelegate));
                    
                _SendCommand = (SendCommandDelegate)Marshal.GetDelegateForFunctionPointer(
                    GetDelegatePointer("SendCommand"),
                    typeof(SendCommandDelegate));
                    
                _GetResponse = (GetResponseDelegate)Marshal.GetDelegateForFunctionPointer(
                    GetDelegatePointer("GetResponse"),
                    typeof(GetResponseDelegate));

                _isInitialized = true;
            }
            catch (Exception ex)
            {
                _logger.LogError("Error loading pnpdll.dll: " + ex.Message);
                throw;
            }
        }

        public async Task<bool> OpenPort(string port)
        {
            try
            {
                if (_isOpen)
                    await ClosePort();

                int result = NativeOpenPort(port);
                _isOpen = result == 0;
                _port = port;

                if (!_isOpen)
                    _logger.LogError($"Failed to open port {port}. Error code: {result}");

                return _isOpen;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, $"Error opening port {port}");
                return false;
            }
        }

        public async Task ClosePort()
        {
            try
            {
                if (_isOpen)
                {
                    NativeClosePort();
                    _isOpen = false;
                    _port = null;
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error closing port");
            }
        }

        public async Task<bool> CheckPrinter()
        {
            try
            {
                if (!_isOpen)
                    return false;

                int result = _CheckPrinterStatus();
                return result == 0;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error checking printer");
                return false;
            }
        }

        public async Task<JObject> GetStatus()
        {
            try
            {
                if (!_isOpen)
                    return CreateErrorResponse("Port not open");

                int status = 0;
                int error = 0;
                int result = _GetStatusError(ref status, ref error);

                if (result != 0)
                    return CreateErrorResponse($"Failed to read status. Error code: {result}");

                return new JObject
                {
                    ["success"] = true,
                    ["status"] = status,
                    ["error"] = error,
                    ["statusDescription"] = DecodePnpStatus(status),
                    ["errorDescription"] = DecodePnpError(error)
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error getting status");
                return CreateErrorResponse(ex.Message);
            }
        }

        public async Task<string> GetSerialNumber()
        {
            try
            {
                if (!_isOpen)
                    throw new Exception("Port not open");

                int result = _SendCommand("S");
                if (result != 0)
                    throw new Exception($"Failed to request serial number. Error code: {result}");

                var response = new StringBuilder(20);
                result = _GetResponse(response, response.Capacity);

                if (result != 0)
                    throw new Exception($"Failed to get serial number response. Error code: {result}");

                return response.ToString().Trim();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error getting serial number");
                throw;
            }
        }

        public async Task<string> GetPrinterVersion()
        {
            try
            {
                if (!_isOpen)
                    throw new Exception("Port not open");

                int result = _SendCommand("V");
                if (result != 0)
                    throw new Exception($"Failed to request printer version. Error code: {result}");

                var response = new StringBuilder(20);
                result = _GetResponse(response, response.Capacity);

                if (result != 0)
                    throw new Exception($"Failed to get printer version response. Error code: {result}");

                return response.ToString().Trim();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error getting printer version");
                throw;
            }
        }

        public async Task<JObject> OpenInvoice(string customerName, string customerId, string address = "", string phone = "")
        {
            try
            {
                if (!_isOpen)
                    return CreateErrorResponse("Port not open");

                // Formato específico para PNP
                string cmd = $"I{customerName}|{customerId}|{address}|{phone}";
                int result = _SendCommand(cmd);

                if (result != 0)
                    return CreateErrorResponse($"Failed to open invoice. Error code: {result}");

                return new JObject
                {
                    ["success"] = true,
                    ["message"] = "Invoice opened successfully"
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error opening invoice");
                return CreateErrorResponse(ex.Message);
            }
        }

        public async Task<JObject> AddInvoiceItem(string description, decimal quantity, decimal price, decimal tax = 0, decimal discount = 0)
        {
            try
            {
                if (!_isOpen)
                    return CreateErrorResponse("Port not open");

                // Formatear valores numéricos según especificación PNP
                string qty = quantity.ToString("0.000");
                string prc = price.ToString("0.00");
                string tx = tax.ToString("0.00");
                string disc = discount.ToString("0.00");

                // Comando específico para PNP
                string cmd = $"A{description}|{qty}|{prc}|{tx}|{disc}";
                int result = _SendCommand(cmd);

                if (result != 0)
                    return CreateErrorResponse($"Failed to add item. Error code: {result}");

                return new JObject
                {
                    ["success"] = true,
                    ["message"] = "Item added successfully"
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error adding invoice item");
                return CreateErrorResponse(ex.Message);
            }
        }

        public async Task<JObject> AddInvoicePayment(string paymentType, decimal amount)
        {
            try
            {
                if (!_isOpen)
                    return CreateErrorResponse("Port not open");

                string amt = amount.ToString("0.00");
                string cmd = $"P{paymentType}|{amt}";
                int result = _SendCommand(cmd);

                if (result != 0)
                    return CreateErrorResponse($"Failed to add payment. Error code: {result}");

                return new JObject
                {
                    ["success"] = true,
                    ["message"] = "Payment added successfully"
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error adding payment");
                return CreateErrorResponse(ex.Message);
            }
        }

        public async Task<JObject> CloseInvoice()
        {
            try
            {
                if (!_isOpen)
                    return CreateErrorResponse("Port not open");

                int result = _SendCommand("C");

                if (result != 0)
                    return CreateErrorResponse($"Failed to close invoice. Error code: {result}");

                return new JObject
                {
                    ["success"] = true,
                    ["message"] = "Invoice closed successfully"
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error closing invoice");
                return CreateErrorResponse(ex.Message);
            }
        }

        public async Task<JObject> PrintXReport()
        {
            try
            {
                if (!_isOpen)
                    return CreateErrorResponse("Port not open");

                int result = _SendCommand("X");

                if (result != 0)
                    return CreateErrorResponse($"Failed to print X report. Error code: {result}");

                return new JObject
                {
                    ["success"] = true,
                    ["message"] = "X report printed successfully"
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error printing X report");
                return CreateErrorResponse(ex.Message);
            }
        }

        public async Task<JObject> PrintZReport()
        {
            try
            {
                if (!_isOpen)
                    return CreateErrorResponse("Port not open");

                int result = _SendCommand("Z");

                if (result != 0)
                    return CreateErrorResponse($"Failed to print Z report. Error code: {result}");

                return new JObject
                {
                    ["success"] = true,
                    ["message"] = "Z report printed successfully"
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error printing Z report");
                return CreateErrorResponse(ex.Message);
            }
        }

        public async Task<JObject> SetHeader(string[] lines)
        {
            try
            {
                if (!_isOpen)
                    return CreateErrorResponse("Port not open");

                for (int i = 0; i < lines.Length && i < 8; i++)
                {
                    string cmd = $"H{i}|{lines[i]}";
                    int result = _SendCommand(cmd);

                    if (result != 0)
                        return CreateErrorResponse($"Failed to set header line {i}. Error code: {result}");
                }

                return new JObject
                {
                    ["success"] = true,
                    ["message"] = "Header set successfully"
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error setting header");
                return CreateErrorResponse(ex.Message);
            }
        }

        public async Task<JObject> SetFooter(string[] lines)
        {
            try
            {
                if (!_isOpen)
                    return CreateErrorResponse("Port not open");

                for (int i = 0; i < lines.Length && i < 3; i++)
                {
                    string cmd = $"F{i}|{lines[i]}";
                    int result = _SendCommand(cmd);

                    if (result != 0)
                        return CreateErrorResponse($"Failed to set footer line {i}. Error code: {result}");
                }

                return new JObject
                {
                    ["success"] = true,
                    ["message"] = "Footer set successfully"
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error setting footer");
                return CreateErrorResponse(ex.Message);
            }
        }

        public async Task<JObject> SetTaxRates(decimal[] rates)
        {
            try
            {
                if (!_isOpen)
                    return CreateErrorResponse("Port not open");

                for (int i = 0; i < rates.Length && i < 3; i++)
                {
                    string rate = rates[i].ToString("0.00");
                    string cmd = $"T{i}|{rate}";
                    int result = _SendCommand(cmd);

                    if (result != 0)
                        return CreateErrorResponse($"Failed to set tax rate {i}. Error code: {result}");
                }

                return new JObject
                {
                    ["success"] = true,
                    ["message"] = "Tax rates set successfully"
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error setting tax rates");
                return CreateErrorResponse(ex.Message);
            }
        }

        public async Task<JObject> GetDiagnostic()
        {
            try
            {
                if (!_isOpen)
                    return CreateErrorResponse("Port not open");

                int result = _SendCommand("D");
                if (result != 0)
                    return CreateErrorResponse($"Failed to request diagnostic. Error code: {result}");

                var response = new StringBuilder(100);
                result = _GetResponse(response, response.Capacity);

                if (result != 0)
                    return CreateErrorResponse($"Failed to get diagnostic response. Error code: {result}");

                return new JObject
                {
                    ["success"] = true,
                    ["diagnostic"] = response.ToString().Trim()
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error getting diagnostic");
                return CreateErrorResponse(ex.Message);
            }
        }

        public async Task<JObject> GetMemoryStatus()
        {
            try
            {
                if (!_isOpen)
                    return CreateErrorResponse("Port not open");

                int result = _SendCommand("M");
                if (result != 0)
                    return CreateErrorResponse($"Failed to request memory status. Error code: {result}");

                var response = new StringBuilder(100);
                result = _GetResponse(response, response.Capacity);

                if (result != 0)
                    return CreateErrorResponse($"Failed to get memory status response. Error code: {result}");

                return new JObject
                {
                    ["success"] = true,
                    ["memoryStatus"] = response.ToString().Trim()
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error getting memory status");
                return CreateErrorResponse(ex.Message);
            }
        }

        private string DecodePnpStatus(int status)
        {
            // Implementar decodificación de estados según manual PNP
            return $"Status code: {status}";
        }

        private string DecodePnpError(int error)
        {
            // Implementar decodificación de errores según manual PNP
            return $"Error code: {error}";
        }

        private JObject CreateErrorResponse(string message)
        {
            return new JObject
            {
                ["success"] = false,
                ["message"] = message
            };
        }

        ~PnpFiscalPrinter()
        {
            if (_dllHandle != IntPtr.Zero)
            {
                FreeLibrary(_dllHandle);
            }
        }
    }
}
