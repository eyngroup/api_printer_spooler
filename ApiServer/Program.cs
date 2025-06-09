using System;
using System.Web.Http;
using Microsoft.Owin.Hosting;
using Owin;
using Newtonsoft.Json;
using NLog;

namespace ApiServer
{
    public class Startup
    {
        public void Configuration(IAppBuilder app)
        {
            var config = new HttpConfiguration();
            
            // Configurar rutas
            config.MapHttpAttributeRoutes();
            config.Routes.MapHttpRoute(
                name: "DefaultApi",
                routeTemplate: "api/{controller}/{id}",
                defaults: new { id = RouteParameter.Optional }
            );

            // Configurar JSON
            config.Formatters.JsonFormatter.SerializerSettings = new JsonSerializerSettings
            {
                Formatting = Formatting.Indented,
                NullValueHandling = NullValueHandling.Ignore
            };

            app.UseWebApi(config);
        }
    }

    class Program
    {
        private static readonly ILogger Logger = LogManager.GetCurrentClassLogger();
        private const string BaseAddress = "http://localhost:9000/";

        static void Main()
        {
            try
            {
                using (WebApp.Start<Startup>(BaseAddress))
                {
                    Logger.Info($"Servidor iniciado en {BaseAddress}");
                    Logger.Info("Presione cualquier tecla para detener el servidor...");
                    
                    Console.WriteLine($"Servidor iniciado en {BaseAddress}");
                    Console.WriteLine("Presione cualquier tecla para detener el servidor...");
                    Console.ReadKey();
                }
            }
            catch (Exception ex)
            {
                Logger.Error(ex, "Error al iniciar el servidor");
                Console.WriteLine($"Error: {ex.Message}");
            }
        }
    }
}
