using System;
using System.Threading.Tasks;
using System.Collections.Generic;
using Newtonsoft.Json.Linq;
using Microsoft.Extensions.Logging;

namespace ApiPrinterServer.Handlers
{
    public class TestHandler : BasePrinterHandler
    {
        private readonly List<JObject> _documentHistory;
        private int _documentCount;
        private bool _simulateErrors;
        private int _errorFrequency;
        private Random _random;
        
        public TestHandler(ILogger logger) : base(logger)
        {
            _documentHistory = new List<JObject>();
            _documentCount = 0;
            _random = new Random();
        }

        public override async Task<bool> Initialize(JObject config)
        {
            try
            {
                await base.Initialize(config);
                
                var testConfig = config["settings"]["TEST"];
                _simulateErrors = testConfig["simulate_errors"]?.Value<bool>() ?? false;
                _errorFrequency = testConfig["error_frequency"]?.Value<int>() ?? 10; // 10% por defecto
                
                _logger.LogInformation(string.Format("Test handler initialized. Simulate errors: {0}, Error frequency: {1}%", _simulateErrors, _errorFrequency));
                
                return true;
            }
            catch (Exception ex)
            {
                _logger.LogError("Error initializing test handler: " + ex.Message);
                return false;
            }
        }

        public override async Task<JObject> ProcessDocument(JObject document)
        {
            try
            {
                if (!_isInitialized)
                    return CreateResponse(false, "Test handler not initialized");

                _documentCount++;
                
                // Simular errores aleatorios si está configurado
                if (_simulateErrors && _random.Next(100) < _errorFrequency)
                {
                    var errorTypes = new[] {
                        "PRINTER_OFFLINE",
                        "PAPER_JAM",
                        "OUT_OF_PAPER",
                        "COVER_OPEN",
                        "MECHANICAL_ERROR"
                    };
                    
                    var error = errorTypes[_random.Next(errorTypes.Length)];
                    _logger.LogWarning(string.Format("Simulating error: {0}", error));
                    return CreateResponse(false, string.Format("Simulated error: {0}", error));
                }

                // Agregar timestamp y metadata
                var processedDocument = new JObject(document)
                {
                    ["test_metadata"] = new JObject
                    {
                        ["processed_at"] = DateTime.UtcNow,
                        ["document_number"] = _documentCount,
                        ["simulation_mode"] = true
                    }
                };

                // Guardar en historial
                _documentHistory.Add(processedDocument);
                
                // Simular tiempo de procesamiento
                await Task.Delay(_random.Next(100, 500));

                _logger.LogInformation(string.Format("Test document {0} processed successfully", _documentCount));
                
                return new JObject
                {
                    ["success"] = true,
                    ["message"] = string.Format("Document processed in test mode"),
                    ["document_number"] = _documentCount,
                    ["processed_document"] = processedDocument
                };
            }
            catch (Exception ex)
            {
                _logger.LogError("Error processing test document: " + ex.Message);
                return CreateResponse(false, ex.Message);
            }
        }

        public override async Task<JObject> CheckStatus()
        {
            try
            {
                if (!_isInitialized)
                    return CreateResponse(false, "Test handler not initialized");

                // Simular estado del dispositivo
                var printerStatus = new JObject
                {
                    ["online"] = true,
                    ["paper_level"] = _random.Next(0, 100),
                    ["temperature"] = _random.Next(25, 35),
                    ["documents_processed"] = _documentCount,
                    ["last_document_time"] = _documentHistory.Count > 0 
                        ? _documentHistory[_documentHistory.Count - 1]["test_metadata"]["processed_at"]
                        : null,
                    ["simulate_errors"] = _simulateErrors,
                    ["error_frequency"] = _errorFrequency
                };

                return new JObject
                {
                    ["success"] = true,
                    ["status"] = printerStatus,
                    ["message"] = string.Format("Test printer status")
                };
            }
            catch (Exception ex)
            {
                _logger.LogError("Error checking test status: " + ex.Message);
                return CreateResponse(false, ex.Message);
            }
        }

        public override async Task Shutdown()
        {
            try
            {
                _logger.LogInformation(string.Format("Test handler shutdown. Total documents processed: {0}", _documentCount));
                await base.Shutdown();
            }
            catch (Exception ex)
            {
                _logger.LogError("Error during test handler shutdown: " + ex.Message);
            }
        }

        // Métodos adicionales para pruebas
        public int GetDocumentCount() => _documentCount;
        
        public List<JObject> GetDocumentHistory() => _documentHistory;
        
        public void ClearHistory()
        {
            _documentHistory.Clear();
            _documentCount = 0;
        }

        public void SetErrorSimulation(bool simulate, int frequency = 10)
        {
            _simulateErrors = simulate;
            _errorFrequency = frequency;
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
