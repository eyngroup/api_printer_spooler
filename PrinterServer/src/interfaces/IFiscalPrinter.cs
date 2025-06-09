using System;
using System.Threading.Tasks;
using Newtonsoft.Json.Linq;

namespace ApiPrinterServer.Interfaces
{
    public interface IFiscalPrinter
    {
        // Métodos de conexión
        Task<bool> OpenPort(string port);
        Task ClosePort();
        Task<bool> CheckPrinter();
        
        // Métodos de estado
        Task<JObject> GetStatus();
        Task<string> GetSerialNumber();
        Task<string> GetPrinterVersion();
        
        // Métodos de facturación
        Task<JObject> OpenInvoice(string customerName, string customerId, string address = "", string phone = "");
        Task<JObject> AddInvoiceItem(string description, decimal quantity, decimal price, decimal tax = 0, decimal discount = 0);
        Task<JObject> AddInvoicePayment(string paymentType, decimal amount);
        Task<JObject> CloseInvoice();
        
        // Métodos de reportes
        Task<JObject> PrintXReport();
        Task<JObject> PrintZReport();
        
        // Métodos de configuración
        Task<JObject> SetHeader(string[] lines);
        Task<JObject> SetFooter(string[] lines);
        Task<JObject> SetTaxRates(decimal[] rates);
        
        // Métodos de diagnóstico
        Task<JObject> GetDiagnostic();
        Task<JObject> GetMemoryStatus();
    }
}
