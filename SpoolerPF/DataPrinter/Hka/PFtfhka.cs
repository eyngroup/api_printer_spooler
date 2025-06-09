using TfhkaNet.IF.VE;
using System;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Text;
using TfhkaNet.IF;
using System.Threading;
using System.Threading.Tasks;

namespace SpoolerPF.DataPrinter.Hka
{
    public class PFtfhka
    {
        private Tfhka oTfhka;
        private string cPort;
        private string cCmd;
        private bool bResp;
        private double nSuma;
        private ReportData oReport;
        private AcumuladosX oJackpots;
        private string IFErrorInfo;
        private string IFEstatusInfo;
        public bool ErrorValidity;
        public string cPFinfo;
        public int nS1LastInvoice;
        public int nS1LastCredit;
        public string cS1SerialPrinter;
        public string cS1Rif;
        public int IFErrorCodigo;
        public int IFEstatusCodigo;

        public PFtfhka()
        {
            oTfhka = new Tfhka();
            cPort = LoadSetting();
            PFopen();
        }
        ~PFtfhka()
        {
            oTfhka.CloseFpCtrl();
            oTfhka = null;
        }
        private string LoadSetting()
        {
            return SpoolerPF.DataConfig.PFconfig.cPortComm;
        }
        private bool PFopen()
        {
            try
            {
                bResp = oTfhka.OpenFpCtrl(cPort);
                if (PFcheck())
                {
                    cPFinfo += "\r\nConexion Establecida en: " + cPort;
                }
                else
                {
                    cPFinfo += "\r\nError de conexión!\r\nVerifique el puerto: ";
                    throw (new Exception(string.Format(cPFinfo + "'{0}' por favor...", cPort)));
                }
            }
            catch (Exception ex)
            {
                cPFinfo = ex.Message;
            }
            return bResp;
        }
        private void PFclose()
        {
            oTfhka.CloseFpCtrl();
        }
        private bool PFcheck()
        {
            bResp = oTfhka.CheckFPrinter();
            if (bResp)
            {
                //PFstatus();
                cPFinfo += "\r\nImpresora conectada.";
            }
            else
            {
                cPFinfo += "Error de conexión! Verifique el puerto " + cPort + " por favor...";
            }
            return (bResp);
        }
        public void PFsend(string cCmd)
        {
            cPFinfo = "";
            try
            {
                if (PFcheck())
                {
                    bResp = oTfhka.SendCmd(cCmd);
                    if (bResp)
                    {
                        PFstatus();
                        cPFinfo = string.Format("Ultimo Comando Enviado: {0}\r\nEstatus {1}", cCmd, oTfhka.Status_Error);
                    }
                    else
                    {
                        PFstatus();
                        throw (new Exception(string.Format("Problema para enviar el comando: {0}\r\n{1}", cCmd, cPFinfo)));
                    }
                }
                else
                {
                    throw (new Exception(string.Format("Error de conexión!\r\nVerifique el puerto '{0}' por favor...", cPort)));
                }
            }
            catch (Exception ex)
            {
                cPFinfo = ex.Message;
            }
        }
        /// <summary>
        /// Imprime el Reporte X [VOID PrintXReport() throws PrinterException]
        /// </summary>
        public void PFreportX()
        {
            PFsend("I0X");
            //oTfhka.PrintXReport();
        }
        /// <summary>
        /// Imprime el Reporte Diario Z [VOID PrintZReport() throws PrinterException]
        /// </summary>
        public void PFreportZ()
        {
            PFsend("I0Z");
            //oTfhka.PrintZReport();
        }
        /// <summary>
        /// Obtiene un reporte del Status y Error de la impresora en un objeto del tipo PrinterStatus que contiene el código y 
        /// una descripción tanto para el Status como para el Error actual.
        /// </summary>
        public void PFstatus()
        {
            var oPrinterStatus = oTfhka.GetPrinterStatus();

            ErrorValidity = oPrinterStatus.ErrorValidity;                      // Validez del Error.
            IFErrorCodigo = oPrinterStatus.PrinterErrorCode;                   // Valor entero del Error. Anexo2
            IFErrorInfo = oPrinterStatus.PrinterErrorDescription;              // Descripción del Error.
            IFEstatusCodigo = oPrinterStatus.PrinterStatusCode;                // Valor entero del Status. anexo 1
            IFEstatusInfo = oPrinterStatus.PrinterStatusDescription;           // Descripción del Status.

            //Anexo 2
            switch (IFErrorCodigo)
            {
                case 0: IFErrorInfo = "No hay error."; break;
                case 1: IFErrorInfo = "Fin en la entrega de papel."; break;
                case 2: IFErrorInfo = "Error de índole mecánico en la entrega de papel."; break;
                case 3: IFErrorInfo = "Fin en la entrega de papel y error mecánico."; break;
                case 80: IFErrorInfo = "Comando inválido o valor inválido."; break;
                case 84: IFErrorInfo = "Tasa inválida."; break;
                case 88: IFErrorInfo = "No hay asignadas directivas."; break;
                case 92: IFErrorInfo = "Comando inválido."; break;
                case 96: IFErrorInfo = "Error fiscal."; break;
                case 100: IFErrorInfo = "Error de la memoria fiscal."; break;
                case 108: IFErrorInfo = "Memoria fiscal llena."; break;
                case 112: IFErrorInfo = "Buffer completo. (debe enviar el comando de reinicio)"; break;
                case 128: IFErrorInfo = "Error en la comunicación."; break;
                case 137: IFErrorInfo = "No hay respuesta."; break;
                case 144: IFErrorInfo = "Error LRC."; break;
                case 145: IFErrorInfo = "Error interno api."; break;
                case 153: IFErrorInfo = "Error en la apertura del archivo."; break;
                default: IFErrorInfo = "Error No Registrado."; break;
            }

            //Anexo 1
            switch (IFEstatusCodigo)
            {
                case 0: IFEstatusInfo = "Estado desconocido."; break;
                case 1: IFEstatusInfo = "En modo prueba y en espera."; break;
                case 2: IFEstatusInfo = "En modo prueba y emisión de documentos fiscales."; break;
                case 3: IFEstatusInfo = "En modo prueba y emisión de documentos no fiscales."; break;
                case 4: IFEstatusInfo = "En modo fiscal y en espera."; break;
                case 5: IFEstatusInfo = "En modo fiscal y emisión de documentos fiscales."; break;
                case 6: IFEstatusInfo = "En modo fiscal y emisión de documentos no fiscales."; break;
                case 7: IFEstatusInfo = "En modo fiscal, cercana carga completa de la memoria fiscal y en espera."; break;
                case 8: IFEstatusInfo = "En modo fiscal, cercana carga completa de la memoria fiscal y en emisión de documentos fiscales."; break;
                case 9: IFEstatusInfo = "En modo fiscal, cercana carga completa de la memoria fiscal y en emisión de documentos no fiscales."; break;
                case 10: IFEstatusInfo = "En modo fiscal, carga completa de la memoria fiscal y en espera."; break;
                case 11: IFEstatusInfo = "En modo fiscal, carga completa de la memoria fiscal y en emisión de documentos fiscales."; break;
                case 12: IFEstatusInfo = "En modo fiscal, carga completa de la memoria fiscal y en emisión de documentos no fiscales."; break;
                default: IFEstatusInfo = "Estado No Registrado."; break;
            }

            cPFinfo = "";
            cPFinfo += "Falla: " + IFErrorInfo + " [ " + IFErrorCodigo + " ]\r\n";
            cPFinfo += "Modo Actual: " + IFEstatusInfo + " [ " + IFEstatusCodigo + " ]\r\n";
            //cPFinfo += "ErrorValidity: " + ErrorValidity;

            _ = oTfhka.UploadStatusCmd("S1", "Report/StatusS1.txt");
            _ = oTfhka.UploadStatusCmd("S2", "Report/StatusS2.txt");
            _ = oTfhka.UploadStatusCmd("S3", "Report/StatusS3.txt");
            _ = oTfhka.UploadStatusCmd("S4", "Report/StatusS4.txt");
            _ = oTfhka.UploadStatusCmd("S5", "Report/StatusS5.txt");
            _ = oTfhka.UploadStatusCmd("S8E", "Report/StatusS8E.txt");
            _ = oTfhka.UploadStatusCmd("S8P", "Report/StatusS8P.txt");

            try
            {
                //S1PrinterData oGetS1 = oTfhka.GetS1PrinterData();
                var oGetS1 = oTfhka.GetS1PrinterData();
                nS1LastInvoice = oGetS1.LastInvoiceNumber;
                nS1LastCredit = oGetS1.LastCreditNoteNumber;
                cS1SerialPrinter = oGetS1.RegisteredMachineNumber;
                cS1Rif = oGetS1.RIF;
            }
            catch (Exception ex)
            {

                PFcheck();
                cPFinfo += "\r\n" + ex.Message;
            }

        }
        /// <summary>
        /// Un objeto de tipo AcumuladosX 
        /// </summary>
        public void PFjackpots()
        {
            try
            {
                oJackpots = oTfhka.GetX4Report();
                cPFinfo = "";
                cPFinfo += "Acumulado exento: " + oJackpots.FreeTax.ToString() + "\r\n";
                cPFinfo += "Acumulado percibido: " + oJackpots.PerceivedTax.ToString() + "\r\n";
                cPFinfo += "Acumulado base imponible tasa 1: " + oJackpots.GeneralRate1.ToString() + "\r\n";
                cPFinfo += "Acumulado base imponible tasa 2: " + oJackpots.ReducedRate2.ToString() + "\r\n";
                cPFinfo += "Acumulado base imponible tasa 3: " + oJackpots.AdditionalRate3.ToString() + "\r\n";
                cPFinfo += "Acumulado base imponible igtf: " + oJackpots.IgtfRate.ToString() + "\r\n";
                cPFinfo += "Acumulado impuesto tasa 1: " + oJackpots.GeneralRate1Tax.ToString() + "\r\n";
                cPFinfo += "Acumulado impuesto tasa 2: " + oJackpots.ReducedRate2Tax.ToString() + "\r\n";
                cPFinfo += "Acumulado impuesto tasa 3: " + oJackpots.AdditionalRate3Tax.ToString() + "\r\n";
                cPFinfo += "Acumulado impuesto igtf: " + oJackpots.IgtfRateTax.ToString();

                //cPFinfo = "";
                //cPFinfo += "Acumulado exento: " + oJackpots.FreeTax + "\r\n";
                //cPFinfo += "Acumulado base imponible tasa 1: " + oJackpots.GeneralRate1 + "\r\n";
                //cPFinfo += "Acumulado base imponible tasa 2: " + oJackpots.ReducedRate2 + "\r\n";
                //cPFinfo += "Acumulado base imponible tasa 3: " + oJackpots.AdditionalRate3 + "\r\n";
                //cPFinfo += "Acumulado impuesto tasa 1: " + oJackpots.GeneralRate1Tax + "\r\n";
                //cPFinfo += "Acumulado impuesto tasa 2: " + oJackpots.ReducedRate2Tax + "\r\n";
                //cPFinfo += "Acumulado impuesto tasa 3: " + oJackpots.AdditionalRate3Tax + "\r\n";
            }
            catch (Exception ex)
            {
                cPFinfo = (ex.Message);
            }
        }
        /// <summary>
        /// Reporte X por medio del comando “U0X”. Un objeto de tipo ReportData 
        /// </summary>
        public void PFreport()
        {
            try
            {
                oReport = oTfhka.GetXReport();
                cPFinfo = "";
                cPFinfo += "Fecha de la última factura: " + oReport.LastInvoiceDate + "\r\n";
                cPFinfo += "Número de la última factura: " + oReport.NumberOfLastInvoice + "\r\n";
                cPFinfo += "Facturas exentas: " + oReport.FreeSalesTax + "\r\n";
                cPFinfo += "Facturas con tasa general BI: " + oReport.GeneralRate1Sale + ", IVA: " + oReport.GeneralRate1Tax + "\r\n";
                cPFinfo += "Facturas con tasa reducida BI: " + oReport.ReducedRate2Sale + ", IVA: " + oReport.ReducedRate2Tax + "\r\n";
                cPFinfo += "Facturas con tasa adicional BI: " + oReport.AdditionalRate3Sale + ", IVA: " + oReport.AdditionalRate3Tax + "\r\n";
                cPFinfo += "Total Facturas c/IVA: " + PFsuma(oReport.FreeSalesTax, oReport.GeneralRate1Sale, oReport.GeneralRate1Tax, oReport.ReducedRate2Sale, oReport.ReducedRate2Tax, oReport.AdditionalRate3Sale, oReport.AdditionalRate3Tax) + "\r\n";
                cPFinfo += "======================================= " + "\r\n";
                cPFinfo += "Número de la última nota de crédito: " + oReport.NumberOfLastCreditNote + "\r\n";
                cPFinfo += "Notas de crédito exentas: " + oReport.FreeTaxDevolution + "\r\n";
                cPFinfo += "Notas de crédito con tasa general BI: " + oReport.GeneralRateDevolution + ", IVA: " + oReport.GeneralRateTaxDevolution + "\r\n";
                cPFinfo += "Notas de crédito con tasa reducida BI: " + oReport.ReducedRateDevolution + ", IVA: " + oReport.ReducedRateTaxDevolution + "\r\n";
                cPFinfo += "Notas de crédito con tasa adicional BI: " + oReport.AdditionalRateDevolution + ", IVA: " + oReport.AdditionalRateTaxDevolution + "\r\n";
                cPFinfo += "Total Notas de Crédito c/IVA: " + PFsuma(oReport.FreeTaxDevolution, oReport.GeneralRateDevolution, oReport.GeneralRateTaxDevolution, oReport.ReducedRateDevolution, oReport.ReducedRateTaxDevolution, oReport.AdditionalRateDevolution, oReport.AdditionalRateTaxDevolution) + "\r\n";
                cPFinfo += "======================================= " + "\r\n";
                cPFinfo += "Número de la última nota de débito: " + oReport.NumberOfLastDebitNote + "\r\n";
                cPFinfo += "Notas de débito exentas: " + oReport.FreeTaxDebit + "\r\n";
                cPFinfo += "Notas de débito con tasa general BI: " + oReport.GeneralRateDebit + ", IVA: " + oReport.GeneralRateTaxDebit + "\r\n";
                cPFinfo += "Notas de débito con tasa reducida BI: " + oReport.ReducedRateDebit + ", IVA: " + oReport.ReducedRateTaxDebit + "\r\n";
                cPFinfo += "Notas de débito con tasa adicional BI: " + oReport.AdditionalRateDebit + ", IVA: " + oReport.AdditionalRateTaxDebit + "\r\n";
                cPFinfo += "Total Notas de Débito c/IVA: " + PFsuma(oReport.FreeTaxDebit, oReport.GeneralRateDebit, oReport.GeneralRateTaxDebit, oReport.ReducedRateDebit, oReport.ReducedRateTaxDebit, oReport.AdditionalRateDebit, oReport.AdditionalRateTaxDebit) + "\r\n";
                cPFinfo += "======================================= " + "\r\n";
                cPFinfo += "IGTF en facturas BI: " + oReport.IgtfRateSales + ", IVA: " + oReport.IgtfRateTaxSales + "\r\n";
                cPFinfo += "IGTF en notas de crédito BI: " + oReport.IgtfRateDevolution + ", IVA: " + oReport.IgtfRateTaxDevolution + "\r\n";
                cPFinfo += "IGTF en notas de débito BI: " + oReport.IgtfRateDebit + ", IVA: " + oReport.IgtfRateTaxDebit + "\r\n";
                cPFinfo += "Total IGTF c/IVA: " + PFsuma(0, oReport.IgtfRateSales, oReport.IgtfRateTaxSales, oReport.IgtfRateDevolution, oReport.IgtfRateTaxDevolution, oReport.IgtfRateDebit, oReport.IgtfRateTaxDebit) + "\r\n";
                cPFinfo += "======================================= " + "\r\n";
                cPFinfo += "Fecha del último Reporte Z: " + oReport.ZReportDate + "\r\n";
                cPFinfo += "Número del último Reporte Z: " + oReport.NumberOfLastZReport + "\r\n";
                cPFinfo += "Número del último documento no fiscal: " + oReport.NumberOfLastNonFiscal + "\r\n";

                //Original
                //cPFinfo += "BI tasa adicional en facturas: " + oReport.AdditionalRate3Sale + "\r\n";
                //cPFinfo += "IVA tasa adicional en facturas: " + oReport.AdditionalRate3Tax + "\r\n";
                //cPFinfo += "BI tasa adicional en nota débito: " + oReport.AdditionalRateDebit + "\r\n";
                //cPFinfo += "BI tasa adicional en nota de crédito: " + oReport.AdditionalRateDevolution + "\r\n";
                //cPFinfo += "IVA Tasa Adicional en Nota Débito: " + oReport.AdditionalRateTaxDebit + "\r\n";
                //cPFinfo += "IVA tasa adicional en nota de crédito: " + oReport.AdditionalRateTaxDevolution + "\r\n";
                //cPFinfo += "Monto tasa en facturas: " + oReport.FreeSalesTax + "\r\n";
                //cPFinfo += "Monto tasa en nota de débito: " + oReport.FreeTaxDebit + "\r\n";
                //cPFinfo += "monto tasa en nota de crédito: " + oReport.FreeTaxDevolution + "\r\n";
                //cPFinfo += "BI tasa general en facturas: " + oReport.GeneralRate1Sale + "\r\n";
                //cPFinfo += "IVA tasa general en facturas: " + oReport.GeneralRate1Tax + "\r\n";
                //cPFinfo += "BI tasa general en nota débito: " + oReport.GeneralRateDebit + "\r\n";
                //cPFinfo += "BI tasa general en nota de crédito: " + oReport.GeneralRateDevolution + "\r\n";
                //cPFinfo += "IVA tasa general en nota de débito: " + oReport.GeneralRateTaxDebit + "\r\n";
                //cPFinfo += "IVA tasa general en nota de crédito: " + oReport.GeneralRateTaxDevolution + "\r\n";
                //cPFinfo += "Fecha de la última factura: " + oReport.LastInvoiceDate + "\r\n";
                //cPFinfo += "Número de la última nota de crédito: " + oReport.NumberOfLastCreditNote + "\r\n";
                //cPFinfo += "Número de la última nota de débito: " + oReport.NumberOfLastDebitNote + "\r\n";
                //cPFinfo += "Número de la última factura: " + oReport.NumberOfLastInvoice + "\r\n";
                //cPFinfo += "Número del último documento no fiscal: " + oReport.NumberOfLastNonFiscal + "\r\n";
                //cPFinfo += "Número del último Reporte Z: " + oReport.NumberOfLastZReport + "\r\n";
                //cPFinfo += "BI tasa reducida en facturas: " + oReport.ReducedRate2Sale + "\r\n";
                //cPFinfo += "IVA tasa adicional en facturas: " + oReport.ReducedRate2Tax + "\r\n";
                //cPFinfo += "BI tasa adicional en nota débito: " + oReport.ReducedRateDebit + "\r\n";
                //cPFinfo += "BI tasa adicional en nota de crédito: " + oReport.ReducedRateDevolution + "\r\n";
                //cPFinfo += "IVA Tasa Adicional en Nota Débito: " + oReport.ReducedRateTaxDebit + "\r\n";
                //cPFinfo += "IVA tasa adicional en nota de crédito: " + oReport.ReducedRateTaxDevolution + "\r\n";
                //cPFinfo += "Fecha del último Reporte Z: " + oReport.ZReportDate + "\r\n";
                //cPFinfo += "BI tasa igtf en facturas: " + oReport.IgtfRateSales + "\r\n";
                //cPFinfo += "IVA tasa igtf en facturas: " + oReport.IgtfRateTaxSales + "\r\n";
                //cPFinfo += "BI tasa igtf en nota débito: " + oReport.IgtfRateDebit + "\r\n";
                //cPFinfo += "IVA Tasa igtf en Nota Débito: " + oReport.IgtfRateTaxDebit + "\r\n";
                //cPFinfo += "BI tasa igtf en Nota de crédito: " + oReport.IgtfRateDevolution + "\r\n";
                //cPFinfo += "IVA Tasa igtf en Nota credito: " + oReport.IgtfRateTaxDevolution;

            }
            catch (Exception ex)
            {
                cPFinfo = (ex.Message);
            }
        }
        /// <summary>
        /// S1 (información de parámetros generales de la impresora). Un objeto de tipo S1PrinterData
        /// </summary>
        public void PFdataS1()
        {
            cPFinfo = "";
            if (PFcheck())
            {
                try
                {
                    S1PrinterData s1Printer = oTfhka.GetS1PrinterData();
                    cPFinfo = "";
                    cPFinfo += "Contador de reporte de auditoría: " + s1Printer.AuditReportsCounter + "\r\n";
                    cPFinfo += "Número de cajero activo: " + s1Printer.CashierNumber + "\r\n";
                    cPFinfo += "Fecha y hora actual de la impresora fiscal: " + s1Printer.CurrentPrinterDateTime + "\r\n";
                    cPFinfo += "Contador de cierre diario (Reporte Z): " + s1Printer.DailyClosureCounter + "\r\n";
                    cPFinfo += "Número de la última nota de crédito: " + s1Printer.LastCreditNoteNumber + "\r\n";
                    cPFinfo += "Número de la última nota de débito: " + s1Printer.LastDebitNoteNumber + "\r\n";
                    cPFinfo += "Número de la última factura: " + s1Printer.LastInvoiceNumber + "\r\n";
                    cPFinfo += "Número del último documento no fiscal: " + s1Printer.LastNonFiscalDocNumber + "\r\n";
                    cPFinfo += "Cantidad de documentos no fiscales: " + s1Printer.QuantityNonFiscalDocuments + "\r\n";
                    cPFinfo += "Cantidad de notas de crédito en el día: " + s1Printer.QuantityOfCreditNotesToday + "\r\n";
                    cPFinfo += "Cantidad de notas débito en el día: " + s1Printer.QuantityOfDebitNotesToday + "\r\n";
                    cPFinfo += "Cantidad de facturas en el día: " + s1Printer.QuantityOfInvoicesToday + "\r\n";
                    cPFinfo += "Número de registro de la impresora fiscal: " + s1Printer.RegisteredMachineNumber + "\r\n";
                    cPFinfo += "RIF de fiscalización de la impresora: " + s1Printer.RIF + "\r\n";
                    cPFinfo += "Monto total de ventas diarias: " + Convert.ToDecimal(s1Printer.TotalDailySales).ToString("###0.00");
                }
                catch (Exception ex)
                {
                    cPFinfo = (ex.Message);
                }
            }
        }
        /// <summary>
        /// S3 (información de configuración de tasas y flags). Un objeto de tipo S3PrinterData
        /// </summary>
        public void PFdataS3()
        {
            cPFinfo = "";
            if (PFcheck())
            {
                try
                {
                    S3PrinterData s3Printer = oTfhka.GetS3PrinterData();
                    cPFinfo = "";
                    cPFinfo += "Valor de la tasa 1 (%): " + Convert.ToDecimal(s3Printer.Tax1).ToString("###0.00") + "\r\n";
                    cPFinfo += "Valor de la tasa 2 (%): " + Convert.ToDecimal(s3Printer.Tax2).ToString("###0.00") + "\r\n";
                    cPFinfo += "Valor de la tasa 3 (%): " + Convert.ToDecimal(s3Printer.Tax3).ToString("###0.00") + "\r\n";
                    cPFinfo += "Valor igtf (3%): " + Convert.ToDecimal(s3Printer.TaxIGTF).ToString("###0.00") + "\r\n";
                    cPFinfo += "Tipo de tasa 1 (Modo Incluido = 1, Modo Excluido = 2): " + s3Printer.TypeTax1 + "\r\n";
                    cPFinfo += "Tipo de tasa 2 (Modo Incluido = 1, Modo Excluido = 2): " + s3Printer.TypeTax2 + "\r\n";
                    cPFinfo += "Tipo de tasa 3 (Modo Incluido = 1, Modo Excluido = 2): " + s3Printer.TypeTax3 + "\r\n";
                    cPFinfo += "Tipo de igtf (Modo Incluido = 1, Modo Excluido = 2): " + s3Printer.TypeTaxIGTF + "\r\n";
                    for (int i = 0; i < s3Printer.AllSystemFlags.Length; i++)
                    {
                        cPFinfo += "\r\nFlag Nro: " + i.ToString("##00") + " | Valor: " + s3Printer.AllSystemFlags[i].ToString();
                    }
                }
                catch (Exception ex)
                {
                    cPFinfo = (ex.Message);
                }
            }
        }
        /// <summary>
        /// S5 (información sobre la memoria de auditoria). Un objeto de tipo S5PrinterData
        /// </summary>
        public void PFdataS5()
        {
            cPFinfo = "";
            if (PFcheck())
            {
                try
                {
                    S5PrinterData s5Printer = oTfhka.GetS5PrinterData();
                    cPFinfo = "";
                    cPFinfo += "Disponibilidad en memoria de auditoria (MB): " + s5Printer.AuditMemoryFreeCapacity + "\r\n";
                    cPFinfo += "Número de memoria de auditoria: " + s5Printer.AuditMemoryNumber + "\r\n";
                    cPFinfo += "Capacidad total de la memoria de auditoria (MB): " + s5Printer.AuditMemoryTotalCapacity + "\r\n";
                    cPFinfo += "Cantidad Documentos en la memoria de auditoria: " + s5Printer.NumberRegisteredDocuments + "\r\n";
                    cPFinfo += "Número de registro de la impresora fiscal: " + s5Printer.RegisteredMachineNumber + "\r\n";
                    cPFinfo += "RIF de fiscalización de la impresora: " + s5Printer.RIF;

                }
                catch (Exception ex)
                {
                    cPFinfo = (ex.Message);
                }
            }
        }
        private double PFsuma(double a1, double a2, double a3, double a4, double a5, double a6, double a7)
        {
            nSuma = a1 + a2 + a3 + a4 + a5 + a6 + a7;
            return nSuma;
        }

