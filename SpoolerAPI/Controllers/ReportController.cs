using Newtonsoft.Json;
using SpoolerAPI.Models;
using SpoolerAPI.PrinterComm;
using System.IO;
using System.Net;
using System.Text;

namespace SpoolerAPI.Controllers
{
    internal class ReportController
    {
        private static PrinterHka printer;
        private static Class _msg = new Class();

        public static void ReportX(HttpListenerContext context)
        {
            _msg.Wrn("Solicitud 'ReportX' iniciada en " + context.Request.Url);

            printer = new PrinterHka();
            printer.PFopen();
            var reportResult = printer.PFreportX();
            printer.PFclose();

            string json = JsonConvert.SerializeObject(reportResult);

            context.Response.ContentType = "application/json";
            byte[] buffer = Encoding.UTF8.GetBytes(json);
            context.Response.ContentLength64 = buffer.Length;
            using (Stream outputStream = context.Response.OutputStream)
            {
                outputStream.Write(buffer, 0, buffer.Length);
            }

            context.Response.StatusCode = (int)HttpStatusCode.OK;
            context.Response.Close();

            _msg.Inf("Respuesta 'ReportX' : " + json);
        }

        public static void ReportZ(HttpListenerContext context)
        {
            _msg.Wrn("Solicitud 'ReportZ' iniciada en " + context.Request.Url);

            printer = new PrinterHka();
            printer.PFopen();
            var reportResult = printer.PFreportZ();
            printer.PFclose();

            string json = JsonConvert.SerializeObject(reportResult);

            context.Response.ContentType = "application/json";
            byte[] buffer = Encoding.UTF8.GetBytes(json);
            context.Response.ContentLength64 = buffer.Length;
            using (Stream outputStream = context.Response.OutputStream)
            {
                outputStream.Write(buffer, 0, buffer.Length);
            }

            context.Response.StatusCode = (int)HttpStatusCode.OK;
            context.Response.Close();

            _msg.Inf("Respuesta 'ReportZ' : " + json);
        }

        public static void UploadStatus(HttpListenerContext context)
        {
            _msg.Wrn("Solicitud 'UploadStatus' iniciada en " + context.Request.Url);

            printer = new PrinterHka();
            printer.PFopen();
            printer.FPuploadStatus();
            printer.PFclose();

            context.Response.StatusCode = (int)HttpStatusCode.OK;
            context.Response.Close();
        }

    }
}