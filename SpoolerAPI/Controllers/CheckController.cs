using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using SpoolerAPI.Models;
using SpoolerAPI.PrinterComm;
using System.IO;
using System.Net;
using System.Text;

namespace SpoolerAPI.Controllers
{
    internal class CheckController
    {
        private static PrinterHka printer;
        private static Class _msg = new Class();

        public static void CheckServer(HttpListenerContext context)
        {

            var responseJson = new JObject
            {
                ["connect"] = true
            };

            string json = JsonConvert.SerializeObject(responseJson);

            context.Response.ContentType = "application/json";
            byte[] buffer = Encoding.UTF8.GetBytes(json);
            context.Response.ContentLength64 = buffer.Length;
            using (Stream outputStream = context.Response.OutputStream)
            {
                outputStream.Write(buffer, 0, buffer.Length);
            }

            context.Response.StatusCode = (int)HttpStatusCode.OK;
            context.Response.Close();

            _msg.Inf("Respuesta 'CheckServer' : " + json);
        }

        public static void CheckPrinter(HttpListenerContext context)
        {
            _msg.Wrn("Solicitud 'CheckPrinter' iniciada en " + context.Request.Url);

            printer = new PrinterHka();
            printer.PFopen();
            printer.PFcheck();
            printer.PFclose();

            context.Response.StatusCode = (int)HttpStatusCode.OK;
            context.Response.Close();
        }

        public static void InfoPrinter(HttpListenerContext context)
        {
            _msg.Wrn("Solicitud 'InfoPrinter' iniciada en " + context.Request.Url);

            printer = new PrinterHka();
            printer.PFopen();
            var infoPrinter = printer.PFregisteredRif();
            printer.PFclose();

            string json = JsonConvert.SerializeObject(infoPrinter);

            context.Response.ContentType = "application/json";
            byte[] buffer = Encoding.UTF8.GetBytes(json);
            context.Response.ContentLength64 = buffer.Length;
            using (Stream outputStream = context.Response.OutputStream)
            {
                outputStream.Write(buffer, 0, buffer.Length);
            }

            context.Response.StatusCode = (int)HttpStatusCode.OK;
            context.Response.Close();

            _msg.Inf("Respuesta 'InfoPrinter' : " + json);
        }

        public static void StatusPrinter(HttpListenerContext context)
        {
            _msg.Wrn("Solicitud 'StatusPrinter' iniciada en " + context.Request.Url);

            printer = new PrinterHka();
            printer.PFopen();
            var statusPrinter = printer.FPstatus();
            printer.PFclose();

            string StatusDescription;
            string ErrorDescription;
           
            if (_msg.DBG)
            {
                StatusDescription = "Developer";
                ErrorDescription = "Null";
            }
            else
            {
                StatusDescription = statusPrinter.PrinterStatusDescription;
                ErrorDescription = statusPrinter.PrinterErrorDescription;
            }
                
            var responseJson = new JObject
            {
                ["Printer Status"] = StatusDescription,
                ["Printer Error"] = ErrorDescription
            };

            string json = JsonConvert.SerializeObject(responseJson);

            context.Response.ContentType = "application/json";
            byte[] buffer = Encoding.UTF8.GetBytes(json);
            context.Response.ContentLength64 = buffer.Length;
            using (Stream outputStream = context.Response.OutputStream)
            {
                outputStream.Write(buffer, 0, buffer.Length);
            }

            context.Response.StatusCode = (int)HttpStatusCode.OK;
            context.Response.Close();

            _msg.Inf("Printer Status: " + StatusDescription + " | Printer Error: " + ErrorDescription);
        }
    }
}