        public void PrintInvoice(DataTable tDatosEncabezado, DataTable tDatosContenido, DataTable tDatosPagos)
        {
            //PFstatus();

            if (PFcheck())
            {
                cPFinfo = "Conexion";

                #region <Encabezado>
                Thread.Sleep(1000);
                string cDocReferencia, dDocFecha, cCliNombre, cRifNumero, cDireccion, cTelefono, cCondicion = "CONTADO", cCajero;
                foreach (DataRow row in tDatosEncabezado.Rows)
                {
                    // DataTable
                    cDocReferencia = Convert.ToString(row["Doc_Numero"]);
                    cRifNumero = Convert.ToString(row["Cli_Rif"]);
                    cCliNombre = Convert.ToString(row["Cli_Nombre"]);
                    cDireccion = Convert.ToString(row["Cli_Direccion"]);
                    cTelefono = Convert.ToString(row["Cli_Telefono"]);
                    cCajero = Convert.ToString(row["User_Login"]);
                    DateTime dFecha = Convert.ToDateTime(row["Doc_Fecha"]);

                    // Format
                    cDocReferencia = cDocReferencia.Replace("/", "").Replace(".", "");
                    cDocReferencia = cDocReferencia.Substring(0, (cDocReferencia.Length < 15 ? cDocReferencia.Length : 15)).Trim(); //Max 15
                    cRifNumero = cRifNumero.Substring(0, (cRifNumero.Length < 12 ? cRifNumero.Length : 12)).Trim(); //Max 32
                    cCliNombre = cCliNombre.Substring(0, (cCliNombre.Length < 28 ? cCliNombre.Length : 28)).Trim(); //Max 28
                    cDireccion = cDireccion.Replace(", Monagas,", "").Replace("Venezuela", "");
                    cDireccion = cDireccion.Substring(0, (cDireccion.Length < 35 ? cDireccion.Length : 35)).Trim(); //Max 42 - 5
                    cTelefono = cTelefono.Replace("+58", "");
                    cTelefono = cTelefono.Substring(0, (cTelefono.Length < 34 ? cTelefono.Length : 34)).Trim(); //Max 42 - 5
                    cCondicion = cCondicion.Substring(0, (cCondicion.Length < 34 ? cCondicion.Length : 34)).Trim(); //Max 42 - 6
                    cCajero = cCajero.ToLower().Trim(); //Max 42 - 8 
                    dDocFecha = dFecha.ToString("dd-MM-yyyy");

                    // Command
                    cCmd = "iR*" + cRifNumero; _ = oTfhka.SendCmd(cCmd);
                    cCmd = "iS*" + cCliNombre; _ = oTfhka.SendCmd(cCmd);
                    cCmd = "i00Dir.:" + cDireccion; _ = oTfhka.SendCmd(cCmd);
                    cCmd = "i01Ref.:" + cDocReferencia; _ = oTfhka.SendCmd(cCmd);
                    //cCmd = "i01Tel.:" + cTelefono; oTfhka.SendCmd(cCmd);
                    //cCmd = "i02Venta:" + cCondicion; oTfhka.SendCmd(cCmd);
                    //cCmd = "i03Usuario:" + cCajero; oTfhka.SendCmd(cCmd);
                    //cCmd = "@Comentario:"; //Max 40

                }
                #endregion

                #region <Contenido>
                Thread.Sleep(1000);
                string cIVA, cPrecio, cCantidad, cProducto;
                foreach (DataRow row in tDatosContenido.Rows)
                {
                    // DataTable
                    cIVA = (row["Iva_Codigo"]).ToString();
                    if (cIVA.Equals("")) { cIVA = Convert.ToInt16(1).ToString(); }
                    else { cIVA = Convert.ToInt16(cIVA).ToString(); }
                    cPrecio = Convert.ToDecimal(row["Mov_PrecioU"]).ToString("###0.00");
                    cCantidad = Convert.ToDecimal(row["Mov_Cantidad"]).ToString("###0.000");
                    cProducto = Convert.ToString(row["Mov_Producto"]);

                    // Format
                    cPrecio = cPrecio.Replace(",", "").Replace(".", "");
                    cPrecio = cPrecio.PadLeft(10, '0');
                    cCantidad = cCantidad.Replace(",", "").Replace(".", "");
                    cCantidad = cCantidad.PadLeft(8, '0');
                    //cProducto = cProducto.Replace("[", "").Replace("]", "");
                    cProducto = cProducto.Substring(0, (cProducto.Length < 40 ? cProducto.Length : 40)).Trim(); //Max 66
                    switch (cIVA)
                    {
                        case "1": cIVA = " "; break;
                        case "2": cIVA = "!"; break;
                        case "3": cIVA = "\""; break;
                        case "4": cIVA = "#"; break;
                        default : cIVA = " "; break;
                    }

                    // Comando
                    cCmd = cIVA + cPrecio + cCantidad + cProducto;
                    oTfhka.SendCmd(cCmd);
                }
                #endregion

                #region <Pagos>
                Thread.Sleep(1000);
                //esta opcion funciono perfecto
                //cCmd = "3";
                //oTfhka.SendCmd(cCmd); // subtotal
                string cPagoID, cPagoMonto;
                foreach (DataRow row in tDatosPagos.Rows)
                {
                    // DataTable
                    cPagoID = Convert.ToInt16(row["Pag_ID"]).ToString();
                    cPagoMonto = Convert.ToDecimal(row["Pag_Monto"]).ToString("###0.00");

                    // Format
                    cPagoMonto = cPagoMonto.Replace(",", "").Replace(".", "");
                    cPagoMonto = cPagoMonto.PadLeft(12, '0');

                    switch (cPagoID)
                    {
                        case "1" : cPagoID = "201"; break; //Efectivo
                        case "2" : cPagoID = "201"; break; //Efectivo
                        case "11": cPagoID = "201"; break; //Efectivo
                        case "12": cPagoID = "213"; break; //Tarjeta
                        case "13": cPagoID = "220"; break; //Divisas
                        case "14": cPagoID = "201"; break; //Efectivo
                        case "15": cPagoID = "201"; break; //Efectivo
                        case "16": cPagoID = "201"; break; //Efectivo
                        case "17": cPagoID = "201"; break; //Efectivo
                        case "18": cPagoID = "201"; break; //Efectivo
                        default  : cPagoID = "102"; break; //Efectivo
                    }

                    // Command
                    if (cPagoID == "220")
                    {
                        cCmd = "122";
                        oTfhka.SendCmd(cCmd);
                    }
                    else
                    {
                        cCmd = cPagoID + cPagoMonto;
                        oTfhka.SendCmd(cCmd);
                    }
                }
                #endregion

                #region <CerrarDocumento>
                // cerrar factura
                cCmd = "199";
                //cCmd = "101";
                oTfhka.SendCmd(cCmd);
                #endregion
            }
        }

