using SpoolerAPI.Controllers;
using System.Net;
using System.Threading.Tasks;

namespace SpoolerAPI
{
    public class ServerAPI
    {
        private readonly HttpListener _httpListener;

        public ServerAPI(string[] prefixes)
        {
            _httpListener = new HttpListener();
            foreach (string prefix in prefixes)
            {
                _httpListener.Prefixes.Add(prefix);
            }
        }

        public void Stop()
        {
            _httpListener.Stop();
            _httpListener.Close();
        }

        public async Task Start()
        {
            _httpListener.Start();
            while (_httpListener.IsListening)
            {
                HttpListenerContext context = await _httpListener.GetContextAsync();
                await ProcessRequestAsync(context);
            }
        }

        private async Task ProcessRequestAsync(HttpListenerContext context)
        {
            if (context.Request.HttpMethod == "GET" && context.Request.Url.AbsolutePath == "/")
            {
                PagesController.ShowHomePage(context);
                return;
            }

            if (context.Request.HttpMethod == "GET" && context.Request.Url.AbsolutePath == "/api/ping")
            {
                CheckController.CheckServer(context);
                return;
            }

            if (context.Request.HttpMethod == "GET" && context.Request.Url.AbsolutePath == "/api/check")
            {
                CheckController.CheckPrinter(context);
                return;
            }

            if (context.Request.HttpMethod == "GET" && context.Request.Url.AbsolutePath == "/api/info")
            {
                CheckController.InfoPrinter(context);
                return;
            }

            if (context.Request.HttpMethod == "GET" && context.Request.Url.AbsolutePath == "/api/status")
            {
                CheckController.StatusPrinter(context);
                return;
            }

            if (context.Request.HttpMethod == "POST" && context.Request.Url.AbsolutePath == "/api/invoice")
            {
                InvoiceController.Invoice(context);
                return;
            }

            if (context.Request.HttpMethod == "GET" && context.Request.Url.AbsolutePath == "/api/reportx")
            {
                ReportController.ReportX(context);
                return;
            }

            if (context.Request.HttpMethod == "GET" && context.Request.Url.AbsolutePath == "/api/reportz")
            {
                ReportController.ReportZ(context);
                return;
            }

            if (context.Request.HttpMethod == "GET" && context.Request.Url.AbsolutePath == "/api/uploadstatus")
            {
                ReportController.UploadStatus(context);
                return;
            }

            await Task.Delay(1);
        }
    }
}