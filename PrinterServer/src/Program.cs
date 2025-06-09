using System;
using System.IO;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Logging.Console;
using Microsoft.Extensions.Logging.Configuration;
using Newtonsoft.Json.Linq;
using ApiPrinterServer.Utils;

namespace ApiPrinterServer
{
    class Program
    {
        static void Main(string[] args)
        {
            try
            {
                var loggerFactory = LoggerFactory.Create(builder =>
                {
                    builder.AddConsole();
                    builder.AddConfiguration();
                });

                var logger = loggerFactory.CreateLogger<Program>();
                var configPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "config.json");
                var configJson = File.ReadAllText(configPath);

                var printerManager = new PrinterManager(logger);
                var httpServer = new HttpServer(configJson, printerManager, logger);

                httpServer.Start().Wait();
            }
            catch (Exception ex)
            {
                Console.WriteLine(string.Format("Error: {0}", ex.Message));
                Environment.Exit(1);
            }
        }
    }
}
