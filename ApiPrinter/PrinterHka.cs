using Newtonsoft.Json.Linq;
using System;
using System.Collections.Generic;
using System.IO.Ports;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using TfhkaNet.IF;
using TfhkaNet.IF.VE;
using System.Configuration;


namespace ApiPrinter
{
    public class PrinterHka
    {
        private readonly Tfhka oTfhka;
        private string cPortComm = ConfigurationManager.AppSettings["PortComm"];
        private bool bResp;
        private RichTextBox txtLog;

        public PrinterHka(RichTextBox txtLog)
        {
            this.txtLog = txtLog;
            oTfhka = new Tfhka();
        }

        public bool PFopen()
        {
            
            try
            {
                bResp = oTfhka.OpenFpCtrl(cPortComm);
                if (bResp)
                {
                    txtLog.Invoke(new Action(() => txtLog.AppendText($"Puerto {cPortComm} Abierto. \n")));
                }
                else
                {
                    //txtLog.Invoke(new Action(() => txtLog.AppendText($"Puerto {cPortComm} en AppConfig. \n")));
                    //string[] ports = SerialPort.GetPortNames();
                    //foreach (string port in ports)
                    //{
                    //    cPortComm = port;
                    //    txtLog.Invoke(new Action(() => txtLog.AppendText($"Probando Puerto: {cPortComm} \n")));
                    //    bResp = oTfhka.OpenFpCtrl(port);
                    //    if (bResp)
                    //    {
                    //        txtLog.Invoke(new Action(() => txtLog.AppendText($"Puerto {cPortComm} Abierto \n")));
                    //    }
                    //    else
                    //    {
                    //        txtLog.Invoke(new Action(() => txtLog.AppendText($"No se pudo abrir el puerto: {cPortComm} \n")));
                    //    }
                    //}
                    txtLog.Invoke(new Action(() => txtLog.AppendText($"No se pudo abrir el puerto: {cPortComm} \n")));
                }
                return bResp;
            }
            catch (Exception ex)
            {
                txtLog.Invoke(new Action(() => txtLog.AppendText("Se produjo un error al abrir el puerto: " + cPortComm + "\n" + ex.Message + "\n")));
                return false;
            }
        }

        public void PFclose()
        {
            oTfhka.CloseFpCtrl(); txtLog.Invoke(new Action(() => txtLog.AppendText($"Puerto {cPortComm} Cerrado \n")));
        }

        public bool PFcheck()
        {
            try
            {
                bResp = oTfhka.CheckFPrinter();
                txtLog.Invoke(new Action(() => txtLog.AppendText($"Check {bResp} \n")));
                return bResp;
            }
            catch (Exception ex)
            {
                txtLog.Invoke(new Action(() => txtLog.AppendText("Se produjo un error al verificar la impresora.\n" + ex.Message + "\n")));
                return false;
            }
        }

        public void PFsend(string command)
        {
            try
            {
                if (PFcheck())
                {
                    bResp = oTfhka.SendCmd(command);
                    if (!bResp)
                    {
                        txtLog.Invoke(new Action(() => txtLog.AppendText($"Error en el envio del comando: {command} \n")));
                        throw (new Exception(string.Format("Error en el envio del comando: {0}\r\n{1}", command, cPortComm)));
                    }
                }
                else
                {
                    txtLog.Invoke(new Action(() => txtLog.AppendText($"Error de conexión!\r\nVerifique el puerto {cPortComm} por favor... \n")));
                    throw (new Exception(string.Format("Error de conexión!\r\nVerifique el puerto '{0}' por favor...", cPortComm)));
                }
            }
            catch (Exception ex)
            {
                txtLog.Invoke(new Action(() => txtLog.AppendText($"Error en el envio del comando: {command} \n" + ex.Message + "\n")));
            }
        }