        public void PrintCredit(DataTable tDatosEncabezado, DataTable tDatosContenido, DataTable tDatosPagos)
        {
            //PFstatus();

            if (PFcheck())
            {
                cPFinfo = "Conexion";

                #region <Encabezado>
                Thread.Sleep(1000);
                string cDocReferencia, dDocFecha, cCliNombre, cRifNumero, cDireccion, cTelefono, cCondicion = "CONTADO", cCajero;
                foreach (DataRow row in tDatosEncabezado.Rows)
                {
                    // DataTable
                    cDocReferencia = Convert.ToString(row["Doc_Numero"]);
                    cRifNumero = Convert.ToString(row["Cli_Rif"]);
                    cCliNombre = Convert.ToString(row["Cli_Nombre"]);
                    cDireccion = Convert.ToString(row["Cli_Direccion"]);
                    cTelefono = Convert.ToString(row["Cli_Telefono"]);
                    cCajero = Convert.ToString(row["User_Login"]);
                    DateTime dFecha = Convert.ToDateTime(row["Doc_Fecha"]);

                    // Format
                    cDocReferencia = cDocReferencia.Replace("/", "").Replace(".", "");
                    cDocReferencia = cDocReferencia.Substring(0, (cDocReferencia.Length < 15 ? cDocReferencia.Length : 15)).Trim(); //Max 15
                    cRifNumero = cRifNumero.Substring(0, (cRifNumero.Length < 12 ? cRifNumero.Length : 12)).Trim(); //Max 32
                    cCliNombre = cCliNombre.Substring(0, (cCliNombre.Length < 28 ? cCliNombre.Length : 28)).Trim(); //Max 28
                    cDireccion = cDireccion.Replace(", Monagas,", "").Replace("Venezuela", "");
                    cDireccion = cDireccion.Substring(0, (cDireccion.Length < 35 ? cDireccion.Length : 35)).Trim(); //Max 42 - 5
                    cTelefono = cTelefono.Replace("+58", "");
                    cTelefono = cTelefono.Substring(0, (cTelefono.Length < 34 ? cTelefono.Length : 34)).Trim(); //Max 42 - 5
                    cCondicion = cCondicion.Substring(0, (cCondicion.Length < 34 ? cCondicion.Length : 34)).Trim(); //Max 42 - 6
                    cCajero = cCajero.ToLower().Trim(); //Max 42 - 8 
                    dDocFecha = dFecha.ToString("dd-MM-yyyy");

                    // Command
                    cCmd = "iR*" + cRifNumero; oTfhka.SendCmd(cCmd);
                    cCmd = "iS*" + cCliNombre; oTfhka.SendCmd(cCmd);
                    cCmd = "iF*00002482"; oTfhka.SendCmd(cCmd);
                    cCmd = "iI*Z7C7007929"; oTfhka.SendCmd(cCmd);
                    //cCmd = "i00Dir.:" + cDireccion; oTfhka.SendCmd(cCmd);
                    //cCmd = "i01Ref.:" + cDocReferencia; oTfhka.SendCmd(cCmd);

                }
                #endregion

                #region <Contenido>
                Thread.Sleep(1000);
                string cIVA, cPrecio, cCantidad, cProducto;
                foreach (DataRow row in tDatosContenido.Rows)
                {
                    // DataTable
                    cIVA = (row["Iva_Codigo"]).ToString();
                    if (cIVA.Equals("")) { cIVA = Convert.ToInt16(1).ToString(); }
                    else { cIVA = Convert.ToInt16(cIVA).ToString(); }
                    cPrecio = Convert.ToDecimal(row["Mov_PrecioU"]).ToString("###0.00");
                    cCantidad = Convert.ToDecimal(row["Mov_Cantidad"]).ToString("###0.000");
                    cProducto = Convert.ToString(row["Mov_Producto"]);

                    // Format
                    cPrecio = cPrecio.Replace(",", "").Replace(".", "");
                    cPrecio = cPrecio.PadLeft(10, '0');
                    cCantidad = cCantidad.Replace(",", "").Replace(".", "");
                    cCantidad = cCantidad.PadLeft(8, '0');
                    //cProducto = cProducto.Replace("[", "").Replace("]", "");
                    cProducto = cProducto.Substring(0, (cProducto.Length < 40 ? cProducto.Length : 40)).Trim(); //Max 66
                    switch (cIVA)
                    {
                        case "1": cIVA = "d0"; break;
                        case "2": cIVA = "d1"; break;
                        case "3": cIVA = "d2"; break;
                        case "4": cIVA = "d3"; break;
                        default: cIVA = "d0"; break;
                    }

                    // Comando
                    cCmd = cIVA + cPrecio + cCantidad + cProducto;
                    oTfhka.SendCmd(cCmd);
                }
                #endregion

                #region <Pagos>
                Thread.Sleep(1000);
                string cPagoID, cPagoMonto;
                foreach (DataRow row in tDatosPagos.Rows)
                {
                    // DataTable
                    cPagoID = Convert.ToInt16(row["Pag_ID"]).ToString();
                    cPagoMonto = Convert.ToDecimal(row["Pag_Monto"]).ToString("###0.00");

                    // Format
                    cPagoMonto = cPagoMonto.Replace(",", "").Replace(".", "");
                    cPagoMonto = cPagoMonto.PadLeft(12, '0');

                    switch (cPagoID)
                    {
                        case "1": cPagoID = "201"; break; //Efectivo
                        case "2": cPagoID = "201"; break; //Efectivo
                        case "11": cPagoID = "201"; break; //Efectivo
                        case "12": cPagoID = "213"; break; //Tarjeta
                        case "13": cPagoID = "220"; break; //Divisas
                        case "14": cPagoID = "201"; break; //Efectivo
                        case "15": cPagoID = "201"; break; //Efectivo
                        case "16": cPagoID = "201"; break; //Efectivo
                        case "17": cPagoID = "201"; break; //Efectivo
                        case "18": cPagoID = "201"; break; //Efectivo
                        default: cPagoID = "102"; break; //Efectivo
                    }

                    // Command
                    if (cPagoID == "220")
                    {
                        cCmd = "122";
                        oTfhka.SendCmd(cCmd);
                    }
                    else
                    {
                        cCmd = cPagoID + cPagoMonto;
                        oTfhka.SendCmd(cCmd);
                    }
                }
                #endregion

                #region <CerrarDocumento>
                // cerrar factura
                cCmd = "199";
                oTfhka.SendCmd(cCmd);
                #endregion
            }
        }

