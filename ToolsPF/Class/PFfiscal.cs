using System;
using System.Collections;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Xml.Linq;
using ToolsPF.Querys;


namespace ToolsPF.Class
{
    internal class PFfiscal
    {
        readonly PFtfhka oPrinter = new PFtfhka();
        readonly OdooQuerys oQuerys = new OdooQuerys();

        public void ComprobarImpresora()
        {
            oPrinter.CheckPrinter();

        }
        public void EnviarCommando(string cCmd)
        {
            oPrinter.SendCommand(cCmd);
        }
        public void EmitirX()
        {
            oPrinter.ReportX();
        }        
        public void EmitirZ()
        {
            oPrinter.ReportZ();
        }



        public string Reporte()
        {
            oPrinter.GetReport();
            //oPrinter.CargarS1();
            return oPrinter.TxtInformation;
        }

       
        
        public void TestFacturaA()
        {
            oPrinter.FacturaSinPersonalizar();
        }
        public void TestFacturaB()
        {
            oPrinter.FacturaPersonalizada();
        }
        public DataTable Factura(string cDocAsociado)
        {
            string cQueryDoc = oQuerys.AccountMove(cDocAsociado);
            var oDataDoc = PFUtils.GetDataTable(cQueryDoc);

            string cQueryMov = oQuerys.AccountMoveLine(cDocAsociado);
            var oDataMov = PFUtils.GetDataTable(cQueryMov);

            string cQueryPag = oQuerys.PosOrder(cDocAsociado);
            var oDataPag = PFUtils.GetDataTable(cQueryPag);

            oPrinter.GenerarFactura(oDataDoc, oDataMov, oDataPag);

            return oDataDoc;
        }

        public string[] Valores()
        {
            oPrinter.CargarS1();
            string NumFac = oPrinter.cNumeroFactura;
            string MontoZ = oPrinter.nMontoZ.ToString();
            string Ultimo = oPrinter.nUltimoZ.ToString();
            string Serial = oPrinter.cSerialPrinter;

            string[] aCargarS1 = new string[4] { NumFac, MontoZ, Ultimo, Serial };
            return aCargarS1;
        }
    
    
    }
}
