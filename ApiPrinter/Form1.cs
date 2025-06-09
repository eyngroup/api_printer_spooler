using Newtonsoft.Json.Linq;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Net;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Configuration;

namespace ApiPrinter
{
    public partial class Form1 : Form
    {
        HttpListener _httpListener;
        Thread _responseThread;
        
        bool debug = bool.Parse(ConfigurationManager.AppSettings["Debug"]);
        string ipServer = ConfigurationManager.AppSettings["IpServer"];
        int portServer = int.Parse(ConfigurationManager.AppSettings["PortServer"]);

        public Form1()
        {
            //string ipServer = ConfigurationManager.AppSettings["IpServer"];
            //int portServer = int.Parse(ConfigurationManager.AppSettings["PortServer"]);
            InitializeComponent();
            //this.ControlBox = false;
            _httpListener = new HttpListener();
            _httpListener.Prefixes.Add($"http://{ipServer}:{portServer}/");
        }

        private void btnStart_Click(object sender, EventArgs e)
        {
            _httpListener.Start();
            _responseThread = new Thread(ResponseThread);
            _responseThread.Start();
            txtLog.AppendText("Servidor iniciado.\n");
        }

        private void btnStop_Click(object sender, EventArgs e)
        {
            _httpListener.Stop();
            _responseThread.Join();
            txtLog.AppendText("Servidor detenido. \n");
            txtLog.AppendText("La Aplicacion se cerrara. \n");
            Thread.Sleep(1000);
            Application.Exit();

        }