        /// <summary>
        /// Para generar esta Factura se activaron los siguientes Flags.
        /// 21 00 Se mantiene la configuración estándar de los montos que maneja la impresora. (Ver.Tabla 21)
        /// 50 01 Se activa para realizar cálculo del IGTF aplicando pagos en moneda extranjera
        /// 30 01 Imprime el código de barra con el número asociado bajo él código
        /// 43 00 Se activa el codigo de barra EAN13
        /// 199 Comando que es de uso obligatorio para cerrar los documentos fiscales(Factura de venta,
        /// Nota de Crédito, Nota de Débito) cuando el flag 50 está en 01.
        /// </summary>
        /// <param name="cModel: 01, 02, 03, 04"></param>

        //public void Examples(string cModel)
        //{
        //    if (cModel == "00")
        //    {
        //        cPFinfo = ""; cCmd = "PH1" + "Encabezado 1"; _ = oTfhka.SendCmd(cCmd); // Encabezado 1 al 8
        //        cPFinfo += cCmd + "\r\n"; cCmd = "iR*" + "J-12345678-9"; _ = oTfhka.SendCmd(cCmd); // RIF/C.I.
        //        cPFinfo += cCmd + "\r\n"; cCmd = "iS*" + "The Factory HKA"; _ = oTfhka.SendCmd(cCmd); // Razón Social
        //        cPFinfo += cCmd + "\r\n"; cCmd = "i01" + "Línea Adicional 01"; _ = oTfhka.SendCmd(cCmd); // Líneas Adicionales 1 al 9
        //        // Doc. Fiscal y Número de Factura
        //        // Fecha del DF y de Hora del DF
        //        cPFinfo += cCmd + "\r\n"; cCmd = "@" + "Esto es un Comentario"; _ = oTfhka.SendCmd(cCmd); // Comentario en el cuerpo del Documento
        //        cPFinfo += cCmd + "\r\n"; cCmd = " " + "0000001000" + "00001000" + "Producto Exento"; _ = oTfhka.SendCmd(cCmd); // Tasa Exento
        //        cPFinfo += cCmd + "\r\n"; cCmd = "p-" + "1000"; _ = oTfhka.SendCmd(cCmd); // Descuento por Porcentaje
        //        cPFinfo += cCmd + "\r\n"; cCmd = "!" + "0000002000" + "00001000" + "Producto General"; _ = oTfhka.SendCmd(cCmd); // Tasa General
        //        cPFinfo += cCmd + "\r\n"; cCmd = "p+" + "1000"; _ = oTfhka.SendCmd(cCmd); // Recargo por Porcentaje
        //        cPFinfo += cCmd + "\r\n"; cCmd = "\"" + "0000003000" + "00001000" + "Producto Reducida"; _ = oTfhka.SendCmd(cCmd); // Tasa Reducida
        //        cPFinfo += cCmd + "\r\n"; cCmd = "q-" + "000001000"; _ = oTfhka.SendCmd(cCmd); // Descuento por Monto
        //        cPFinfo += cCmd + "\r\n"; cCmd = "#" + "0000004000" + "00001000" + "Producto Adicional"; _ = oTfhka.SendCmd(cCmd); // Tasa Adicional
        //        cPFinfo += cCmd + "\r\n"; cCmd = "q+" + "000001000"; _ = oTfhka.SendCmd(cCmd); // Recargo por Monto
        //        // CORRECCIÓN
        //        cPFinfo += cCmd + "\r\n"; cCmd = " " + "0000001000" + "00001000" + "Producto Exento"; _ = oTfhka.SendCmd(cCmd); // Tasa Exento Para Corrección
        //        cPFinfo += cCmd + "\r\n"; cCmd = "k"; _ = oTfhka.SendCmd(cCmd); // Corrección 
        //        //Cancela último ítem/descuento/recargo
        //        cPFinfo += cCmd + "\r\n"; cCmd = "#" + "0000004000" + "00001000" + "Producto Adicional"; _ = oTfhka.SendCmd(cCmd); // Tasa Adicional
        //        // ANULACIÓN    
        //        cPFinfo += cCmd + "\r\n"; cCmd = "£" + "0000004000" + "00001000" + "Producto Adicional"; _ = oTfhka.SendCmd(cCmd); // Anula producto Tasa (A)
        //        cPFinfo += cCmd + "\r\n"; cCmd = "$" + "0000005000" + "00001000" + "Producto Percibido"; _ = oTfhka.SendCmd(cCmd); // Tasa Percibido
        //        cPFinfo += cCmd + "\r\n"; cCmd = "Y" + "1234567890128"; _ = oTfhka.SendCmd(cCmd); // Código de barra para un producto
        //        cPFinfo += cCmd + "\r\n"; cCmd = "3"; _ = oTfhka.SendCmd(cCmd); // Subtotal
        //        //Tasas de Impuesto utilizadas en el cuerpo de la factura
        //        cPFinfo += cCmd + "\r\n"; cCmd = "201" + "000000002062"; _ = oTfhka.SendCmd(cCmd); // Pago Parcial (Efectivo 1)
        //        cPFinfo += cCmd + "\r\n"; cCmd = "211" + "000000005100"; _ = oTfhka.SendCmd(cCmd); // Pago Parcial (Cheque 5)
        //        cPFinfo += cCmd + "\r\n"; cCmd = "122"; _ = oTfhka.SendCmd(cCmd); // Pago Directo(Divisa 3)
        //        cPFinfo += cCmd + "\r\n"; cCmd = "199"; _ = oTfhka.SendCmd(cCmd); // Cierre de la Factura
        //        cPFinfo += cCmd + "\r\n"; cCmd = "i01"; _ = oTfhka.SendCmd(cCmd); // Líneas Adicionales 1 al 9
        //        cPFinfo += cCmd + "\r\n"; cCmd = "PH91" + "Encabezado 1"; _ = oTfhka.SendCmd(cCmd); // Pie de Ticket 91 al 98
        //        cPFinfo += cCmd + "\r\n"; cCmd = "y" + "1234567890128"; _ = oTfhka.SendCmd(cCmd); // Código de barra de Pie de Ticket
        //        cPFinfo += cCmd;
        //    }

