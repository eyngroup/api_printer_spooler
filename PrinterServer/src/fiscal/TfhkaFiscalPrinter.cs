using System;
using System.Threading.Tasks;
using System.Text;
using System.Runtime.InteropServices;
using Newtonsoft.Json.Linq;
using Microsoft.Extensions.Logging;
using ApiPrinterServer.Interfaces;

namespace ApiPrinterServer.Fiscal
{
    public class TfhkaFiscalPrinter : IFiscalPrinter
    {
        private readonly ILogger _logger;
        private bool _isPortOpen;
        private IntPtr _dllHandle;
        private string _currentPort;

        // Delegados para los métodos del DLL
        private delegate int OpenFpctrl(string port);
        private delegate int CloseFpctrl();
        private delegate int CheckFprinter();
        private delegate int ReadFpStatus(ref int status, ref int error);
        private delegate int SendCmd(string cmd);
        private delegate int SendCmdAscii(string cmd);
        private delegate int UploadStatusCmd(string cmd, StringBuilder response, int responseSize);

        private OpenFpctrl _OpenFpctrl;
        private CloseFpctrl _CloseFpctrl;
        private CheckFprinter _CheckFprinter;
        private ReadFpStatus _ReadFpStatus;
        private SendCmd _SendCmd;
        private SendCmdAscii _SendCmdAscii;
        private UploadStatusCmd _UploadStatusCmd;

        public TfhkaFiscalPrinter(ILogger logger)
        {
            _logger = logger;
            _isPortOpen = false;
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
                _dllHandle = LoadLibrary("TfhkaNet.dll");
                if (_dllHandle == IntPtr.Zero)
                    throw new Exception("Failed to load TfhkaNet.dll");

                // Cargar los métodos del DLL usando Marshal directamente
                _OpenFpctrl = (OpenFpctrl)Marshal.GetDelegateForFunctionPointer(
                    GetDelegatePointer("OpenFpctrl"),
                    typeof(OpenFpctrl));
                    
                _CloseFpctrl = (CloseFpctrl)Marshal.GetDelegateForFunctionPointer(
                    GetDelegatePointer("CloseFpctrl"),
                    typeof(CloseFpctrl));
                    
                _CheckFprinter = (CheckFprinter)Marshal.GetDelegateForFunctionPointer(
                    GetDelegatePointer("CheckFprinter"),
                    typeof(CheckFprinter));
                    
                _ReadFpStatus = (ReadFpStatus)Marshal.GetDelegateForFunctionPointer(
                    GetDelegatePointer("ReadFpStatus"),
                    typeof(ReadFpStatus));
                    
                _SendCmd = (SendCmd)Marshal.GetDelegateForFunctionPointer(
                    GetDelegatePointer("SendCmd"),
                    typeof(SendCmd));
                    
                _SendCmdAscii = (SendCmdAscii)Marshal.GetDelegateForFunctionPointer(
                    GetDelegatePointer("SendCmdAscii"),
                    typeof(SendCmdAscii));
                    
                _UploadStatusCmd = (UploadStatusCmd)Marshal.GetDelegateForFunctionPointer(
                    GetDelegatePointer("UploadStatusCmd"),
                    typeof(UploadStatusCmd));
            }
            catch (Exception ex)
            {
                _logger.LogError("Error loading TfhkaNet.dll: " + ex.Message);
                throw;
            }
        }

