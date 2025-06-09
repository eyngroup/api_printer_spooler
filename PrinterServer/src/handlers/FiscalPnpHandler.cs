using System;
using System.Threading.Tasks;
using Newtonsoft.Json.Linq;
using Microsoft.Extensions.Logging;
using ApiPrinterServer.Fiscal;

namespace ApiPrinterServer.Handlers
{
    public class FiscalPnpHandler : BasePrinterHandler
    {
        private string _port;
        private string _model;
        private PnpFiscalPrinter _printer;
        
        public FiscalPnpHandler(ILogger logger) : base(logger)
        {
            _printer = new PnpFiscalPrinter(logger);
        }

        public override async Task<bool> Initialize(JObject config)
        {
            try
            {
                await base.Initialize(config);
                
                _port = config["settings"]["FISCAL_PNP"]["port"].ToString();
                _model = config["settings"]["FISCAL_PNP"]["model"].ToString();
                
                return await _printer.OpenPort(_port);
            }
            catch (Exception ex)
            {
                _logger.LogError("Error initializing PNP fiscal printer: " + ex.Message);
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

                // Obtener datos del cliente con valores por defecto
                string customerAddress = "";
                string customerPhone = "";
                
                var addressToken = document["customer_address"];
                if (addressToken != null)
                    customerAddress = addressToken.ToString();
                    
                var phoneToken = document["customer_phone"];
                if (phoneToken != null)
                    customerPhone = phoneToken.ToString();

                // Abrir factura
                var openResult = await _printer.OpenInvoice(
                    document["customer_name"].ToString(),
                    document["customer_vat"].ToString(),
                    customerAddress,
                    customerPhone
                );

                if (!openResult["success"].Value<bool>())
                    return openResult;

                // Procesar items
                var items = document["items"] as JArray;
                foreach (var item in items)
                {
                    decimal itemTax = 0;
                    decimal itemDiscount = 0;
                    
                    var taxToken = item["item_tax"];
                    if (taxToken != null)
                        itemTax = taxToken.Value<decimal>();
                        
                    var discountToken = item["item_discount"];
                    if (discountToken != null)
                        itemDiscount = discountToken.Value<decimal>();

                    var itemResult = await _printer.AddInvoiceItem(
                        item["item_name"].ToString(),
                        item["item_quantity"].Value<decimal>(),
                        item["item_price"].Value<decimal>(),
                        itemTax,
                        itemDiscount
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
                _logger.LogError("Error processing document on PNP fiscal printer: " + ex.Message);
                return CreateResponse(false, string.Format("Error: {0}", ex.Message));
            }
        }

        public override async Task<JObject> CheckStatus()
        {
            try
            {
                if (!_isInitialized)
                    return CreateResponse(false, "Printer not initialized");

                var status = await _printer.GetStatus();
                status["printer_model"] = _model;
                status["port"] = _port;
                return status;
            }
            catch (Exception ex)
            {
                _logger.LogError("Error checking PNP fiscal printer status: " + ex.Message);
                return CreateResponse(false, string.Format("Error: {0}", ex.Message));
            }
        }

        private JObject CreateResponse(bool success, string message)
        {
            return new JObject
            {
                ["success"] = success,
                ["message"] = message
            };
        }
    }
}