        private void ResponseThread()
        {
            var printer = new PrinterHka(txtLog);
            if (!printer.PFopen() || !printer.PFcheck())
            {
                txtLog.Invoke(new Action(() => txtLog.AppendText("No se pudo establecer la conexión con la impresora.\n")));
                return;
                //this.Invoke(new Action(() => btnStop_Click(this, EventArgs.Empty))); // Llama al evento btnStop_Click en el hilo de la interfaz de usuario
            }


            while (_httpListener.IsListening)
            {
                try
                {
                    var context = _httpListener.GetContext();
                    var response = context.Response;

                    if (context.Request.Url.AbsolutePath == "/api/invoice")
                    {
                        using (var reader = new StreamReader(context.Request.InputStream, context.Request.ContentEncoding))
                        {
                            var json = reader.ReadToEnd();
                            var data = JsonConvert.DeserializeObject<Dictionary<string, object>>(json);

                            var DocType = data["type"].ToString();
                            var DocLine = (JArray)data["cmd"];

                            foreach (var line in DocLine)
                            {
                                txtLog.Invoke(new Action(() => txtLog.AppendText(line.ToString() + "\n")));
                                if (!debug)
                                {
                                    printer.PFsend(line.ToString());
                                }
                                Thread.Sleep(750); // pausa de 750 milisegundos
                            }

                            Thread.Sleep(750);
                            string printer_serial = printer.PFregisteredSerial();
                            Thread.Sleep(750);
                            (int printer_last_number, int printer_report_z) = printer.PFlastNumber(DocType);
                            string formatted_number = printer_last_number.ToString("D10");
                            string formatted_report = printer_report_z.ToString("D6");

                            // Devolver un JSON como respuesta al cliente
                            var responseString = JsonConvert.SerializeObject(new
                            {
                                PrinterSerial = printer_serial,
                                PrinterCounterZ = formatted_report,
                                PrinterNumber = formatted_number,
                                PrinterDate = DateTime.Now.ToString("yyyy-MM-dd"),
                                PrinterBase = 0,
                                PrinterTax = 0,
                                PrinterIgt = 0
                            });
                            byte[] buffer = Encoding.UTF8.GetBytes(responseString);
                            response.ContentLength64 = buffer.Length;
                            var output = response.OutputStream;
                            output.Write(buffer, 0, buffer.Length);
                            output.Close();
                        }
                    }


                    if (context.Request.Url.AbsolutePath == "/api/printer_x")
                    {
                        string resp = null;
                        try
                        {
                            if (!debug)
                            {
                                resp = printer.PFreportX();
                            }
                            Thread.Sleep(1000); // pausa de 1000 milisegundos

                            // Devolver un JSON como respuesta al cliente
                            var responseString = JsonConvert.SerializeObject(new { status = resp, code = 200 });
                            byte[] buffer = System.Text.Encoding.UTF8.GetBytes(responseString);
                            response.ContentLength64 = buffer.Length;
                            var output = response.OutputStream;
                            output.Write(buffer, 0, buffer.Length);
                            output.Close();
                        }
                        catch (Exception ex)
                        {
                            txtLog.Invoke(new Action(() => txtLog.AppendText($"Se produjo un error al procesar el reporte X: {ex.Message}\n")));

                            // Devolver un JSON como respuesta al cliente
                            var responseString = JsonConvert.SerializeObject(new { status = "Error", code = 400 });
                            byte[] buffer = System.Text.Encoding.UTF8.GetBytes(responseString);
                            response.ContentLength64 = buffer.Length;
                            var output = response.OutputStream;
                            output.Write(buffer, 0, buffer.Length);
                            output.Close();
                        }
                    }

                    if (context.Request.Url.AbsolutePath == "/api/printer_z")
                    {
                        string resp = null;
                        try
                        {
                            if (!debug)
                            {
                                resp = printer.PFreportZ();
                            }
                            Thread.Sleep(1000); // pausa de 1000 milisegundos

                            // Devolver un JSON como respuesta al cliente
                            var responseString = JsonConvert.SerializeObject(new { status = resp, code = 200 });
                            byte[] buffer = System.Text.Encoding.UTF8.GetBytes(responseString);
                            response.ContentLength64 = buffer.Length;
                            var output = response.OutputStream;
                            output.Write(buffer, 0, buffer.Length);
                            output.Close();
                        }
                        catch (Exception ex)
                        {
                            txtLog.Invoke(new Action(() => txtLog.AppendText($"Se produjo un error al procesar el reporte Z: {ex.Message}\n")));

                            // Devolver un JSON como respuesta al cliente
                            var responseString = JsonConvert.SerializeObject(new { status = "Error", code = 400 });
                            byte[] buffer = System.Text.Encoding.UTF8.GetBytes(responseString);
                            response.ContentLength64 = buffer.Length;
                            var output = response.OutputStream;
                            output.Write(buffer, 0, buffer.Length);
                            output.Close();
                        }
                    }

                    if (context.Request.Url.AbsolutePath == "/api/printer_status")
                    {
                        try
                        {

                            var resp = printer.PFstatus();
                            Thread.Sleep(1000); // pausa de 1000 milisegundos

                            // Devolver un JSON como respuesta al cliente
                            var responseString = JsonConvert.SerializeObject(new { status = resp, code = 200 });
                            byte[] buffer = System.Text.Encoding.UTF8.GetBytes(responseString);
                            response.ContentLength64 = buffer.Length;
                            var output = response.OutputStream;
                            output.Write(buffer, 0, buffer.Length);
                            output.Close();
                        }
                        catch (Exception ex)
                        {
                            txtLog.Invoke(new Action(() => txtLog.AppendText($"Se produjo un error al obtener el estatus: {ex.Message}\n")));

                            // Devolver un JSON como respuesta al cliente
                            var responseString = JsonConvert.SerializeObject(new { status = "Error", code = 400 });
                            byte[] buffer = System.Text.Encoding.UTF8.GetBytes(responseString);
                            response.ContentLength64 = buffer.Length;
                            var output = response.OutputStream;
                            output.Write(buffer, 0, buffer.Length);
                            output.Close();
                        }
                    }
                }
                catch (HttpListenerException)
                {
                    // Se lanza cuando se detiene el HttpListener
                }
                catch (Exception ex)
                {
                    txtLog.Invoke(new Action(() => txtLog.AppendText($"{ex}" + "\n")));
                }
            }
        }

        private void btnOpenUrl_Click(object sender, EventArgs e)
        {
            string url = $"http://{ipServer}:{portServer}/api/printer_x"; 
            System.Diagnostics.Process.Start(url);
        }

        private void btnOpenZ_Click(object sender, EventArgs e)
        {
            string url = $"http://{ipServer}:{portServer}/api/printer_z";
            System.Diagnostics.Process.Start(url);
        }

        private void btnStatus_Click(object sender, EventArgs e)
        {
            string url = $"http://{ipServer}:{portServer}/api/printer_status";
            System.Diagnostics.Process.Start(url);
        }

        private void txtLog_TextChanged(object sender, EventArgs e)
        {
            string fecha = DateTime.Now.ToString("yyyyMMdd"); // Obtiene la fecha actual sin la hora
            string path = $"registros{fecha}.log"; // Crea el nombre del archivo con la fecha

            using (StreamWriter sw = new StreamWriter(path))
            {
                sw.Write(txtLog.Text); // Escribe el contenido de txtLog en el archivo
            }
        }

    }
}