        public PrinterStatus PFstatus()
        {
            var oGetPS = oTfhka.GetPrinterStatus();
            try
            {
                if (PFcheck())
                {
                    bool ErrorValidity = oGetPS.ErrorValidity;                  // Validez del Error.
                    int IFStatusCode = oGetPS.PrinterStatusCode;                // Valor entero del Status. anexo 1
                    string IFStatusInfo = oGetPS.PrinterStatusDescription;      // Descripción del Status.
                    int IFErrorCode = oGetPS.PrinterErrorCode;                  // Valor entero del Error. Anexo2
                    string IFErrorInfo = oGetPS.PrinterErrorDescription;        // Descripción del Error.

                    txtLog.Invoke(new Action(() => txtLog.AppendText($"Retorno: [{ErrorValidity}] | Status: [{IFStatusCode}] \n {IFStatusInfo} | Error: [{IFErrorCode}] {IFErrorInfo} \n")));
                    return oGetPS;
                }
            }
            catch (Exception ex)
            {
                txtLog.Invoke(new Action(() => txtLog.AppendText("Se produjo un error en la verificacion de la impresora: " + ex.Message + "\n")));
            }
            return oGetPS;
        }

        public (int, int) PFlastNumber(string typedoc)
        {
            try
            {
                if (PFcheck())
                {
                    var oGetS1 = oTfhka.GetS1PrinterData();
                    txtLog.Invoke(new Action(() => txtLog.AppendText($"Ultimo reporte Z: {oGetS1.DailyClosureCounter} \n")));
                    if (typedoc == "FAV")
                    {
                        txtLog.Invoke(new Action(() => txtLog.AppendText($"Ultima factura: {oGetS1.LastInvoiceNumber} \n")));
                        return (oGetS1.LastInvoiceNumber, oGetS1.DailyClosureCounter);
                    }
                    else
                    {
                        txtLog.Invoke(new Action(() => txtLog.AppendText($"Ultima Nota de Credito: {oGetS1.LastCreditNoteNumber} \n")));
                        return (oGetS1.LastCreditNoteNumber, oGetS1.DailyClosureCounter);
                    }
                }
            }
            catch (Exception ex)
            {
                txtLog.Invoke(new Action(() => txtLog.AppendText($"Se produjo un error al obtener el ultimo numero de: {typedoc} [se retorna 0]: {ex.Message} \n")));
                return (0, 0);
            }
            return (1, 1);
        }

        public string PFregisteredSerial()
        {
            try
            {
                if (PFcheck())
                {
                    var oGetS5 = oTfhka.GetS5PrinterData();
                    txtLog.Invoke(new Action(() => txtLog.AppendText($"SERIAL: {oGetS5.RegisteredMachineNumber} \n")));
                    return oGetS5.RegisteredMachineNumber;
                }
            }
            catch (Exception ex)
            {
                txtLog.Invoke(new Action(() => txtLog.AppendText($"Se produjo un error al obtener el SERIAL: {ex.Message} \n")));
                return "Z1B1234567";
            }
            return "Z1A0000000";
        }

        public string PFreportX()
        {
            try
            {
                if (PFcheck())
                {
                    oTfhka.PrintXReport();
                    txtLog.Invoke(new Action(() => txtLog.AppendText("El reporte X se ha impreso correctamente. \n")));
                    return "El reporte X se ha impreso exitosamente.";
                }
            }
            catch (Exception ex)
            {
                txtLog.Invoke(new Action(() => txtLog.AppendText($"Se produjo un error al imprimir el reporte X: {ex.Message} \n")));
                return "El reporte X no fue impreso exitosamente.";
            }
            return "Ocurrio una falla en la impresion del reporte X.";
        }

        public string PFreportZ()
        {
            try
            {
                if (PFcheck())
                {
                    oTfhka.PrintZReport();
                    txtLog.Invoke(new Action(() => txtLog.AppendText("El reporte Z se ha impreso correctamente. \n")));
                    return "El reporte Z se ha impreso exitosamente.";
                }
            }
            catch (Exception ex)
            {
                txtLog.Invoke(new Action(() => txtLog.AppendText($"Se produjo un error al imprimir el reporte Z: {ex.Message} \n")));
                return "El reporte Z no fue impreso exitosamente.";
            }
            return "Ocurrio una falla en la impresion del reporte Z.";
        }
    }
}
