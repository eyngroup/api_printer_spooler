using System;
using System.Collections.Generic;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Net.NetworkInformation;
using System.Reflection.Emit;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Forms;
using System.Xml.Linq;
using TfhkaNet.IF;
using TfhkaNet.IF.VE;
using ToolsPF.Properties;
using static System.Net.Mime.MediaTypeNames;
using static System.Windows.Forms.VisualStyles.VisualStyleElement;


namespace ToolsPF.Class
{
    public class Pagos
    {
        static public string Efectivo = "201";
        static public string Tarjeta = "213";
        static public string Divisa = "220";
        static public string Resto = "102";
    }

    public class PFtfhka
    {
        Tfhka oFiscal;
        public string cPort;
        public static bool bResp;
        public string TxtInformation;
        private ReportData oReport;
        public double _suma;
        public string cNumeroFactura;
        public double nMontoZ;
        public int nUltimoZ;
        public string cSerialPrinter;

        public PFtfhka()
        {
            oFiscal = new Tfhka();
            cPort = LoadSettings();
            bResp = false;
            DetectPrinter();
        }
        private string LoadSettings()
        {
            cPort = "COM9";
            try
            {
                XElement xmlSettings = XElement.Load("Settings.xml");
                var cPortComm =
                    (from c in xmlSettings.Descendants("Settings")
                     select c.Element("PortComm").Value).FirstOrDefault();
                if (cPortComm != null)
                    cPortComm = cPortComm.ToString();
                return cPortComm;
            }
            catch (Exception e)
            {
                MessageBox.Show(e.Message);
            }
            return cPort;
        }
        ~PFtfhka()
        {
            oFiscal.CloseFpCtrl();
            oFiscal = null;
        }
        private void OpenPort()
        {
            oFiscal.OpenFpCtrl(cPort);
        }
        private void ClosePort()
        {
            oFiscal.CloseFpCtrl();
        }
        private void DetectPrinter()
        {
            try
            {
                bResp = oFiscal.CheckFPrinter();
                if (oFiscal.OpenFpCtrl(cPort))
                {
                    bResp = oFiscal.ReadFpStatus();
                    if (!oFiscal.ReadFpStatus())
                    {
                        throw (new Exception(string.Format("Error de conexión, Estatus {0} verifique el puerto por favor...", oFiscal.Status_Error)));
                    }
                }
                else
                {
                    var cText = oFiscal.ComPort;
                    var ex = oFiscal.Estado;
                    throw (new Exception(string.Format("Error al abrir el puerto {0}", cText)));
                }
            }
            catch (TfhkaNet.IF.PrinterException)
            {
                MessageBox.Show(string.Format("{0}\r\nEstatus: {1}", oFiscal.Estado.ToUpper(), oFiscal.Status_Error.ToUpper()), "PrinterException");
            }
            catch (Exception ex)
            {
                MessageBox.Show(string.Format("Error: {0}", ex.Message.ToUpper()), "SystemException");
            }
        }
        public void CheckPrinter()
        {
            bResp = oFiscal.CheckFPrinter();
            if (bResp)
            {
                oFiscal.UploadStatusCmd("S1", "StatusS1.txt");
                oFiscal.UploadStatusCmd("S2", "StatusS2.txt");
                oFiscal.UploadStatusCmd("S3", "StatusS3.txt");
                oFiscal.UploadStatusCmd("S4", "StatusS4.txt");
                oFiscal.UploadStatusCmd("S5", "StatusS5.txt");
                oFiscal.UploadStatusCmd("S8E", "StatusS8E.txt");
                oFiscal.UploadStatusCmd("S8P", "StatusS8P.txt");
                MessageBox.Show("Online Printer", "CheckFPrinter");
            }
            else
            {
                MessageBox.Show("Offline Printer", "CheckFPrinter");
            }
        }
        public void SendCommand(string cCmd)
        {
            oFiscal.SendCmd(cCmd);
        }
        public void ReportX()
        {
            try
            {
                oFiscal.SendCmd("I0X");  
                //oFiscal.PrintXReport();
            }
            catch (TfhkaNet.IF.PrinterException)
            {
                MessageBox.Show(string.Format("{0}\r\nEstatus: {1}", oFiscal.Estado.ToUpper(), oFiscal.Status_Error.ToUpper()), "PrinterException");
            }
            catch (Exception x)
            {
                MessageBox.Show(string.Format("Error: {0}", x.Message.ToUpper()), "SystemException");
            }
        }
        public void ReportZ()
        {
            try
            {
                S1PrinterData d = oFiscal.GetS1PrinterData();
                if (d.QuantityOfInvoicesToday < 1)
                {
                    throw new Exception("No hay facturas aún hoy");
                }
                //nUltimoZ = d.DailyClosureCounter + 2;
                oFiscal.SendCmd("I0Z"); //oFiscal.PrintZReport();
            }
            catch (TfhkaNet.IF.PrinterException)
            {
                MessageBox.Show(string.Format("{0}\r\nEstatus: {1}", oFiscal.Estado.ToUpper(), oFiscal.Status_Error.ToUpper()), "PrinterException");
            }
            catch (Exception x)
            {
                MessageBox.Show(string.Format("Error: {0}", x.Message.ToUpper()), "SystemException");
            }

        }      