        //    if (cModel == "01")
        //    {
        //        cPFinfo = ""; cCmd = "PH1" + "Encabezado 1"; _ = oTfhka.SendCmd(cCmd); // Encabezado 1 al 8
        //        cPFinfo += cCmd + "\r\n"; cCmd = "iR*" + "J-12345678-9"; _ = oTfhka.SendCmd(cCmd); // RIF/C.I.
        //        cPFinfo += cCmd + "\r\n"; cCmd = "iS*" + "The Factory HKA"; _ = oTfhka.SendCmd(cCmd); // Razón Social
        //        cPFinfo += cCmd + "\r\n"; cCmd = "i01" + "Línea Adicional 01"; _ = oTfhka.SendCmd(cCmd); // Líneas Adicionales 1 al 9
        //        cPFinfo += cCmd + "\r\n"; cCmd = "@" + "Esto es un Comentario"; _ = oTfhka.SendCmd(cCmd); // Comentario en el cuerpo del Documento
        //        cPFinfo += cCmd + "\r\n"; cCmd = " " + "0000001000" + "00001000" + "Producto Exento"; _ = oTfhka.SendCmd(cCmd); // Tasa Exento
        //        cPFinfo += cCmd + "\r\n"; cCmd = "p-" + "1000"; _ = oTfhka.SendCmd(cCmd); // Descuento por Porcentaje
        //        cPFinfo += cCmd + "\r\n"; cCmd = "!" + "0000002000" + "00001000" + "Producto General"; _ = oTfhka.SendCmd(cCmd); // Tasa General
        //        cPFinfo += cCmd + "\r\n"; cCmd = "p+" + "1000"; _ = oTfhka.SendCmd(cCmd); // Recargo por Porcentaje
        //        cPFinfo += cCmd + "\r\n"; cCmd = "\"" + "0000003000" + "00001000" + "Producto Reducida"; _ = oTfhka.SendCmd(cCmd); // Tasa Reducida
        //        cPFinfo += cCmd + "\r\n"; cCmd = "q-" + "000001000"; _ = oTfhka.SendCmd(cCmd); // Descuento por Monto
        //        cPFinfo += cCmd + "\r\n"; cCmd = "#" + "0000004000" + "00001000" + "Producto Adicional"; _ = oTfhka.SendCmd(cCmd); // Tasa Adicional
        //        cPFinfo += cCmd + "\r\n"; cCmd = "q+" + "000001000"; _ = oTfhka.SendCmd(cCmd); // Recargo por Monto
        //        cPFinfo += cCmd + "\r\n"; cCmd = " " + "0000001000" + "00001000" + "Producto Exento"; _ = oTfhka.SendCmd(cCmd); // Tasa Exento Para Corrección
        //        cPFinfo += cCmd + "\r\n"; cCmd = "k"; _ = oTfhka.SendCmd(cCmd); // Corrección 
        //        cPFinfo += cCmd + "\r\n"; cCmd = "#" + "0000004000" + "00001000" + "Producto Adicional"; _ = oTfhka.SendCmd(cCmd); // Tasa Adicional 
        //        cPFinfo += cCmd + "\r\n"; cCmd = "£" + "0000004000" + "00001000" + "Producto Adicional"; _ = oTfhka.SendCmd(cCmd); // Anula producto Tasa (A)
        //        cPFinfo += cCmd + "\r\n"; cCmd = "$" + "0000005000" + "00001000" + "Producto Percibido"; _ = oTfhka.SendCmd(cCmd); // Tasa Percibido
        //        cPFinfo += cCmd + "\r\n"; cCmd = "Y" + "1234567890128"; _ = oTfhka.SendCmd(cCmd); // Código de barra para un producto
        //        cPFinfo += cCmd + "\r\n"; cCmd = "3"; _ = oTfhka.SendCmd(cCmd); // Subtotal
        //        cPFinfo += cCmd + "\r\n"; cCmd = "201" + "000000002062"; _ = oTfhka.SendCmd(cCmd); // Pago Parcial (Efectivo 1)
        //        cPFinfo += cCmd + "\r\n"; cCmd = "211" + "000000005100"; _ = oTfhka.SendCmd(cCmd); // Pago Parcial (Cheque 5)
        //        cPFinfo += cCmd + "\r\n"; cCmd = "101"; _ = oTfhka.SendCmd(cCmd); // Cierre de la Factura
        //        cPFinfo += cCmd + "\r\n"; cCmd = "i01"; _ = oTfhka.SendCmd(cCmd); // Líneas Adicionales 1 al 9
        //        cPFinfo += cCmd + "\r\n"; cCmd = "PH91" + "Encabezado 1"; _ = oTfhka.SendCmd(cCmd); // Pie de Ticket 91 al 98
        //        cPFinfo += cCmd + "\r\n"; cCmd = "y" + "1234567890128"; _ = oTfhka.SendCmd(cCmd); // Código de barra de Pie de Ticket
        //        cPFinfo += cCmd;
        //    }

