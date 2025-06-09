using Serilog;
using System;
using TfhkaNet.IF;
using TfhkaNet.IF.VE;
using SpoolerAPI.Models;
using System.IO.Ports;
using System.Text;
using System.Runtime;
using Newtonsoft.Json;
using System.IO;

namespace SpoolerAPI.PrinterComm
{
    public class PrinterHka
    {
        private readonly Tfhka oTfhka;
        private readonly AppSettings _settings;
        private readonly Class _msg;
        private string cPortComm;
        private bool bResp;

        public PrinterHka()
        {
            oTfhka = new Tfhka();
            _settings = JsonConvert.DeserializeObject<AppSettings>(File.ReadAllText("appsettings.json"));
            _msg = new Class();   
        }

        public bool PFopen()
        {
            cPortComm = _settings.PrinterSetting.PrinterPort;

            if (_msg.DBG)
            {
                _msg.Dbg("Metodo PFopen " + cPortComm);
                return true;
            }
            else
            {
                try
                {
                    bResp = oTfhka.OpenFpCtrl(cPortComm);
                    if (bResp)
                    {
                        _msg.Inf("Puerto " + cPortComm + " abierto");
                    }
                    else
                    {
                        string[] ports = SerialPort.GetPortNames();
                        foreach (string port in ports)
                        {
                            cPortComm = port;
                            _msg.Dbg("Probando Puerto: " + cPortComm);
                            bResp = oTfhka.OpenFpCtrl(port);
                            if (bResp)
                            {
                                _msg.Inf("Puerto " + cPortComm + " Abierto");
                            }
                            else
                            {
                                _msg.Wrn("No se pudo abrir el puerto: " + cPortComm);
                            }
                        }
                    }
                    _msg.Dbg("PFopen: [" + bResp + "]");
                    return bResp;
                }
                catch (Exception ex)
                {
                    _msg.Err("Se produjo un error al abrir el puerto: " + cPortComm + "\n" + ex.Message);
                    return false;
                }
            }
        }

        public void PFclose()
        {
            if (_msg.DBG) { _msg.Dbg("Metodo PFclose"); }
            else { oTfhka.CloseFpCtrl(); _msg.Inf("Puerto " + cPortComm + " Cerrado"); }
        }

        public bool PFcheck()
        {
            if ( _msg.DBG) 
            {
                _msg.Dbg("Metodo PFcheck");
                return true;
            }
            else
            {
                try
                {
                    bResp = oTfhka.CheckFPrinter();
                    if (bResp)
                    {
                        _msg.Dbg("Check: [" + bResp + "]");
                        return bResp;
                    }
                    else
                    {
                        _msg.Dbg("Check: [" + bResp + "]");
                        return bResp;
                    }
                }
                catch (Exception ex)
                {
                    _msg.Err("Se produjo un error al verificar la impresora.\n" + ex.Message);
                    return false;
                }
            }
        }

        public void PFsend(string command)
        {
            if (_msg.DBG)
            {
                _msg.Dbg("Metodo PFsend");
                _msg.Dbg("IntTFHKA SendCmd("+command+")");
            }
            else
            {
                try
                {
                    if (PFcheck())
                    {
                        bResp = oTfhka.SendCmd(command);
                        if (!bResp)
                        {
                            _msg.Err("Error en el envio del comando: " + command);
                            throw (new Exception(string.Format("Error en el envio del comando: {0}\r\n{1}", command, cPortComm)));
                        }
                    }
                    else
                    {
                        _msg.Err("Error de conexión!\r\nVerifique el puerto " + cPortComm + " por favor...");
                        throw (new Exception(string.Format("Error de conexión!\r\nVerifique el puerto '{0}' por favor...", cPortComm)));
                    }
                }
                catch (Exception ex)
                {
                    _msg.Err("Error en el envio del comando: " + command + "\n" + ex.Message);
                }
            }
        }

