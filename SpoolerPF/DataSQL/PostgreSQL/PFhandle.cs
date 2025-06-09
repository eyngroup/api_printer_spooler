using CookComputing.XmlRpc;
using SpoolerPF.DataConfig;
using SpoolerPF.Main;
using SpoolerPF.DataPrinter.Hka;
using System;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Xml.Linq;

namespace SpoolerPF.DataSQL.Pgsql
{
    public class PFhandle
    {
        public string Handleinfo;
        readonly PFpgsql oPgSQL = new PFpgsql();    
        readonly OdooQuerys qOdoo = new OdooQuerys();

        public DataTable GetInvoice(string cSerial, int nLimit)
        {
            DataTable oDataInvoice = new DataTable();
            try
            {
                string cQuery = qOdoo.AccountMove(cSerial, nLimit);
                oDataInvoice = oPgSQL.GetDataTable(cQuery);
                Handleinfo = cQuery;    
            }
            catch (Exception ex)
            {
                Handleinfo = ex.Message;
            }
            return oDataInvoice;
        }

        public DataTable SearchDataDoc(int nID)
        {
            string cQueryDoc = qOdoo.AccountMove(nID);
            Handleinfo = cQueryDoc;
            var oDataDoc = oPgSQL.GetDataTable(cQueryDoc);
            if (oDataDoc.Rows.Count == 0){return null;}
            return oDataDoc;
        }

        public DataTable SearchDataMov(int nID)
        {
            string cQueryMov = qOdoo.AccountMoveLine(nID);
            Handleinfo = cQueryMov;
            var oDataMov = oPgSQL.GetDataTable(cQueryMov);
            if (oDataMov.Rows.Count == 0) { return null; }
            return oDataMov;
        }

        public DataTable SearchDataPag(int nID)
        {
            string cQueryPag = qOdoo.PosOrder(nID);
            Handleinfo = cQueryPag;
            var oDataPag = oPgSQL.GetDataTable(cQueryPag);
            if (oDataPag.Rows.Count == 0) { return null; }
            return oDataPag;
        }

        public bool UpdateInvoice(string cInvoice, int nID)
        {
            string cQueryUp = qOdoo.UpdateAccountMove(cInvoice, nID);
            Handleinfo = cQueryUp;
            bool lDataUp = oPgSQL.SqlUpdate(cQueryUp);

            return lDataUp; 
        }

    }
}