        //    if (cModel == "02")
        //    {
        //        /*Factura sin Personalizar*/
        //        bResp = oTfhka.SendCmd("@Comentario");
        //        bResp = oTfhka.SendCmd(" 000000010000001000TaxFreeExento");
        //        bResp = oTfhka.SendCmd("!000000010000001000TaxRate1General");
        //        bResp = oTfhka.SendCmd("\"000000010000001000TaxRate2Reducida");
        //        bResp = oTfhka.SendCmd("#000000010000001000TaxRate3Adicional");
        //        bResp = oTfhka.SendCmd("3");
        //        bResp = oTfhka.SendCmd("101");
        //    }

        //    if (cModel == "03")
        //    {
        //        /*Factura Personalizada*/
        //        bResp = oTfhka.SendCmd("iF*FAV0000012345");
        //        bResp = oTfhka.SendCmd("iR*V111236542");
        //        bResp = oTfhka.SendCmd("iS*Ian A. Graterol");
        //        bResp = oTfhka.SendCmd("i00Dir.:Ppal de Siempre Viva");
        //        bResp = oTfhka.SendCmd("i01Tel.:+58(212)555-55-55");
        //        bResp = oTfhka.SendCmd("i02Usuario:ventas@cajero.local");
        //        bResp = oTfhka.SendCmd(" 000000010000001000TaxFreeExento");
        //        bResp = oTfhka.SendCmd("!000000010000001000TaxRate1General");
        //        bResp = oTfhka.SendCmd("\"000000010000001000TaxRate2Reducida");
        //        bResp = oTfhka.SendCmd("#000000010000001000TaxRate3Adicional");
        //        bResp = oTfhka.SendCmd("201000000000442");
        //        //bResp = oTfhka.SendCmd("3");
        //        //bResp = oTfhka.SendCmd("101");
        //    }


