using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net;
using System.Text;
using System.Threading.Tasks;

namespace SpoolerAPI.Controllers
{
    internal class PagesController
    {
        public static void ShowHomePage(HttpListenerContext context)
        {
            // Leer el archivo HTML
            string html = File.ReadAllText("Views/index.html");

            // Establecer el tipo de contenido de la respuesta HTTP
            context.Response.ContentType = "text/html";

            // Escribir la respuesta HTTP
            using (StreamWriter writer = new StreamWriter(context.Response.OutputStream))
            {
                writer.Write(html);
            }
        }
    }
}