        public async Task<bool> OpenPort(string port)
        {
            try
            {
                if (_isPortOpen)
                    await ClosePort();

                return await Task.Run(() =>
                {
                    int result = _OpenFpctrl(port);
                    _isPortOpen = result == 0;
                    _currentPort = port;

                    if (!_isPortOpen)
                        _logger.LogError($"Failed to open port {port}. Error code: {result}");

                    return _isPortOpen;
                });
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
                if (_isPortOpen)
                {
                    await Task.Run(() =>
                    {
                        _CloseFpctrl();
                        _isPortOpen = false;
                        _currentPort = null;
                    });
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
                if (!_isPortOpen)
                    return false;

                return await Task.Run(() =>
                {
                    int result = _CheckFprinter();
                    return result == 0;
                });
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
                if (!_isPortOpen)
                    return CreateErrorResponse("Port not open");

                return await Task.Run(() =>
                {
                    int status = 0;
                    int error = 0;
                    int result = _ReadFpStatus(ref status, ref error);

                    if (result != 0)
                        return CreateErrorResponse($"Failed to read status. Error code: {result}");

                    return new JObject
                    {
                        ["success"] = true,
                        ["status"] = status,
                        ["error"] = error,
                        ["statusDescription"] = DecodeStatus(status),
                        ["errorDescription"] = DecodeError(error)
                    };
                });
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
                if (!_isPortOpen)
                    throw new Exception("Port not open");

                return await Task.Run(() =>
                {
                    var response = new StringBuilder(20);
                    int result = _UploadStatusCmd("S1", response, response.Capacity);

                    if (result != 0)
                        throw new Exception($"Failed to get serial number. Error code: {result}");

                    return response.ToString().Trim();
                });
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
                if (!_isPortOpen)
                    throw new Exception("Port not open");

                return await Task.Run(() =>
                {
                    var response = new StringBuilder(20);
                    int result = _UploadStatusCmd("V", response, response.Capacity);

                    if (result != 0)
                        throw new Exception($"Failed to get printer version. Error code: {result}");

                    return response.ToString().Trim();
                });
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
                if (!_isPortOpen)
                    return CreateErrorResponse("Port not open");

                return await Task.Run(() =>
                {
                    // Comando para abrir factura fiscal
                    string cmd = $"i{customerName}\\{customerId}\\{address}\\{phone}";
                    int result = _SendCmd(cmd);

                    if (result != 0)
                        return CreateErrorResponse($"Failed to open invoice. Error code: {result}");

                    return new JObject
                    {
                        ["success"] = true,
                        ["message"] = "Invoice opened successfully"
                    };
                });
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
                if (!_isPortOpen)
                    return CreateErrorResponse("Port not open");

                return await Task.Run(() =>
                {
                    // Formatear valores numéricos según especificación de la impresora
                    string qty = quantity.ToString("0.000");
                    string prc = price.ToString("0.00");
                    string tx = tax.ToString("0.00");
                    string disc = discount.ToString("0.00");

                    // Comando para agregar ítem
                    string cmd = $"B{description}\\{qty}\\{prc}\\{tx}\\{disc}";
                    int result = _SendCmd(cmd);

                    if (result != 0)
                        return CreateErrorResponse($"Failed to add item. Error code: {result}");

                    return new JObject
                    {
                        ["success"] = true,
                        ["message"] = "Item added successfully"
                    };
                });
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
                if (!_isPortOpen)
                    return CreateErrorResponse("Port not open");

                return await Task.Run(() =>
                {
                    string amt = amount.ToString("0.00");
                    string cmd = $"P{paymentType}\\{amt}";
                    int result = _SendCmd(cmd);

                    if (result != 0)
                        return CreateErrorResponse($"Failed to add payment. Error code: {result}");

                    return new JObject
                    {
                        ["success"] = true,
                        ["message"] = "Payment added successfully"
                    };
                });
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
                if (!_isPortOpen)
                    return CreateErrorResponse("Port not open");

                return await Task.Run(() =>
                {
                    int result = _SendCmd("101");

                    if (result != 0)
                        return CreateErrorResponse($"Failed to close invoice. Error code: {result}");

                    return new JObject
                    {
                        ["success"] = true,
                        ["message"] = "Invoice closed successfully"
                    };
                });
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
                if (!_isPortOpen)
                    return CreateErrorResponse("Port not open");

                return await Task.Run(() =>
                {
                    int result = _SendCmd("I0X");

                    if (result != 0)
                        return CreateErrorResponse($"Failed to print X report. Error code: {result}");

                    return new JObject
                    {
                        ["success"] = true,
                        ["message"] = "X report printed successfully"
                    };
                });
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
                if (!_isPortOpen)
                    return CreateErrorResponse("Port not open");

                return await Task.Run(() =>
                {
                    int result = _SendCmd("I0Z");

                    if (result != 0)
                        return CreateErrorResponse($"Failed to print Z report. Error code: {result}");

                    return new JObject
                    {
                        ["success"] = true,
                        ["message"] = "Z report printed successfully"
                    };
                });
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
                if (!_isPortOpen)
                    return CreateErrorResponse("Port not open");

                return await Task.Run(() =>
                {
                    for (int i = 0; i < lines.Length && i < 8; i++)
                    {
                        string cmd = $"@{i}{lines[i]}";
                        int result = _SendCmd(cmd);

                        if (result != 0)
                            return CreateErrorResponse($"Failed to set header line {i}. Error code: {result}");
                    }

                    return new JObject
                    {
                        ["success"] = true,
                        ["message"] = "Header set successfully"
                    };
                });
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
                if (!_isPortOpen)
                    return CreateErrorResponse("Port not open");

                return await Task.Run(() =>
                {
                    for (int i = 0; i < lines.Length && i < 3; i++)
                    {
                        string cmd = $"f{i}{lines[i]}";
                        int result = _SendCmd(cmd);

                        if (result != 0)
                            return CreateErrorResponse($"Failed to set footer line {i}. Error code: {result}");
                    }

                    return new JObject
                    {
                        ["success"] = true,
                        ["message"] = "Footer set successfully"
                    };
                });
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
                if (!_isPortOpen)
                    return CreateErrorResponse("Port not open");

                return await Task.Run(() =>
                {
                    for (int i = 0; i < rates.Length && i < 3; i++)
                    {
                        string rate = rates[i].ToString("0.00");
                        string cmd = $"t{i}{rate}";
                        int result = _SendCmd(cmd);

                        if (result != 0)
                            return CreateErrorResponse($"Failed to set tax rate {i}. Error code: {result}");
                    }

                    return new JObject
                    {
                        ["success"] = true,
                        ["message"] = "Tax rates set successfully"
                    };
                });
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
                if (!_isPortOpen)
                    return CreateErrorResponse("Port not open");

                return await Task.Run(() =>
                {
                    var response = new StringBuilder(100);
                    int result = _UploadStatusCmd("D", response, response.Capacity);

                    if (result != 0)
                        return CreateErrorResponse($"Failed to get diagnostic. Error code: {result}");

                    return new JObject
                    {
                        ["success"] = true,
                        ["diagnostic"] = response.ToString().Trim()
                    };
                });
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
                if (!_isPortOpen)
                    return CreateErrorResponse("Port not open");

                return await Task.Run(() =>
                {
                    var response = new StringBuilder(100);
                    int result = _UploadStatusCmd("M", response, response.Capacity);

                    if (result != 0)
                        return CreateErrorResponse($"Failed to get memory status. Error code: {result}");

                    return new JObject
                    {
                        ["success"] = true,
                        ["memoryStatus"] = response.ToString().Trim()
                    };
                });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error getting memory status");
                return CreateErrorResponse(ex.Message);
            }
        }

        private string DecodeStatus(int status)
        {
            // Implementar decodificación de estados según manual
            return $"Status code: {status}";
        }

        private string DecodeError(int error)
        {
            // Implementar decodificación de errores según manual
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

        [DllImport("kernel32.dll")]
        private static extern IntPtr LoadLibrary(string dllToLoad);

        [DllImport("kernel32.dll")]
        private static extern IntPtr GetProcAddress(IntPtr hModule, string procedureName);

        [DllImport("kernel32.dll")]
        private static extern bool FreeLibrary(IntPtr hModule);

        ~TfhkaFiscalPrinter()
        {
            if (_dllHandle != IntPtr.Zero)
            {
                FreeLibrary(_dllHandle);
            }
        }
    }
}
