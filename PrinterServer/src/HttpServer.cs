using System;
using System.IO;
using System.Net;
using System.Text;
using System.Threading.Tasks;
using System.Collections.Generic;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using ApiPrinterServer.Handlers;
using ApiPrinterServer.Interfaces;

namespace ApiPrinterServer
{
    public class HttpServer
    {
        private readonly HttpListener _listener;
        private readonly PrinterManager _printerManager;
        private readonly ILogger _logger;
        private readonly WebStatusHandler _statusHandler;
        private readonly string _host;
        private readonly int _port;
        private bool _isRunning;

        public HttpServer(string configJson, PrinterManager printerManager, ILogger logger)
        {
            _printerManager = printerManager;
            _logger = logger;
            
            var config = JObject.Parse(configJson);
            _host = config["server"]["host"].ToString();
            _port = config["server"]["port"].Value<int>();
            
            _listener = new HttpListener();
            _listener.Prefixes.Add(string.Format("http://{0}:{1}/", _host, _port));
            
            _statusHandler = new WebStatusHandler(printerManager, logger);
            _isRunning = false;
        }

        public async Task Start()
        {
            try
            {
                _listener.Start();
                _isRunning = true;
                _logger.LogInformation(string.Format("Server started at http://{0}:{1}/", _host, _port));

                while (_isRunning)
                {
                    var context = await _listener.GetContextAsync();
                    _ = ProcessRequestAsync(context);
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error in HTTP server");
                throw;
            }
        }

        private async Task ProcessRequestAsync(HttpListenerContext context)
        {
            try
            {
                string path = context.Request.Url.AbsolutePath.ToLower();
                string method = context.Request.HttpMethod.ToUpper();

                if (path == "/api/status")
                {
                    var parameters = ParseQueryString(context.Request);
                    var result = await _statusHandler.ProcessRequest(method, parameters);
                    await WriteJsonResponse(context, result);
                    return;
                }

                if (path == "/api/document")
                {
                    if (method != "POST")
                    {
                        await WriteErrorResponse(context, "Method not allowed", 405);
                        return;
                    }

                    StreamReader reader = null;
                    try
                    {
                        reader = new StreamReader(context.Request.InputStream);
                        var body = await reader.ReadToEndAsync();
                        var document = JObject.Parse(body);

                        var result = await _printerManager.ProcessDocument("DOCUMENT", new Dictionary<string, string>
                        {
                            ["document"] = document.ToString()
                        });
                        
                        await WriteJsonResponse(context, result);
                        return;
                    }
                    finally
                    {
                        if (reader != null) reader.Dispose();
                    }
                }

                if (path == "/api/report/x")
                {
                    var result = await _printerManager.PrintReportX();
                    await WriteJsonResponse(context, result);
                    return;
                }

                if (path == "/api/report/z")
                {
                    var result = await _printerManager.PrintReportZ();
                    await WriteJsonResponse(context, result);
                    return;
                }

                await WriteErrorResponse(context, "Not found", 404);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error processing request");
                await WriteErrorResponse(context, "Internal server error", 500);
            }
        }

        private Dictionary<string, string> ParseQueryString(HttpListenerRequest request)
        {
            var parameters = new Dictionary<string, string>();
            foreach (string key in request.QueryString.Keys)
            {
                parameters[key] = request.QueryString[key];
            }
            return parameters;
        }

        private async Task WriteJsonResponse(HttpListenerContext context, JObject result)
        {
            string response = result.ToString(Formatting.None);
            byte[] buffer = Encoding.UTF8.GetBytes(response);
            
            context.Response.ContentType = "application/json";
            context.Response.ContentLength64 = buffer.Length;
            await context.Response.OutputStream.WriteAsync(buffer, 0, buffer.Length);
            context.Response.Close();
        }

        private async Task WriteErrorResponse(HttpListenerContext context, string message, int statusCode)
        {
            context.Response.StatusCode = statusCode;
            var error = new JObject
            {
                ["error"] = message
            };
            await WriteJsonResponse(context, error);
        }

        public void Stop()
        {
            _isRunning = false;
            _listener.Stop();
            _logger.LogInformation("Server stopped");
        }
    }
}
