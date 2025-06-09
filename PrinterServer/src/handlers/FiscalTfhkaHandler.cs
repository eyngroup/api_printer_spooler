using System;
using System.Threading.Tasks;
using Newtonsoft.Json.Linq;
using Microsoft.Extensions.Logging;
using ApiPrinterServer.Fiscal;

namespace ApiPrinterServer.Handlers
{
    public class FiscalTfhkaHandler : BasePrinterHandler
    {
        private string _port;
        private string _model;
        private TfhkaFiscalPrinter _printer;
        
        public FiscalTfhkaHandler(ILogger logger) : base(logger)
        {
            _printer = new TfhkaFiscalPrinter(logger);
        }

        public override async Task<bool> Initialize(JObject config)
        {
            try
            {
                await base.Initialize(config);
                
                _port = config["settings"]["FISCAL_TFHKA"]["port"].ToString();
                _model = config["settings"]["FISCAL_TFHKA"]["model"].ToString();
                
                return await _printer.OpenPort(_port);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error initializing TFHKA fiscal printer");
                return false;
            }
        }

        public override async Task<JObject> ProcessDocument(JObject document)
        {
            try
            {
                if (!_isInitialized)
                    return CreateResponse(false, "Printer not initialized");

                // Verificar estado de la impresora
                var status = await _printer.GetStatus();
                if (!status["success"].Value<bool>())
                    return status;

                // Abrir factura
                var openResult = await _printer.OpenInvoice(
                    document["customer_name"].ToString(),
                    document["customer_vat"].ToString(),
                    document["customer_address"]?.ToString() ?? "",
                    document["customer_phone"]?.ToString() ?? ""
                );

                if (!openResult["success"].Value<bool>())
                    return openResult;

                // Procesar items
                var items = document["items"] as JArray;
                foreach (var item in items)
                {
                    var itemResult = await _printer.AddInvoiceItem(
                        item["item_name"].ToString(),
                        item["item_quantity"].Value<decimal>(),
                        item["item_price"].Value<decimal>(),
                        item["item_tax"]?.Value<decimal>() ?? 0,
                        item["item_discount"]?.Value<decimal>() ?? 0
                    );

                    if (!itemResult["success"].Value<bool>())
                        return itemResult;
                }

                // Procesar pagos
                var payments = document["payments"] as JArray;
                foreach (var payment in payments)
                {
                    var paymentResult = await _printer.AddInvoicePayment(
                        payment["payment_method"].ToString(),
                        payment["payment_amount"].Value<decimal>()
                    );

                    if (!paymentResult["success"].Value<bool>())
                        return paymentResult;
                }

                // Cerrar factura
                return await _printer.CloseInvoice();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error processing document on TFHKA fiscal printer");
                return CreateResponse(false, $"Error: {ex.Message}");
            }
        }

        public override async Task<JObject> CheckStatus()
        {
            try
            {
                if (!_isInitialized)
                    return CreateResponse(false, "Printer not initialized");

                var status = await _printer.GetStatus();
                if (!status["success"].Value<bool>())
                    return status;

                // Agregar información adicional
                var diagnostic = await _printer.GetDiagnostic();
                var memory = await _printer.GetMemoryStatus();
                var serial = await _printer.GetSerialNumber();
                var version = await _printer.GetPrinterVersion();

                return new JObject
                {
                    ["success"] = true,
                    ["status"] = status,
                    ["diagnostic"] = diagnostic["diagnostic"],
                    ["memory"] = memory["memoryStatus"],
                    ["serial"] = serial,
                    ["version"] = version,
                    ["port"] = _port,
                    ["model"] = _model
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error checking TFHKA fiscal printer status");
                return CreateResponse(false, $"Error: {ex.Message}");
            }
        }

        public override async Task Shutdown()
        {
            try
            {
                await _printer.ClosePort();
                await base.Shutdown();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error during TFHKA fiscal printer shutdown");
            }
        }
    }
}
