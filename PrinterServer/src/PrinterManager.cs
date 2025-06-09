using System;
using System.IO;
using System.Threading.Tasks;
using System.Collections.Generic;
using System.Drawing.Printing;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json.Linq;
using ApiPrinterServer.Interfaces;

namespace ApiPrinterServer
{
    public class PrinterManager
    {
        private readonly ILogger _logger;
        private IPrinterHandler _currentHandler;
        private DateTime _startTime;
        
        public DateTime StartTime
        {
            get { return _startTime; }
            private set { _startTime = value; }
        }
        
        public IPrinterHandler CurrentHandler
        {
            get { return _currentHandler; }
        }

        public PrinterManager(ILogger logger)
        {
            _logger = logger;
            StartTime = DateTime.Now;
        }

        public async Task<bool> Initialize(string configPath)
        {
            try
            {
                string configJson = File.ReadAllText(configPath);
                var config = JObject.Parse(configJson);
                // Inicializar el handler según la configuración
                return true;
            }
            catch (Exception ex)
            {
                _logger.LogError("Error initializing PrinterManager: " + ex.Message);
                return false;
            }
        }

        public async Task<JObject> ProcessDocument(string documentType, Dictionary<string, string> parameters)
        {
            try
            {
                if (_currentHandler == null)
                    return new JObject { ["error"] = "No handler configured" };

                return await _currentHandler.ProcessRequest(documentType, parameters);
            }
            catch (Exception ex)
            {
                _logger.LogError("Error processing document: " + ex.Message);
                return new JObject { ["error"] = ex.Message };
            }
        }

        public async Task<JObject> PrintReportX()
        {
            try
            {
                if (_currentHandler == null)
                    return new JObject { ["error"] = "No handler configured" };

                return await _currentHandler.ProcessRequest("X", new Dictionary<string, string>());
            }
            catch (Exception ex)
            {
                _logger.LogError("Error printing report X: " + ex.Message);
                return new JObject { ["error"] = ex.Message };
            }
        }

        public async Task<JObject> PrintReportZ()
        {
            try
            {
                if (_currentHandler == null)
                    return new JObject { ["error"] = "No handler configured" };

                return await _currentHandler.ProcessRequest("Z", new Dictionary<string, string>());
            }
            catch (Exception ex)
            {
                _logger.LogError("Error printing report Z: " + ex.Message);
                return new JObject { ["error"] = ex.Message };
            }
        }

        public List<string> GetPrinters()
        {
            try
            {
                var printers = new List<string>();
                foreach (string printer in PrinterSettings.InstalledPrinters)
                {
                    printers.Add(printer);
                }
                return printers;
            }
            catch (Exception ex)
            {
                _logger.LogError("Error getting printers list: " + ex.Message);
                return new List<string>();
            }
        }
    }
}
