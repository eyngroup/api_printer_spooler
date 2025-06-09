using System;
using System.Net.Http;
using System.Threading.Tasks;
using System.Text;
using Newtonsoft.Json.Linq;
using Microsoft.Extensions.Logging;

namespace ApiPrinterServer.Handlers
{
    public class ProxyHandler : BasePrinterHandler
    {
        private readonly HttpClient _httpClient;
        private string _targetUrl;
        private string _authToken;
        private int _timeout;
        
        public ProxyHandler(ILogger logger) : base(logger)
        {
            _httpClient = new HttpClient();
        }

        public override async Task<bool> Initialize(JObject config)
        {
            try
            {
                await base.Initialize(config);
                
                var proxyConfig = config["settings"]["PROXY"];
                _targetUrl = proxyConfig["target_url"].ToString();
                _timeout = proxyConfig["timeout"]?.Value<int>() ?? 30000;
                _authToken = proxyConfig["auth_token"]?.ToString();
                
                _httpClient.Timeout = TimeSpan.FromMilliseconds(_timeout);
                
                if (!string.IsNullOrEmpty(_authToken))
                {
                    _httpClient.DefaultRequestHeaders.Add("Authorization", $"Bearer {_authToken}");
                }
                
                // Verificar conexión con el servidor destino
                using (var response = await _httpClient.GetAsync($"{_targetUrl}/api/ping"))
                {
                    return response.IsSuccessStatusCode;
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error initializing proxy handler");
                return false;
            }
        }

        public override async Task<JObject> ProcessDocument(JObject document)
        {
            try
            {
                if (!_isInitialized)
                    return CreateResponse(false, "Proxy not initialized");

                var content = new StringContent(
                    document.ToString(),
                    Encoding.UTF8,
                    "application/json"
                );

                using (var response = await _httpClient.PostAsync($"{_targetUrl}/printer/invoice", content))
                {
                    var responseContent = await response.Content.ReadAsStringAsync();
                    
                    if (!response.IsSuccessStatusCode)
                    {
                        _logger.LogError($"Proxy request failed: {response.StatusCode} - {responseContent}");
                        return CreateResponse(false, $"Proxy request failed: {response.StatusCode}");
                    }

                    try
                    {
                        return JObject.Parse(responseContent);
                    }
                    catch
                    {
                        return CreateResponse(true, responseContent);
                    }
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error in proxy request");
                return CreateResponse(false, $"Proxy error: {ex.Message}");
            }
        }

        public override async Task<JObject> CheckStatus()
        {
            try
            {
                if (!_isInitialized)
                    return CreateResponse(false, "Proxy not initialized");

                using (var response = await _httpClient.GetAsync($"{_targetUrl}/api/ping"))
                {
                    var responseContent = await response.Content.ReadAsStringAsync();
                    
                    return new JObject
                    {
                        ["success"] = response.IsSuccessStatusCode,
                        ["status"] = (int)response.StatusCode,
                        ["message"] = response.IsSuccessStatusCode ? "Connected" : "Not Connected",
                        ["target_url"] = _targetUrl,
                        ["response"] = responseContent
                    };
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error checking proxy status");
                return CreateResponse(false, $"Proxy status error: {ex.Message}");
            }
        }

        public override async Task Shutdown()
        {
            try
            {
                _httpClient.Dispose();
                await base.Shutdown();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error during proxy handler shutdown");
            }
        }
    }
}
