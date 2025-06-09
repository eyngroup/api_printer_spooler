using System;
using System.IO;
using System.Text;
using System.Threading.Tasks;
using System.Collections.Generic;
using System.Drawing.Printing;
using Newtonsoft.Json.Linq;
using Microsoft.Extensions.Logging;
using ApiPrinterServer.Utils;

namespace ApiPrinterServer.Handlers
{
    public class TicketHandler : BasePrinterHandler
    {
        private string _printerName;
        private string _templatePath;
        private PrintDocument _printDocument;
        
        public TicketHandler(ILogger logger) : base(logger)
        {
        }

        public override async Task<bool> Initialize(JObject config)
        {
            try
            {
                await base.Initialize(config);
                
                _printerName = config["settings"]["TICKET"]["printer_name"].ToString();
                string templateName = config["settings"]["TICKET"]["template"].ToString();
                _templatePath = Path.Combine("templates", "escpos", $"{templateName}.template");
                
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
                _logger.LogError(ex, "Error initializing ticket printer");
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
                var variables = PrintTemplateManager.ExtractVariablesFromDocument(document);
                foreach (var variable in variables)
                {
                    templateManager.SetVariable(variable.Key, variable.Value);
                }

                string processedTemplate = templateManager.ProcessTemplate();
                byte[] printData = ProcessTemplateToEscpos(processedTemplate);

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
                _logger.LogError(ex, "Error processing document on ticket printer");
                return CreateResponse(false, $"Error: {ex.Message}");
            }
        }

        private byte[] ProcessTemplateToEscpos(string template)
        {
            var commands = new List<byte[]>();
            commands.Add(EscposCommands.Initialize);

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
                        case "center":
                            commands.Add(EscposCommands.AlignCenter);
                            continue;
                        case "right":
                            commands.Add(EscposCommands.AlignRight);
                            continue;
                        case "left":
                            commands.Add(EscposCommands.AlignLeft);
                            continue;
                        case "/center":
                        case "/right":
                        case "/left":
                            commands.Add(EscposCommands.AlignLeft);
                            continue;
                    }
                }

                // Procesar texto con énfasis
                if (trimmedLine.StartsWith("**") && trimmedLine.EndsWith("**"))
                {
                    commands.Add(EscposCommands.Bold);
                    commands.Add(EscposCommands.GetText(
                        trimmedLine.Substring(2, trimmedLine.Length - 4)));
                    commands.Add(EscposCommands.BoldOff);
                }
                else
                {
                    commands.Add(EscposCommands.GetText(trimmedLine));
                }

                commands.Add(EscposCommands.NewLine);
            }

            commands.Add(EscposCommands.Feed);
            commands.Add(EscposCommands.Cut);

            return EscposCommands.CombineCommands(commands.ToArray());
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
                _logger.LogError(ex, "Error checking ticket printer status");
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
                _logger.LogError(ex, "Error during ticket printer shutdown");
            }
        }
    }
}
