using SpoolerPF.DataConnect.Odoo;
using SpoolerPF.DataSQL.Pgsql;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Xml.Linq;
using System.Configuration;
using System.IO;
using System.Security.Policy;
using System.Security.Cryptography;

namespace SpoolerPF.Main
{
    public partial class WndDataCheck : Form
    {
        // Datos de conexión
        private string svrUrl = SpoolerPF.DataConfig.PFconfig.cOdooUrl;
        private string dbName = SpoolerPF.DataConfig.PFconfig.cOdooDb;
        private string dbUser = SpoolerPF.DataConfig.PFconfig.cOdooUser;
        private string dbPass = SpoolerPF.DataConfig.PFconfig.cOdooPass;
        private string companyID = SpoolerPF.DataConfig.PFconfig.cOdooCompany;

        private DataTable dt = new DataTable();

        public WndDataCheck()
        {
            InitializeComponent();
        }

        public void Procesar()
        {
            DateTime dateTime = DateTime.Now;
            //MessageBox.Show(svrUrl +" "+ dbName + " " + dbUser + " " + dbPass);
            OdooConnect odoo = new OdooConnect(svrUrl, dbName, dbUser, dbPass);
            odoo.Login();

            string models = "account.move";

            //MessageBox.Show("Usuario Logeado?: " + odoo.IsLoggedIn);
            if (odoo.IsLoggedIn)
            {
                object[] where = new object[]
                {
                    new object[]{ "journal_id", "=", 14 },
                    new object[]{"move_type", "=", "out_invoice" },
                    new object[]{ "date", "=", dateTime },
                };

                string[] fields = new string[]
                {
                };

                var model_data = odoo.SearchRead(models, where, fields);

                //try
                //{
                //    foreach (var partner in model_data)
                //    {

                //    }

                //}
                //catch (Exception ex)
                //{
                //    MessageBox.Show(ex.Message);
                //}


                DataTable oData = new DataTable();
                oData.Clear();
                oData.Columns.Add(new DataColumn() { ColumnName = "Doc_NumID", DataType = typeof(string) });
                oData.Columns.Add(new DataColumn() { ColumnName = "Doc_NumDoc", DataType = typeof(string) });
                oData.Columns.Add(new DataColumn() { ColumnName = "Doc_AsoDoc", DataType = typeof(string) });
                oData.Columns.Add(new DataColumn() { ColumnName = "Doc_TipDoc", DataType = typeof(string) });
                oData.Columns.Add(new DataColumn() { ColumnName = "Doc_CodCli", DataType = typeof(string) });
                oData.Columns.Add(new DataColumn() { ColumnName = "Doc_CodVen", DataType = typeof(string) });
                oData.Columns.Add(new DataColumn() { ColumnName = "Doc_Journa", DataType = typeof(string) });
                oData.Columns.Add(new DataColumn() { ColumnName = "Doc_FchDoc", DataType = typeof(string) });
                oData.Columns.Add(new DataColumn() { ColumnName = "Doc_NumFis", DataType = typeof(string) });
                oData.Columns.Add(new DataColumn() { ColumnName = "Doc_IsPrin", DataType = typeof(string) });


                foreach (var row_data in model_data)
                {
                    DataRow _line = oData.NewRow();
                    _line["Doc_NumID"] = row_data["id"].ToString();
                    _line["Doc_NumDoc"] = row_data["name"].ToString();
                    _line["Doc_AsoDoc"] = row_data["ref"].ToString();
                    _line["Doc_TipDoc"] = row_data["move_type"].ToString();
                    _line["Doc_CodCli"] = row_data["partner_id"].ToString();
                    _line["Doc_CodVen"] = row_data["invoice_user_id"].ToString();
                    _line["Doc_Journa"] = row_data["journal_id"].ToString();
                    _line["Doc_FchDoc"] = row_data["date"].ToString();
                    _line["Doc_NumFis"] = row_data["num_doc_fiscal"].ToString();
                    _line["Doc_IsPrin"] = row_data["is_print"].ToString();

                    oData.Rows.Add(_line);

                    //oData.Rows.Add(row_data["id"].ToString());
                    //MessageBox.Show("Cliente ID: "+row_data["name"].ToString());
                }
                DataGridView.DataSource = oData;
            }
        }

       
        public static DataTable GetDataTable(string cQuery)
        {

            DataTable oData = new DataTable();
            //name
            oData.Columns.Add(new DataColumn() { ColumnName = "FACTURA", DataType = typeof(string) });
            //invoice_payment_term_id
            oData.Columns.Add(new DataColumn() { ColumnName = "COD COND PAGO", DataType = typeof(string) });
            //state
            oData.Columns.Add(new DataColumn() { ColumnName = "STATUS", DataType = typeof(string) });
            //invoice_date
            oData.Columns.Add(new DataColumn() { ColumnName = "FECHA", DataType = typeof(string) });
            //rif
            oData.Columns.Add(new DataColumn() { ColumnName = "RIF CLIENTE", DataType = typeof(string) });
            //rif
            oData.Columns.Add(new DataColumn() { ColumnName = "COD CLIENTE", DataType = typeof(string) });
            //partner_id[1]
            oData.Columns.Add(new DataColumn() { ColumnName = "CLIENTE", DataType = typeof(string) });
            //invoice_date_due
            oData.Columns.Add(new DataColumn() { ColumnName = "F/VTO", DataType = typeof(string) });
            //
            oData.Columns.Add(new DataColumn() { ColumnName = "COD VENDEDOR", DataType = typeof(string) });
            //
            oData.Columns.Add(new DataColumn() { ColumnName = "TRANSPORTE", DataType = typeof(string) });
            //nro_ctrl
            oData.Columns.Add(new DataColumn() { ColumnName = "NO. DE CONTROL", DataType = typeof(string) });
            //currency_id
            oData.Columns.Add(new DataColumn() { ColumnName = "MONEDA", DataType = typeof(string) });
            //currency_bs_rate
            oData.Columns.Add(new DataColumn() { ColumnName = "TASA", DataType = typeof(string) });
            //nro_item
            oData.Columns.Add(new DataColumn() { ColumnName = "REG_NUM", DataType = typeof(string) });
            //default_code
            oData.Columns.Add(new DataColumn() { ColumnName = "COD ARTICULO", DataType = typeof(string) });
            //
            oData.Columns.Add(new DataColumn() { ColumnName = "ALMACEN", DataType = typeof(string) });
            //
            oData.Columns.Add(new DataColumn() { ColumnName = "CANTIDAD", DataType = typeof(string) });
            //
            oData.Columns.Add(new DataColumn() { ColumnName = "PRECIO BS.", DataType = typeof(string) });
            //
            oData.Columns.Add(new DataColumn() { ColumnName = "UNIDAD", DataType = typeof(string) });
            //
            oData.Columns.Add(new DataColumn() { ColumnName = "DSCTO MONTO", DataType = typeof(string) });
            //
            oData.Columns.Add(new DataColumn() { ColumnName = "DSCTO %", DataType = typeof(string) });
            //
            oData.Columns.Add(new DataColumn() { ColumnName = "NETO BS.", DataType = typeof(string) });
            //
            oData.Columns.Add(new DataColumn() { ColumnName = "IVA BS.", DataType = typeof(string) });
            //amount_total
            oData.Columns.Add(new DataColumn() { ColumnName = "TOTAL FACTURADO", DataType = typeof(string) });
            //
            oData.Columns.Add(new DataColumn() { ColumnName = "TIPO_TASA", DataType = typeof(string) });
            //
            oData.Columns.Add(new DataColumn() { ColumnName = "TASAG %", DataType = typeof(string) });
            //
            oData.Columns.Add(new DataColumn() { ColumnName = "COD SUCURSAL", DataType = typeof(string) });
            //
            oData.Columns.Add(new DataColumn() { ColumnName = "COS_PRO_UN", DataType = typeof(string) });
            //
            oData.Columns.Add(new DataColumn() { ColumnName = "ULT_COS_UN", DataType = typeof(string) });

            try
            {
                return oData;
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
            }

            return oData;
        }

        private void Consultar()
        {
            DataTable oQuery = new DataTable();
            OdooQuerys querys = new OdooQuerys();
            PFpgsql pg = new PFpgsql();

            string resp = querys.AccountMove("Z7C7007929", 1);
            MessageBox.Show(resp);

            oQuery = pg.GetDataTable(resp);

            DataGridView.DataSource = oQuery;

        }

        private void BtnClose_Click(object sender, EventArgs e)
        {
            this.Close();
        }

        private void BtnGetData_Click(object sender, EventArgs e)
        {
            Procesar();
        }

        private void BtnGetStruct_Click(object sender, EventArgs e)
        {
            Consultar();
        }
    }
}
