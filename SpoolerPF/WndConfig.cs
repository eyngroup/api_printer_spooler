using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Security.Policy;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace SpoolerPF.Main
{
    public partial class WndConfig : Form
    {
        public WndConfig()
        {
            InitializeComponent();
            LoadFields();
        }

        private void LoadFields()
        {
            txtPortComm.Text = SpoolerPF.DataConfig.PFconfig.cPortComm;
            txtPrinterSerial.Text = SpoolerPF.DataConfig.PFconfig.cPrinterSerial;
            txtCompanyVAT.Text = SpoolerPF.DataConfig.PFconfig.cCompanyVAT;
            txtOdooUrl.Text = SpoolerPF.DataConfig.PFconfig.cOdooUrl;
            txtOdooDb.Text = SpoolerPF.DataConfig.PFconfig.cOdooDb;
            txtOdooUser.Text = SpoolerPF.DataConfig.PFconfig.cOdooUser;
            txtOdooPass.Text = SpoolerPF.DataConfig.PFconfig.cOdooPass;
            txtOdooCompany.Text = SpoolerPF.DataConfig.PFconfig.cOdooCompany;
            txtSQLServer.Text = SpoolerPF.DataConfig.PFconfig.cSQLServer;
            txtSQLPort.Text = SpoolerPF.DataConfig.PFconfig.cSQLPort;
            txtSQLDataBase.Text = SpoolerPF.DataConfig.PFconfig.cSQLDataBase;
            txtSQLUser.Text = SpoolerPF.DataConfig.PFconfig.cSQLUser;
            txtSQLPassword.Text = SpoolerPF.DataConfig.PFconfig.cSQLPassword;
        }

        private void BtnClose_Click(object sender, EventArgs e)
        {
            this.Close();   
        }

        private void btnLoad_Click(object sender, EventArgs e)
        {

        }

        private void btnRecord_Click(object sender, EventArgs e)
        {
            
        }
    }
}
