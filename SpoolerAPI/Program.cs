using System;
using Serilog;
using System.Net.NetworkInformation;
using System.Linq;
using System.IO;
using SpoolerAPI.Models;
using System.Diagnostics;
using System.Runtime.InteropServices;
using Newtonsoft.Json;

namespace SpoolerAPI
{
    internal class Program
    {
        private static Class _msg;
        private const int SW_MINIMIZE = 6;
        [DllImport("kernel32.dll")]
        static extern IntPtr GetConsoleWindow();
        [DllImport("user32.dll")]
        static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);

        static void Main()
        {
            Log.Logger = new LoggerConfiguration()
            .MinimumLevel.Debug()
            .WriteTo.Console()
            .WriteTo.File("log.txt", rollingInterval: RollingInterval.Day)
            .CreateLogger();

            _msg = new Class();

            var networkInterface = NetworkInterface.GetAllNetworkInterfaces().FirstOrDefault(n => n.Name == "Ethernet");
            if (networkInterface != null)
            {
                var ipProperties = networkInterface.GetIPProperties();
                var ipv4Address = ipProperties.UnicastAddresses
                    .FirstOrDefault(a => a.Address.AddressFamily == System.Net.Sockets.AddressFamily.InterNetwork)?.Address;

                if (ipv4Address != null)
                {
                    var ipAddress = ipv4Address.ToString();
                }
            }

            var appSettings = JsonConvert.DeserializeObject<AppSettings>(File.ReadAllText("appsettings.json"));
            string[] prefixes = { $"http://{appSettings.ServerSetting.ServerIp}:{appSettings.ServerSetting.ServerPort}/" };
            ServerAPI server = new ServerAPI(prefixes);

            if (appSettings.UserSetting.MinimizeConsole)
            {
                _msg.Dbg("Inicia la ventana de comandos minimizada.");
                var handle = GetConsoleWindow();
                ShowWindow(handle, SW_MINIMIZE);
            }

            if (appSettings.UserSetting.OpenBrowser)
            {
                _msg.Dbg("Inicia el navegador con la pagina index del servidor.");
                string url = $"http://{appSettings.ServerSetting.ServerIp}:{appSettings.ServerSetting.ServerPort}/";
                Process.Start(new ProcessStartInfo(url) { UseShellExecute = true });
            }

            DeviceValidator deviceValidator = new DeviceValidator();
            if (deviceValidator._deviceConnected)
            {
                _msg.Inf($"Servidor iniciado en http://{appSettings.ServerSetting.ServerIp}:{appSettings.ServerSetting.ServerPort}/");
                server.Start().Wait();
            }
            else
            {
                _msg.Ftl($"No se inicia el servidor por falla en la validacion de credenciales: {deviceValidator._deviceConnected}");
            }
        }
    }
}
