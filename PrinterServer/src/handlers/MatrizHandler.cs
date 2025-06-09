using System;
using System.Threading.Tasks;
using System.IO;
using System.Text;
using System.Drawing.Printing;
using System.Collections.Generic;
using Newtonsoft.Json.Linq;
using Microsoft.Extensions.Logging;
using ApiPrinterServer.Utils;

namespace ApiPrinterServer.Handlers
{
    public class MatrizHandler : BasePrinterHandler
    {
        private string _printerName;
        private string _templatePath;
        private PrintDocument _printDocument;
        
        public MatrizHandler(ILogger logger) : base(logger)
        {
        }

        public override async Task<bool> Initialize(JObject config)
        {
            try
            {
                await base.Initialize(config);
                
                _printerName = config["settings"]["MATRIZ"]["printer_name"].ToString();
                string templateName = config["settings"]["MATRIZ"]["template"].ToString();
                _templatePath = Path.Combine("templates", "matriz", $"{templateName}.template");
                
                // Verificar que existe la impresora y el template
                if (!File.Exists(_templatePath))
                {
                    throw new FileNotFoundException($"Template {templateName} not found");
                }

                // Verificar que la impresora existe
                bool printerExists = false;
                foreach (string printer in PrinterSettings.InstalledPrinters)
                {
                    if (printer.Equals(_printerName, StringComparison.OrdinalIgnoreCase))
                    {
                        printerExists = true;
                        break;
                    }
                }

                if (!printerExists)
                {
                    throw new Exception($"Printer {_printerName} not found");
                }

                // Inicializar el documento de impresión
                _printDocument = new PrintDocument();
                _printDocument.PrinterSettings.PrinterName = _printerName;
                
                return true;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error initializing matrix printer");
                return false;
            }
        }

        public override async Task<JObject> ProcessDocument(JObject document)
        {
            try
            {
                if (!_isInitialized)
                    return CreateResponse(false, "Printer not initialized");

                // Cargar y procesar el template
                var templateManager = new PrintTemplateManager(_templatePath);
                var variables = ExtractVariablesFromDocument(document);
                foreach (var variable in variables)
                {
                    templateManager.SetVariable(variable.Key, variable.Value);
                }

                string processedTemplate = templateManager.ProcessTemplate();
                byte[] printData = ProcessTemplateToMatrix(processedTemplate);

                // Imprimir usando Raw Data
                using (var rawPrinter = new RawPrinterHelper())
                {
                    if (!rawPrinter.SendBytesToPrinter(_printerName, printData))
                    {
                        throw new Exception("Failed to send data to printer");
                    }
                }
                
                return CreateResponse(true, "Document printed successfully");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error processing document on matrix printer");
                return CreateResponse(false, $"Error: {ex.Message}");
            }
        }

        private Dictionary<string, string> ExtractVariablesFromDocument(JObject document)
        {
            var variables = PrintTemplateManager.ExtractVariablesFromDocument(document);

            // Formato especial para items en impresora matriz
            var itemsBuilder = new StringBuilder();
            var items = document["items"] as JArray;
            if (items != null)
            {
                foreach (var item in items)
                {
                    decimal quantity = item["item_quantity"]?.Value<decimal>() ?? 0;
                    decimal price = item["item_price"]?.Value<decimal>() ?? 0;
                    decimal subtotal = quantity * price;

                    string formattedRow = MatrixCommands.FormatTableRow(
                        item["item_name"].ToString(),
                        quantity,
                        price,
                        subtotal
                    );
                    itemsBuilder.AppendLine(formattedRow);

                    if (!string.IsNullOrEmpty(item["item_comment"]?.ToString()))
                    {
                        itemsBuilder.AppendLine($"  {item["item_comment"]}");
                    }
                }
            }
            variables["ITEMS"] = itemsBuilder.ToString();

            return variables;
        }

        private byte[] ProcessTemplateToMatrix(string template)
        {
            var commands = new List<byte[]>();
            commands.Add(MatrixCommands.Initialize);
            bool inTable = false;
            bool inCondensed = false;

            foreach (string line in template.Split('\n'))
            {
                string trimmedLine = line.Trim();
                if (string.IsNullOrEmpty(trimmedLine)) continue;

                // Procesar comandos especiales entre []
                if (trimmedLine.StartsWith("[") && trimmedLine.EndsWith("]"))
                {
                    string command = trimmedLine.Substring(1, trimmedLine.Length - 2);
                    switch (command.ToLower())
                    {
                        case "condensed":
                            commands.Add(MatrixCommands.CondensedOn);
                            inCondensed = true;
                            continue;
                        case "/condensed":
                            commands.Add(MatrixCommands.CondensedOff);
                            inCondensed = false;
                            continue;
                        case "table":
                            inTable = true;
                            commands.Add(MatrixCommands.SetLineSpacing1_6);
                            continue;
                        case "/table":
                            inTable = false;
                            commands.Add(MatrixCommands.SetLineSpacing1_8);
                            continue;
                    }
                }

                // Procesar texto
                commands.Add(MatrixCommands.GetText(trimmedLine));
                commands.Add(MatrixCommands.NewLine);
            }

            // Restaurar estados
            if (inCondensed)
                commands.Add(MatrixCommands.CondensedOff);
            
            commands.Add(MatrixCommands.FormFeed);

            return MatrixCommands.CombineCommands(commands.ToArray());
        }

        public override async Task<JObject> CheckStatus()
        {
            try
            {
                if (!_isInitialized)
                    return CreateResponse(false, "Printer not initialized");

                var status = new JObject();
                var settings = new PrinterSettings
                {
                    PrinterName = _printerName
                };

                status["online"] = settings.IsValid;
                status["default"] = (settings.PrinterName == new PrinterSettings().PrinterName);
                status["port"] = settings.PrintToFile ? "FILE" : settings.PrinterName;

                return CreateResponse(true, "Printer status checked", status);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error checking matrix printer status");
                return CreateResponse(false, $"Error: {ex.Message}");
            }
        }

        public override async Task Shutdown()
        {
            try
            {
                _printDocument?.Dispose();
                await base.Shutdown();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error during matrix printer shutdown");
            }
        }
    }
}