        //}


        //private string[] splitDecimalSTR(decimal d)
        //{
        //    char[] delimiters = new char[] { '.', ',' };
        //    string[] price = d.ToString().Split(delimiters);

        //    string[] ret = new string[2];
        //    ret[0] = price[0];
        //    if (price.Length == 2)
        //        ret[1] = price[1];
        //    else
        //        ret[1] = "0";

        //    return ret;
        //}

        //private string gen_number_fm(int v, bool aling_left, uint digits)
        //{
        //    return gen_number_fm(v.ToString(), aling_left, digits);
        //}

        //private string gen_number_fm(string v, bool aling_left, uint digits)
        //{
        //    string result = "";
        //    if (aling_left)
        //    {
        //        result += v;
        //        for (int i = v.Length; i < digits; ++i)
        //            result += "0";
        //    }
        //    else
        //    {
        //        for (int i = 0; i < digits - v.Length; ++i)
        //            result += "0";
        //        result += v;
        //    }
        //    return result;
        //}




        ////Retorna el Numero de Factura generado. -1 en caso de error.
        //public int generate_invoice(FMInvoice invoice, bool show_barcode, string barcode = null)
        //{

        //    if (!reloadLastFiscalPrints())
        //    {
        //        return -1;
        //    }

        //    int linv = last_invoice;