        public PrinterStatus FPstatus()
        {
            if (_msg.DBG)
            {
                _msg.Dbg("Metodo FPstatus");
                _msg.Dbg("PrinterStatus GetPrinterStatus()");
                return null;
            }
            else
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

                        _msg.Inf("Retorno: [" + ErrorValidity + "] | Status: [" + IFStatusCode + "] "
                            + IFStatusInfo + " | Error: [" + IFErrorCode + "] " + IFErrorInfo);
                        return oGetPS;
                    }
                }
                catch (Exception ex)
                {
                    _msg.Err("Se produjo un error en la verificacion de la impresora: " + ex.Message);
                }
                return oGetPS;
            }   
        }

        public void FPuploadStatus()
        {
            if (_msg.DBG)
            {
                _msg.Dbg("Metodo FPuploadStatus");
                _msg.Dbg("bool UploadStatusCmd(string Cmd, string file)");
            }
            else
            {
                try
                {
                    if (PFcheck())
                    {
                        oTfhka.UploadStatusCmd("S1", "Report/StatusS1.txt");
                        oTfhka.UploadStatusCmd("S2", "Report/StatusS2.txt");
                        oTfhka.UploadStatusCmd("S3", "Report/StatusS3.txt");
                        oTfhka.UploadStatusCmd("S4", "Report/StatusS4.txt");
                        oTfhka.UploadStatusCmd("S5", "Report/StatusS5.txt");
                        oTfhka.UploadStatusCmd("S8E", "Report/StatusS8E.txt");
                        oTfhka.UploadStatusCmd("S8P", "Report/StatusS8P.txt");
                        _msg.Inf("Reportes Almacenados en: /Report/StatusXX.txt");
                    }
                }
                catch (Exception ex)
                {
                    _msg.Err("Se produjo un error en la descarga de reportes: " + ex.Message);
                }
            }
        }

        public int PFlastInvoice()
        {
            if (_msg.DBG)
            {
                _msg.Dbg("Metodo PFlastInvoice");
                _msg.Dbg("S1PrinterData GetS1PrinterData() [LastInvoiceNumber]");
                return 99991;
            }
            else
            {
                try
                {
                    if (PFcheck())
                    {
                        var oGetS1 = oTfhka.GetS1PrinterData();
                        _msg.Inf("Ultima factura registrada en la impresora: " + oGetS1.LastInvoiceNumber);
                        return oGetS1.LastInvoiceNumber;
                    }
                }
                catch (Exception ex)
                {
                    _msg.Err("Se produjo un error al obtener el ultimo numero de factura [se retorna 0]: " + ex.Message);
                    return 0;
                }
            }
            return 1;
        }

        public int PFlastCreditNote()
        {
            if (_msg.DBG)
            {
                _msg.Dbg("Metodo PFlastCreditNote");
                _msg.Dbg("S1PrinterData GetS1PrinterData() [LastCreditNoteNumber]");
                return 99992;
            }
            else
            {
                try
                {
                    if (PFcheck())
                    {
                        var oGetS1 = oTfhka.GetS1PrinterData();
                        _msg.Inf("Ultima nota de credito registrada en la impresora: " + oGetS1.LastCreditNoteNumber);
                        return oGetS1.LastCreditNoteNumber;
                    }
                }
                catch (Exception ex)
                {
                    _msg.Err("Se produjo un error al obtener el ultimo numero de nota de credito [se retorna 0]: " + ex.Message);
                    return 0;
                }
            }
            return 1;
        }

        public string PFregisteredRif()
        {
            if (_msg.DBG)
            {
                _msg.Dbg("Metodo PFregisteredRif");
                _msg.Dbg("S5PrinterData GetS5PrinterData() [RIF]");
                return "J317052900";
            }
            else
            {
                try
                {
                    if (PFcheck())
                    {
                        var oGetS5 = oTfhka.GetS5PrinterData();
                        _msg.Inf("RIF Registrado: " + oGetS5.RIF);
                        return oGetS5.RIF;
                    }
                }
                catch (Exception ex)
                {
                    _msg.Err("Se produjo un error al obtener el RIF: " + ex.Message);
                    return "J312171197";
                }
            }
            return "J123456789";
        }

        public string PFregisteredSerial()
        {
            if (_msg.DBG)
            {
                _msg.Dbg("Metodo PFregisteredSerial");
                _msg.Dbg("S5PrinterData GetS5PrinterData() [RegisteredMachineNumber]");
                return "J317052900";
            }
            else
            {
                try
                {
                    if (PFcheck())
                    {
                        var oGetS5 = oTfhka.GetS5PrinterData();
                        _msg.Inf("SERIAL Registrado: " + oGetS5.RegisteredMachineNumber);
                        return oGetS5.RegisteredMachineNumber;
                    }
                }
                catch (Exception ex)
                {
                    _msg.Err("Se produjo un error al obtener el SERIAL: " + ex.Message);
                    return "Z1B1234567";
                }
            }
            return "Z1A0000000";
        }

        public ReportResult PFreportX()
        {
            var result_default = new ReportResult
            {
                Success = false,
                Message = "Ocurrio una falla en la impresion del reporte X."
            };

            if (_msg.DBG)
            {
                _msg.Dbg("Metodo PFreportX");
                _msg.Dbg("void PrintXReport() [SendCmd(\"I0X\")]");
            }
            else
            {
                try
                {
                    if (PFcheck())
                    {
                        oTfhka.PrintXReport();
                        _msg.Inf("El reporte X se ha impreso correctamente.");
                        var result = new ReportResult
                        {
                            Success = true,
                            Message = "El reporte X se ha impreso exitosamente."
                        };
                        return result;
                    }
                }
                catch (Exception ex)
                {
                    _msg.Err("Se produjo un error al imprimir el reporte X: " + ex.Message);
                    var result = new ReportResult
                    {
                        Success = false,
                        Message = "El reporte X no fue impreso exitosamente."
                    };
                    return result;
                }
            }
            return result_default;
        }

        public ReportResult PFreportZ()
        {
            var result_default = new ReportResult
            {
                Success = false,
                Message = "Ocurrio una falla en la impresion del reporte Z."
            };

            if (_msg.DBG)
            {
                _msg.Dbg("Metodo PFreportZ");
                _msg.Dbg("void PrintZReport() [SendCmd(\"I0Z\")]");
            }
            else
            {
                try
                {
                    if (PFcheck())
                    {
                        oTfhka.PrintZReport();
                        _msg.Inf("El reporte Z se ha impreso correctamente.");
                        var result = new ReportResult
                        {
                            Success = true,
                            Message = "El reporte Z se ha impreso exitosamente."
                        };
                        return result;
                    }
                }
                catch (Exception ex)
                {
                    _msg.Err("Se produjo un error al imprimir el reporte Z: " + ex.Message);
                    var result = new ReportResult
                    {
                        Success = false,
                        Message = "El reporte Z no fue impreso exitosamente."
                    };
                    return result;
                }
            }
            return result_default;
        }
    }
}