        public bool GenerarFactura(DataTable tDoc, DataTable tMov, DataTable tPag)
        {
            string cCmd;

            #region <Header>
            string cRef, dFchD, cCli, cRif, cDir, cTel, cCon = "CONTADO", cCaj;
            foreach (DataRow row in tDoc.Rows)
            {

                // Consulta
                cRef = Convert.ToString(row["Doc_Numero"]);
                cRif = Convert.ToString(row["Cli_Rif"]);
                cCli = Convert.ToString(row["Cli_Nombre"]);
                cDir = Convert.ToString(row["Cli_Direccion"]);
                cTel = Convert.ToString(row["Cli_Telefono"]);
                cCaj = Convert.ToString(row["User_Login"]);
                DateTime dFch = Convert.ToDateTime(row["Doc_Fecha"]);

                // Formato
                cRef = cRef.Replace("/", "").Replace(".", "");
                cRef = cRef.Substring(0, (cRef.Length < 15 ? cRef.Length : 15)).Trim(); //Max 15
                cRif = cRif.Substring(0, (cRif.Length < 12 ? cRif.Length : 12)).Trim(); //Max 32
                cCli = cCli.Substring(0, (cCli.Length < 28 ? cCli.Length : 28)).Trim(); //Max 28
                cDir = cDir.Replace(", Monagas,", "").Replace("Venezuela", "");
                cDir = cDir.Substring(0, (cDir.Length < 35 ? cDir.Length : 35)).Trim(); //Max 42 - 5
                cTel = cTel.Replace("+58", "");
                cTel = cTel.Substring(0, (cTel.Length < 34 ? cTel.Length : 34)).Trim(); //Max 42 - 5
                cCon = cCon.Substring(0, (cCon.Length < 34 ? cCon.Length : 34)).Trim(); //Max 42 - 6
                cCaj = cCaj.ToLower().Trim(); //Max 42 - 8 
                dFchD = dFch.ToString("dd-MM-yyyy");

                // Comando
                //cCmd = "iF*" + cRef; oFiscal.SendCmd(cCmd);
                //cCmd = "iD*" + dFchD; oFiscal.SendCmd(cCmd);
                cCmd = "iR*" + cRif; oFiscal.SendCmd(cCmd);
                cCmd = "iS*" + cCli; oFiscal.SendCmd(cCmd);
                cCmd = "i00Dir.:" + cDir; oFiscal.SendCmd(cCmd);
                cCmd = "i01Ref.:" + cRef; oFiscal.SendCmd(cCmd);
                //cCmd = "i01Tel.:" + cTel; oFiscal.SendCmd(cCmd);
                //cCmd = "i02Venta:" + cCon; oFiscal.SendCmd(cCmd);
                //cCmd = "i03Usuario:" + cCaj; oFiscal.SendCmd(cCmd);
                //cCmd = "@Comentario:"; //Max 40
            }
            System.Threading.Thread.Sleep(500);
            #endregion
            #region <Section>
            string cIva, cPre, cCan, cPro;
            foreach (DataRow row in tMov.Rows)
            {
                // Consulta
                cIva = (row["Iva_Codigo"]).ToString();
                if (cIva.Equals("")){ cIva = Convert.ToInt16(1).ToString();}
                else{ cIva = Convert.ToInt16(cIva).ToString();}
                cPre = Convert.ToDecimal(row["Mov_PrecioU"]).ToString("###0.00");
                cCan = Convert.ToDecimal(row["Mov_Cantidad"]).ToString("###0.000");
                cPro = Convert.ToString(row["Mov_Producto"]);

                // Formato
                cPre = cPre.Replace(",", "").Replace(".", "");
                cPre = cPre.PadLeft(10, '0');
                cCan = cCan.Replace(",", "").Replace(".", "");
                cCan = cCan.PadLeft(8, '0');
                //cPro = cPro.Replace("[", "").Replace("]", "");
                cPro = cPro.Substring(0, (cPro.Length < 40 ? cPro.Length : 40)).Trim(); //Max 66
                switch (cIva)
                {
                    case "1": cIva  = " " ; break;
                    case "2": cIva  = "!" ; break;
                    case "3": cIva  = "\""; break;
                    case "4": cIva  = "#" ; break;
                    default : cIva  = " " ; break;
                }

                // Comando
                cCmd = cIva + cPre + cCan + cPro;
                oFiscal.SendCmd(cCmd);
            }
            System.Threading.Thread.Sleep(500);
            #endregion


            //esta opcion funciono perfecto
            //cCmd = "3";
            //oFiscal.SendCmd(cCmd); // subtotal
            System.Threading.Thread.Sleep(500);
            string cPid, cPmo;
            foreach (DataRow row in tPag.Rows)
            {
                // Consulta
                cPid = Convert.ToInt16(row["Pag_ID"]).ToString();
                cPmo = Convert.ToDecimal(row["Pag_Monto"]).ToString("###0.00");

                // Formato
                cPmo = cPmo.Replace(",", "").Replace(".", "");
                cPmo = cPmo.PadLeft(12, '0');

                switch (cPid)
                {
                    case "1":  cPid = "201"; break; //Efectivo
                    case "2":  cPid = "201"; break; //Efectivo
                    case "11": cPid = "201"; break; //Efectivo
                    case "12": cPid = "213"; break; //Tarjeta
                    case "13": cPid = "220"; break; //Divisas
                    case "14": cPid = "201"; break; //Efectivo
                    case "15": cPid = "201"; break; //Efectivo
                    case "16": cPid = "201"; break; //Efectivo
                    case "17": cPid = "201"; break; //Efectivo
                    case "18": cPid = "201"; break; //Efectivo
                    default:   cPid = "102"; break; //efectivo
                }

                // Comando
                if (cPid == "220")
                {
                    cCmd = "122";
                    oFiscal.SendCmd(cCmd);
                }
                else
                {
                    cCmd = cPid + cPmo;
                    oFiscal.SendCmd(cCmd);
                }
                //System.Threading.Thread.Sleep(500);

                // cerrar factura
                cCmd = "199";
                oFiscal.SendCmd(cCmd);
                System.Threading.Thread.Sleep(500);
              
                
            }


            //bool cEfectivo = true;
            //decimal monto, topago = 0, tofact;
            //string montopago;

            //if (tPag != null)
            //{

            //}

            //if (cEfectivo)
            //{
            //    cCmd = cPid[nPid] + nPmo;
            //    bResp = oFiscal.SendCmd(cCmd);
            //}


            //string nPag_ID = Convert.ToString(oPagRow["Pag_ID"]);
            //string nPag_Monto = Convert.ToString(oPagRow["Pag_Monto"]);
            //oPrint.SendCommand(nPag_ID + nPag_Monto);






            //if (dtPagos != null)
            //{
            //    if (dtPagos.Rows.Count == 1)
            //    {
            //        if (dtPagos.Rows[0]["idpagofiscal"].ToString().Trim() != "")
            //        {
            //            cadena = "1" + dtPagos.Rows[0]["idpagofiscal"].ToString().Trim();
            //        }
            //    }
            //    else
            //    {
            //        foreach (DataRow row in dtPagos.Rows)
            //        {
            //            monto = Convert.ToDecimal(row["monto"]);

            //            if (monto > 0 && row["idpagofiscal"].ToString().Trim() != "")
            //            {
            //                montopago = monto.ToString("#####0.00");
            //                montopago = montopago.Replace(",", "").Replace(".", "");
            //                montopago = montopago.PadLeft(12, '0');

            //                cadena = "2" + row["idpagofiscal"].ToString().Trim() + montopago;
            //                respuesta = SendCmd(ref status, ref error, cadena);

            //                pagodirecto = false;
            //                topago += monto;
            //            }
            //        }

            //        if (topago > 0)
            //        {
            //            cadena = LeerStatusS2(true, 51, 13);

            //            tofact = (cadena != "" ? (Convert.ToDecimal(cadena) / 100) : totaldoc);

            //            if (topago < tofact)
            //            {
            //                monto = (tofact - topago);
            //                montopago = monto.ToString("#####0.00");
            //                montopago = montopago.Replace(",", "").Replace(".", "");
            //                montopago = montopago.PadLeft(12, '0');

            //                cadena = "201" + montopago;
            //                respuesta = SendCmd(ref status, ref error, cadena);
            //            }
            //        }
            //    }
            //}




            //ok = evalua_errores(respuesta);

            //    respuesta = SendCmd(ref status, ref error, cadena);


            //}







            //int respuesta;
            //long status = 0;
            //long error = 0;
            //string cadena;
            //

            //string descrip, cant, precio, talla, color, seriales, notas;
            //char[] tipotasa = new Char[4];
            //int i;

            //tipotasa[0] = ' ';
            //tipotasa[1] = '!';
            //tipotasa[2] = '"';
            //tipotasa[3] = '#';


            //if (abrir_puerto(puerto))
            //{
            //    rifoci = rifoci.Substring(0, (rifoci.Length < 12 ? rifoci.Length : 12)).Trim();
            //    nomcli = nomcli.Substring(0, (nomcli.Length < 80 ? nomcli.Length : 80)).Trim();
            //    dircli = dircli.Trim();

            //    if (codfiscal == "BIXOLON350" || codfiscal == "DASCOM230")
            //    {
            //        cadena = "jS" + nomcli;
            //        respuesta = SendCmd(ref status, ref error, cadena);

            //        cadena = "jR" + rifoci;
            //        respuesta = SendCmd(ref status, ref error, cadena);

            //        cadena = "j1" + "DIRECCION:" + dircli;
            //        respuesta = SendCmd(ref status, ref error, cadena);

            //        cadena = "j2" + "REF. " + referencia + " / " + cajero + " / " + estacion;
            //        respuesta = SendCmd(ref status, ref error, cadena);

            //        cadena = "j3" + "VEND." + vendedor;
            //        respuesta = SendCmd(ref status, ref error, cadena);

            //        if (!string.IsNullOrEmpty(huesped))
            //        {
            //            cadena = "j4" + "HUESPED: " + huesped;
            //            respuesta = SendCmd(ref status, ref error, cadena);
            //        }

            //        if (!string.IsNullOrEmpty(habino))
            //        {
            //            cadena = "j5" + "HAB. No: " + habino;
            //            respuesta = SendCmd(ref status, ref error, cadena);
            //        }
            //    }
            //    else
            //    {
            //        cadena = "i01 CLIENTE:" + nomcli;
            //        respuesta = SendCmd(ref status, ref error, cadena);

            //        cadena = "i02 CI/RIF :" + rifoci;
            //        respuesta = SendCmd(ref status, ref error, cadena);

            //        cadena = "i03 DIRECCION:" + dircli;
            //        respuesta = SendCmd(ref status, ref error, cadena);

            //        cadena = "i04 TELEFONO :" + tlfcli;
            //        respuesta = SendCmd(ref status, ref error, cadena);

            //        cadena = "i05 REF. " + referencia + " / " + cajero + " / " + estacion;
            //        respuesta = SendCmd(ref status, ref error, cadena);

            //        cadena = "i06 VEND." + vendedor;
            //        respuesta = SendCmd(ref status, ref error, cadena);

            //        if (!string.IsNullOrEmpty(huesped))
            //        {
            //            cadena = "i07 HUESPED: " + huesped;
            //            respuesta = SendCmd(ref status, ref error, cadena);
            //        }

            //        if (!string.IsNullOrEmpty(habino))
            //        {
            //            cadena = "i08 HAB. No: " + habino;
            //            respuesta = SendCmd(ref status, ref error, cadena);
            //        }
            //    }

            //    foreach (DataRow row in dtDetalle.Rows)
            //    {
            //        descrip = row["codigo"].ToString().Trim() + " " + row["descrip"].ToString();
            //        cant = Convert.ToDecimal(row["cant"]).ToString("###0.000");
            //        cant = cant.Replace(",", "").Replace(".", "");
            //        cant = cant.PadLeft(8, '0');
            //        precio = Convert.ToDecimal(row["precio"]).ToString("#####0.00");
            //        precio = precio.Replace(",", "").Replace(".", "");
            //        precio = precio.PadLeft(10, '0');
            //        talla = row["talla"].ToString();
            //        color = row["color"].ToString();
            //        seriales = row["seriales"].ToString();
            //        notas = row["notas"].ToString();
            //        i = Convert.ToInt16(row["baseiva"]);

            //        cadena = tipotasa[i] + precio + cant + descrip;
            //        respuesta = SendCmd(ref status, ref error, cadena);

            //        if (!string.IsNullOrEmpty(talla))
            //        {
            //            cadena = "@ " + talla + " / " + color;
            //            respuesta = SendCmd(ref status, ref error, cadena);
            //        }

            //        if (!string.IsNullOrEmpty(seriales))
            //        {
            //            cadena = "@ S/N:" + seriales;
            //            respuesta = SendCmd(ref status, ref error, cadena);
            //        }
            //    }

            //    bool pagodirecto = true;
            //    decimal monto, topago = 0, tofact;
            //    string montopago;

            //    cadena = "101";

            //    if (dtPagos != null)
            //    {
            //        if (dtPagos.Rows.Count == 1)
            //        {
            //            if (dtPagos.Rows[0]["idpagofiscal"].ToString().Trim() != "")
            //            {
            //                cadena = "1" + dtPagos.Rows[0]["idpagofiscal"].ToString().Trim();
            //            }
            //        }
            //        else
            //        {
            //            foreach (DataRow row in dtPagos.Rows)
            //            {
            //                monto = Convert.ToDecimal(row["monto"]);

            //                if (monto > 0 && row["idpagofiscal"].ToString().Trim() != "")
            //                {
            //                    montopago = monto.ToString("#####0.00");
            //                    montopago = montopago.Replace(",", "").Replace(".", "");
            //                    montopago = montopago.PadLeft(12, '0');

            //                    cadena = "2" + row["idpagofiscal"].ToString().Trim() + montopago;
            //                    respuesta = SendCmd(ref status, ref error, cadena);

            //                    pagodirecto = false;
            //                    topago += monto;
            //                }
            //            }

            //            if (topago > 0)
            //            {
            //                cadena = LeerStatusS2(true, 51, 13);

            //                tofact = (cadena != "" ? (Convert.ToDecimal(cadena) / 100) : totaldoc);

            //                if (topago < tofact)
            //                {
            //                    monto = (tofact - topago);
            //                    montopago = monto.ToString("#####0.00");
            //                    montopago = montopago.Replace(",", "").Replace(".", "");
            //                    montopago = montopago.PadLeft(12, '0');

            //                    cadena = "201" + montopago;
            //                    respuesta = SendCmd(ref status, ref error, cadena);
            //                }
            //            }
            //        }
            //    }

            //    if (pagodirecto)
            //    {
            //        respuesta = SendCmd(ref status, ref error, cadena);
            //    }

            //    ok = evalua_errores(respuesta);

            //    CloseFpctrl();
            //}

            return bResp;
        }
        public void FacturaSinPersonalizar()
        {
            /*Factura sin Personalizar*/
            bResp = oFiscal.SendCmd("@Comentario");
            bResp = oFiscal.SendCmd(" 000000010000001000TaxFreeExento");
            bResp = oFiscal.SendCmd("!000000010000001000TaxRate1General");
            bResp = oFiscal.SendCmd("\"000000010000001000TaxRate2Reducida");
            bResp = oFiscal.SendCmd("#000000010000001000TaxRate3Adicional");
            bResp = oFiscal.SendCmd("3");
            bResp = oFiscal.SendCmd("101");
        }
        public void FacturaPersonalizada()
        {
            /*Factura Personalizada*/
            bResp = oFiscal.SendCmd("iF*FAV0000012345");
            bResp = oFiscal.SendCmd("iR*V11365852");
            bResp = oFiscal.SendCmd("iS*Ian A. Graterol");
            bResp = oFiscal.SendCmd("i00Dir.:Ppal de Siempre Viva");
            bResp = oFiscal.SendCmd("i01Tel.:+58(212)555-55-55");
            bResp = oFiscal.SendCmd("i02Usuario:ventas@cajero.local");
            bResp = oFiscal.SendCmd(" 000000010000001000TaxFreeExento");
            bResp = oFiscal.SendCmd("!000000010000001000TaxRate1General");
            bResp = oFiscal.SendCmd("\"000000010000001000TaxRate2Reducida");
            bResp = oFiscal.SendCmd("#000000010000001000TaxRate3Adicional");
            bResp = oFiscal.SendCmd("201000000000442");
            //bResp = oFiscal.SendCmd("3");
            //bResp = oFiscal.SendCmd("101");
        }
        public void GetReport()
        {
            try
            {
                oFiscal.ReadFpStatus(); 

                oReport = oFiscal.GetXReport();
                TxtInformation = "";
                TxtInformation += "Ultimo Reporte Z: " + oReport.NumberOfLastZReport + "\r\n";
                TxtInformation += "Fecha del Ultimo Reporte Z: " + oReport.ZReportDate + "\r\n";
                TxtInformation += "Venta Sin Impuesto: " + oReport.FreeSalesTax + "\r\n";
                TxtInformation += "Venta con IVA 16% BI: " + oReport.GeneralRate1Sale + "," + " IVA: " + oReport.GeneralRate1Tax + "\r\n";
                TxtInformation += "Venta con IVA 08% BI: " + oReport.ReducedRate2Sale + "," + " IVA: " + oReport.ReducedRate2Tax + "\r\n";
                TxtInformation += "Venta con IVA 22% BI: " + oReport.AdditionalRate3Sale + "," + " IVA: " + oReport.AdditionalRate3Tax + "\r\n";
                TxtInformation += "Total Ventas BI: " + suma(oReport.FreeSalesTax, oReport.GeneralRate1Sale, oReport.ReducedRate2Sale, oReport.AdditionalRate3Sale) + "\r\n";
                TxtInformation += "Total Devoluciones: " + suma(oReport.AdditionalRateDevolution, oReport.FreeTaxDevolution, oReport.GeneralRateDevolution, oReport.ReducedRateDevolution) + "\r\n";
                TxtInformation += "Total Debitos: " + suma(oReport.AdditionalRateDebit, oReport.FreeTaxDebit, oReport.GeneralRateDebit, oReport.ReducedRateDebit) + "\r\n";
                TxtInformation += "Nro Ultima Factura: " + oReport.NumberOfLastInvoice + "\r\n";
                TxtInformation += "Fecha Ultima Factura: " + oReport.LastInvoiceDate + "\r\n";
                TxtInformation += "Nro Ultima Nota de Credito: " + oReport.NumberOfLastCreditNote + "\r\n";
                TxtInformation += "Nro Ultima Nota de Debito: " + oReport.NumberOfLastDebitNote + "\r\n";
                TxtInformation += "Nro Ultimo Documento NO Fiscal: " + oReport.NumberOfLastNonFiscal;

                //MessageBox.Show(TxtInformation);
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
            }
            

        }
        public void CargarS1()
        {
            try
            {
                S1PrinterData data = oFiscal.GetS1PrinterData();
                cNumeroFactura = data.LastInvoiceNumber.ToString("00000000");
                nMontoZ = data.TotalDailySales;
                nUltimoZ = data.DailyClosureCounter;
                cSerialPrinter = data.RegisteredMachineNumber;

                TxtInformation = "";
                TxtInformation += "Ultimo Reporte Z: " + data.LastInvoiceNumber.ToString("00000000") + "\r\n";
                TxtInformation += "Venta Sin Impuesto: " + data.TotalDailySales + "\r\n";
                TxtInformation += "Ultima Factura Impresa: " + data.DailyClosureCounter + "\r\n";
                TxtInformation += "Nro de Serial: " + data.RegisteredMachineNumber;
            }
            catch (TfhkaNet.IF.PrinterException)
            {
                MessageBox.Show(string.Format("{0}\r\nEstatus: {1}", oFiscal.Estado.ToUpper(), oFiscal.Status_Error.ToUpper()), "PrinterException");
            }
            catch (Exception x)
            {
                MessageBox.Show(string.Format("Error: {0}", x.Message.ToUpper()), "SystemException");
            }
        }
        double suma(double a, double b, double c, double d)
        {
            _suma = a + b + c + d;
            return _suma;
        }
    }
}
