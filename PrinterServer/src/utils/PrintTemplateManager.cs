using System;
using System.IO;
using System.Text;
using System.Collections.Generic;
using Newtonsoft.Json.Linq;

namespace ApiPrinterServer.Utils
{
    public class PrintTemplateManager
    {
        private readonly string _templateContent;
        private readonly Dictionary<string, string> _variables;

        public PrintTemplateManager(string templatePath)
        {
            _templateContent = File.ReadAllText(templatePath);
            _variables = new Dictionary<string, string>();
        }

        public void SetVariable(string key, string value)
        {
            _variables[key] = value ?? "";
        }

        public string ProcessTemplate()
        {
            string result = _templateContent;
            foreach (var variable in _variables)
            {
                result = result.Replace($"{{{{{variable.Key}}}}}", variable.Value);
            }
            return result;
        }

        public static Dictionary<string, string> ExtractVariablesFromDocument(JObject document)
        {
            var variables = new Dictionary<string, string>();

            // Información del cliente
            variables["CUSTOMER_VAT"] = document["customer_vat"]?.ToString() ?? "";
            variables["CUSTOMER_NAME"] = document["customer_name"]?.ToString() ?? "";
            variables["CUSTOMER_ADDRESS"] = document["customer_address"]?.ToString() ?? "";
            variables["CUSTOMER_PHONE"] = document["customer_phone"]?.ToString() ?? "";

            // Información del documento
            variables["DOCUMENT_NAME"] = document["document_name"]?.ToString() ?? "";
            variables["DOCUMENT_NUMBER"] = document["document_number"]?.ToString() ?? "";
            variables["DOCUMENT_DATE"] = document["document_date"]?.ToString() ?? "";
            variables["DOCUMENT_CURRENCY"] = document["document_currency"]?.ToString() ?? "";

            // Procesar items
            var itemsBuilder = new StringBuilder();
            var items = document["items"] as JArray;
            decimal total = 0;

            if (items != null)
            {
                foreach (var item in items)
                {
                    decimal quantity = item["item_quantity"]?.Value<decimal>() ?? 0;
                    decimal price = item["item_price"]?.Value<decimal>() ?? 0;
                    decimal subtotal = quantity * price;
                    total += subtotal;

                    itemsBuilder.AppendLine($"{item["item_name"],-40}");
                    itemsBuilder.AppendLine($"{quantity,6:N2} x {price,10:N2} = {subtotal,10:N2}");
                    if (!string.IsNullOrEmpty(item["item_comment"]?.ToString()))
                    {
                        itemsBuilder.AppendLine($"  {item["item_comment"]}");
                    }
                }
            }

            variables["ITEMS"] = itemsBuilder.ToString();
            variables["TOTAL"] = total.ToString("N2");

            // Procesar pagos
            var paymentsBuilder = new StringBuilder();
            var payments = document["payments"] as JArray;
            if (payments != null)
            {
                foreach (var payment in payments)
                {
                    paymentsBuilder.AppendLine($"{payment["payment_name"],-20} {payment["payment_amount"],10:N2}");
                }
            }
            variables["PAYMENTS"] = paymentsBuilder.ToString();

            return variables;
        }
    }
}
