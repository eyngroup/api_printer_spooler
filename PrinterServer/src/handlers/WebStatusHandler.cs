using System;
using System.IO;
using System.Text;
using System.Net;
using System.Threading.Tasks;
using System.Collections.Generic;
using Newtonsoft.Json.Linq;
using Microsoft.Extensions.Logging;
using ApiPrinterServer.Interfaces;

namespace ApiPrinterServer.Handlers
{
    public class WebStatusHandler : IHandler
    {
        private readonly PrinterManager _printerManager;
        private readonly ILogger _logger;

        public WebStatusHandler(PrinterManager printerManager, ILogger logger)
        {
            _printerManager = printerManager;
            _logger = logger;
        }

        public async Task<JObject> ProcessRequest(string method, Dictionary<string, string> parameters)
        {
            try
            {
                var status = new JObject
                {
                    ["uptime"] = (DateTime.Now - _printerManager.StartTime).TotalSeconds,
                    ["start_time"] = _printerManager.StartTime.ToString("yyyy-MM-dd HH:mm:ss"),
                    ["current_handler"] = _printerManager.CurrentHandler?.GetType().Name ?? "None"
                };

                return status;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error getting web status");
                return new JObject { ["error"] = ex.Message };
            }
        }

        private async Task<string> ReadFileAsync(string path)
        {
            FileStream stream = null;
            StreamReader reader = null;
            try
            {
                stream = new FileStream(path, FileMode.Open, FileAccess.Read);
                reader = new StreamReader(stream);
                return await reader.ReadToEndAsync();
            }
            finally
            {
                if (reader != null) reader.Dispose();
                if (stream != null) stream.Dispose();
            }
        }

        private async Task WriteResponseAsync(HttpListenerResponse response, string content)
        {
            var buffer = Encoding.UTF8.GetBytes(content);
            response.ContentType = "application/json";
            response.ContentLength64 = buffer.Length;
            await response.OutputStream.WriteAsync(buffer, 0, buffer.Length);
            response.Close();
        }
    }
}
