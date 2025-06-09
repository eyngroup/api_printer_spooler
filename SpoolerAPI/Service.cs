using System.ServiceProcess;
using Newtonsoft.Json;
using SpoolerAPI.Models;
using System.IO;

namespace SpoolerAPI
{
    internal class Service
    {
        public class SpoolerService : ServiceBase
        {
            private ServerAPI server;

            public SpoolerService()
            {
                ServiceName = "SpoolerService";
            }

            protected override void OnStart(string[] args)
            {
                var appSettings = JsonConvert.DeserializeObject<AppSettings>(File.ReadAllText("appsettings.json"));

                // Inicializa el servidor
                server = new ServerAPI(new string[] { $"http://{appSettings.ServerSetting.ServerIp}:{appSettings.ServerSetting.ServerPort}/" });
                server.Start().Wait();
            }

            protected override void OnStop()
            {
                // Detiene el servidor
                server.Stop();
            }

            //Para instalar el servicio, debes compilar el proyecto como un archivo.exe y luego ejecutar el siguiente
            //comando desde una ventana de comando con privilegios elevados:
            //sc.exe create SpoolerService binPath = "C:\ruta\a\archivo.exe"
            //Reemplaza C:\ruta\a\archivo.exe con la ruta completa del archivo.exe generado por tu proyecto.Esto creará
            //el servicio y lo registrará en el sistema. Luego puedes iniciar y detener el servicio desde la ventana de
            //Servicios de Windows o utilizando los comandos net start SpoolerService y net stop SpoolerService.
        }
    }
}