        //    fm.SendCmd("7", 3, 4); //cancela la factura si quedo alguna pendiente, solo se intenta una vez.

        //    bool ready = fm.SendCmd("5" + String.Format("{0:00000}", invoice.vendor.id));

        //    if (!ready)
        //        return -1;

        //    ready = fm.SendCmd("i01Razon Social: " + SafeSubstring(invoice.customer_name, 0, 35)) &&
        //            fm.SendCmd("i02R.I.F./C.I.:  " + SafeSubstring(invoice.customer_vat, 0, 35)) &&
        //            fm.SendCmd("i03Direccion:    " + SafeSubstring(invoice.customer_address, 0, 35)) &&
        //            fm.SendCmd("i04Telefono:     " + SafeSubstring(invoice.customer_phone, 0, 35)) &&
        //            fm.SendCmd("i05Caja:         " + SafeSubstring(invoice.customer_sale, 0, 35)) &&
        //            fm.SendCmd("i06Vendedor:     " + SafeSubstring(invoice.customer_vendor, 0, 35));

        //    if (!ready)
        //    {
        //        fm.SendCmd("7", 3, 4); //cancela la factura
        //        fm.SendCmd("6");
        //        return -1;
        //    }

        //    bool ready_comment = true;
        //    for (int i = 0; i < invoice.items.Count && ready; ++i)
        //    {
        //        FMInvoiceItem item = invoice.items[i];
        //        string cmd = "";

        //        if (item.tax.type == FMTax.FMTaxType.FMTAX_EXCENT || item.tax.value < 0.01m)
        //        {
        //            cmd = TAX0;
        //        }
        //        else
        //        {
        //            switch (item.tax.id)
        //            {
        //                case 1:
        //                    cmd += TAX1;
        //                    break;
        //                case 2:
        //                    cmd += TAX2;
        //                    break;
        //                case 3:
        //                    cmd += TAX3;
        //                    break;
        //                default:
        //                    Program.PrintLog("Error catastrofico, el ID es Invaldo! Como es posible :S");
        //                    fm.SendCmd("7"); //cancela la factura
        //                    return -1;
        //            }
        //        }

        //        decimal real_price = Math.Round(item.price, 2);
        //        decimal real_discount = Math.Round(item.discount, 2);
        //        decimal real_count = Math.Round(item.count, 3);

        //        string[] price = splitDecimalSTR(real_price);
        //        string[] count = splitDecimalSTR(real_count);
        //        string[] discount = splitDecimalSTR(real_discount);
        //        cmd += gen_number_fm(price[0], false, 8) + gen_number_fm(price[1], true, 2) +
        //                gen_number_fm(count[0], false, 5) + gen_number_fm(count[1], true, 3) +
        //               SafeSubstring(item.name, 0, 25);
        //        //sprintf(&tmp[1], "%08s%02s%05s%03s%s", price_1.toStdString().c_str(), price_2.toStdString().c_str(), count_1.toStdString().c_str(), count_2.toStdString().c_str(), item.get_name().mid(0, 25).toStdString().c_str());

        //        ready = fm.SendCmd(cmd, 10);
        //        if (ready && ready_comment)
        //        {
        //            if (ready_comment && item.desc1 != null && item.desc1.Trim().Length > 0)
        //                ready_comment = fm.SendCmd("@" + SafeSubstring(item.desc1.Trim(), 0, 45));
        //            if (ready_comment && item.desc2 != null && item.desc2.Trim().Length > 0)
        //                ready_comment = fm.SendCmd("@" + SafeSubstring(item.desc2.Trim(), 0, 45));
        //            if (ready_comment && item.desc3 != null && item.desc3.Trim().Length > 0)
        //                ready_comment = fm.SendCmd("@" + SafeSubstring(item.desc3.Trim(), 0, 45));
        //            if (ready_comment && item.reference != null && item.reference.Trim().Length > 0)
        //                ready_comment = fm.SendCmd("@Ref.: " + SafeSubstring(item.reference.Trim(), 0, 39));
        //        }
        //    }

        //    if (!ready)
        //    {
        //        fm.SendCmd("7", 3, 4); //cancela la factura
        //        fm.SendCmd("6");
        //        return -1;
        //    }

        //    if (show_barcode)
        //    {
        //        ulong code = (ulong)last_invoice + 1;
        //        if (barcode != null && Convert.ToUInt64(barcode) > 0)
        //            code = Convert.ToUInt64(barcode);
        //        string cmd = "y" + gen_number_fm(code.ToString(), false, 12);
        //        //sprintf(tmp, "y%012lld", code);

        //        //No se verifica ya que algunas impresoras no soportan esta opcion.
        //        fm.SendCmd(cmd, 5, 4);
        //    }
        //    decimal pay_amount_acum = 0;
        //    for (int i = 0; i < invoice.payments.Count && ready; ++i)
        //    {

        //        if (pay_amount_acum >= invoice.total)
        //            break; //Esto evita que la maquina fiscal se cuelgue...

        //        FMPaymentInvoice pay = invoice.payments[i];
        //        string cmd = "2";
        //        decimal pay_amount = Math.Round(pay.amount, 2);
        //        pay_amount_acum += pay_amount;
        //        string[] pay_amount_str = splitDecimalSTR(pay_amount);
        //        cmd += gen_number_fm(pay.payment.id, false, 2) + gen_number_fm(pay_amount_str[0], false, 10) + gen_number_fm(pay_amount_str[1], true, 2);
        //        //sprintf(tmp, "2%02d%010s%02s", pay.get_payment().get_id(), amount_1.toStdString().c_str(), amount_2.toStdString().c_str());
        //        ready = ready && fm.SendCmd(cmd, 10);
        //    }

        //    if (!ready)
        //    {
        //        fm.SendCmd("7", 3, 4); //cancela la factura
        //        fm.SendCmd("6");
        //        return -1;
        //    }

        //    fm.SendCmd("6");

        //    if (reloadLastFiscalPrints())
        //    {
        //        if (linv < last_invoice)
        //        {
        //            return last_invoice;
        //        }
        //    }
        //    return ++linv;
        //}

    }
}
