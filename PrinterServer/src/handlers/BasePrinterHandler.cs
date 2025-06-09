using System;
using System.Threading.Tasks;
using System.Collections.Generic;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json.Linq;
using ApiPrinterServer.Interfaces;

namespace ApiPrinterServer.Handlers
{
    public abstract class BasePrinterHandler : IPrinterHandler
    {
        protected readonly ILogger _logger;
        protected JObject _config;
        protected bool _isInitialized;

        protected BasePrinterHandler(ILogger logger)
        {
            _logger = logger;
            _isInitialized = false;
        }

        public virtual async Task<bool> Initialize(JObject config)
        {
            try
            {
                _config = config;
                _isInitialized = true;
                _logger.LogInformation(string.Format("Initialized {0}", GetType().Name));
                return true;
            }
            catch (Exception ex)
            {
                _logger.LogError(string.Format("Error initializing {0}", GetType().Name), ex);
                return false;
            }
        }

        public abstract Task<JObject> ProcessDocument(JObject document);
        
        public virtual async Task<JObject> ProcessRequest(string method, Dictionary<string, string> parameters)
        {
            try
            {
                if (!_isInitialized)
                {
                    return new JObject { ["error"] = "Handler not initialized" };
                }

                switch (method.ToUpper())
                {
                    case "X":
                        return await PrintReportX();
                    case "Z":
                        return await PrintReportZ();
                    case "DOCUMENT":
                        if (!parameters.ContainsKey("document"))
                            return new JObject { ["error"] = "Missing document parameter" };
                            
                        var document = JObject.Parse(parameters["document"]);
                        return await ProcessDocument(document);
                    default:
                        return new JObject { ["error"] = string.Format("Unknown method: {0}", method) };
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(string.Format("Error processing request method: {0}", method), ex);
                return new JObject { ["error"] = ex.Message };
            }
        }

        public virtual async Task<JObject> CheckStatus()
        {
            try
            {
                return new JObject
                {
                    ["status"] = _isInitialized ? "ready" : "not_initialized",
                    ["timestamp"] = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss")
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(string.Format("Error checking status"), ex);
                return new JObject { ["error"] = ex.Message };
            }
        }

        public virtual async Task Shutdown()
        {
            try
            {
                _isInitialized = false;
                _logger.LogInformation(string.Format("Shutdown {0}", GetType().Name));
            }
            catch (Exception ex)
            {
                _logger.LogError(string.Format("Error during shutdown of {0}", GetType().Name), ex);
            }
        }

        protected virtual async Task<JObject> PrintReportX()
        {
            return new JObject { ["error"] = "PrintReportX not implemented" };
        }

        protected virtual async Task<JObject> PrintReportZ()
        {
            return new JObject { ["error"] = "PrintReportZ not implemented" };
        }

        protected JObject CreateResponse(bool success, string message, JObject data = null)
        {
            return new JObject
            {
                ["success"] = success,
                ["message"] = message,
                ["timestamp"] = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss"),
                ["data"] = data ?? new JObject()
            };
        }
    }
}
