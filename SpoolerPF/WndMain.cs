using SpoolerPF.DataConfig;
using SpoolerPF.DataPrinter.Hka;
using SpoolerPF.DataSQL.Pgsql;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Configuration;
using System.Data;
using System.Drawing;
using System.Drawing.Text;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Security.Policy;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Windows.Input;

namespace SpoolerPF.Main
{
    public partial class WndMain : Form
    {
        private PFconfig oConfig = new PFconfig();
        private PFtfhka oFiscal = new PFtfhka();
        private PFhandle oHandle = new PFhandle();
        private DataTable oSearchDoc; 
        private DataTable oSearchMov;
        private DataTable oSearchPag;
        private int numberID;
        private string tipoDOC;
        private string cSerialPrinter;
        private string cRifPrinter;
        private int nUltimaFactura;
        private int nUltimaCredito;
        private bool bRun;
        private bool bError;

        public WndMain()
        {
            bRun = false;
            bError = false;
            oFiscal.PFstatus();
            cSerialPrinter = oFiscal.cS1SerialPrinter;
            cRifPrinter = oFiscal.cS1Rif;
            nUltimaFactura = oFiscal.nS1LastInvoice;
            InitializeComponent();

        }
        private void BtnOnOff(bool bOnOff)
        {
            BtnClose.Enabled = bOnOff;
            BtnCheck.Enabled = bOnOff;
            BtnReportX.Enabled = bOnOff;
            BtnReportZ.Enabled = bOnOff;
            BtnDatosS1.Enabled = bOnOff;
            BtnDatosS3.Enabled = bOnOff;
            BtnDatosS5.Enabled = bOnOff;
            BtnJackpot.Enabled = bOnOff;
            BtnReportD.Enabled = bOnOff;
            BtnRun.Enabled = bOnOff;

        }
        private void WndMain_Load(object sender, EventArgs e)
        {
            BtnStop.Enabled = false;
        }
        private void BtnClose_Click(object sender, EventArgs e)
        {
            Application.Exit();
        }

        private void BtnStop_Click(object sender, EventArgs e)
        {
            rTextBox.Clear();
            bRun = false;
            Thread.Sleep(1000);
            BtnStop.Enabled = false;
            BtnOnOff(true);
        }

        private void BtnCheck_Click(object sender, EventArgs e)
        {
            rTextBox.Clear();
            oFiscal.PFstatus();
            nUltimaFactura = oFiscal.nS1LastInvoice;
            rTextBox.Text = $"INICIAR PROCESO DE CAPTURA\r\n" +
                "Ultima Factura Registrada: " + nUltimaFactura + "\r\n" + oFiscal.cPFinfo;

           // MessageBox.Show(oFiscal.nS1LastInvoice.ToString());
        }

        private void BtnReportX_Click(object sender, EventArgs e)
        {
            rTextBox.Clear();
            oFiscal.PFreportX();
            rTextBox.Text = "REPORTE X\r\n" + oFiscal.cPFinfo;
        }

        private void BtnReportZ_Click(object sender, EventArgs e)
        {
            rTextBox.Clear();
            oFiscal.PFreportZ();
            rTextBox.Text = "REPORTE Z\r\n" + oFiscal.cPFinfo;
        }

        private void BtnDatosS1_Click(object sender, EventArgs e)
        {
            rTextBox.Clear();
            oFiscal.PFdataS1();
            rTextBox.Text = "S1PrinterData\r\n" + oFiscal.cPFinfo;
        }

        private void BtnDatosS3_Click(object sender, EventArgs e)
        {
            rTextBox.Clear();
            oFiscal.PFdataS3();
            rTextBox.Text = "S3PrinterData\r\n" + oFiscal.cPFinfo;
        }

        private void BtnDatosS5_Click(object sender, EventArgs e)
        {
            rTextBox.Clear();
            oFiscal.PFdataS5();
            rTextBox.Text = "S5PrinterData\r\n" + oFiscal.cPFinfo;
        }

        private void BtnJackpot_Click(object sender, EventArgs e)
        {
            rTextBox.Clear();
            oFiscal.PFjackpots();
            rTextBox.Text = "ACUMULADOS X DEL DIA\r\n" + oFiscal.cPFinfo;
        }

        private void BtnReportD_Click(object sender, EventArgs e)
        {
            rTextBox.Clear();
            oFiscal.PFreport();
            rTextBox.Text = "DETALLADOS X DEL DIA\r\n" + oFiscal.cPFinfo;
        }

        private void MonitorToolStripMenuItem_Click(object sender, EventArgs e)
        {
            rTextBox.Clear();
        }

        private void DataCheckToolStripMenuItem_Click(object sender, EventArgs e)
        {
            rTextBox.Clear();
            this.Hide();
            WndDataCheck wDataCheck = new WndDataCheck();
            wDataCheck.ShowDialog();
            this.Show();
        }

        private void ConfiguraciónToolStripMenuItem_Click(object sender, EventArgs e)
        {
            rTextBox.Clear();
            this.Hide();
            WndConfig wConfig = new WndConfig();
            wConfig.ShowDialog();
            this.Show();
        }

        private void BtnRun_Click(object sender, EventArgs e)
        {
            rTextBox.Clear();
            BtnOnOff(false);
            BtnStop.Enabled = true;
            bRun = true;
            Spooler();
        }

        private async void Spooler()
        {
            while (bRun)
            {
                if (!bRun) { break; }
                await Task.Run(() =>
                {
                    oFiscal.PFstatus();
                    nUltimaFactura = oFiscal.nS1LastInvoice;
                    nUltimaCredito = oFiscal.nS1LastCredit;
                    Thread.Sleep(1000);
                    //MessageBox.Show(nUltimaFactura.ToString(), "nUltimaFactura");
                    //MessageBox.Show(nUltimaCredito.ToString(), "nUltimaCredito");
                });

                if (!bRun) { break; }
                await Task.Run(() =>
                {
                    numberID = 0;
                    while (bRun)
                    {
                        if (!bRun || numberID > 0) { break; }

                        DataTable oGetInvoice = oHandle.GetInvoice(DataConfig.PFconfig.cPrinterSerial, 1);

                        if (oGetInvoice.Rows.Count == 0)
                        {
                            Thread.Sleep(15000);
                            numberID = 0;
                        }
                        else
                        {
                            foreach (DataRow row in oGetInvoice.Rows)
                            {
                                numberID = Convert.ToInt16(row["Id"]);
                                tipoDOC = Convert.ToString(row["Doc_Tipo"]);
                            }
                        }
                    }
                    Thread.Sleep(1000);
                });

                if (!bRun) { break; }
                await Task.Run(() =>
                {
                    oSearchDoc = oHandle.SearchDataDoc(numberID);
                    if (oSearchDoc.Rows.Count == 0) { oSearchDoc = null; }
                    Thread.Sleep(1000);
                });

                if (!bRun) { break; }
                await Task.Run(() =>
                {
                    oSearchMov = oHandle.SearchDataMov(numberID);
                    if (oSearchMov.Rows.Count == 0) { oSearchMov = null; }
                    Thread.Sleep(1000);
                });

                if (!bRun) { break; }
                await Task.Run(() =>
                {
                    oSearchPag = oHandle.SearchDataPag(numberID);
                    if (oSearchPag.Rows.Count == 0) { oSearchPag = null; }
                    Thread.Sleep(1000);
                });

                if (!bRun) { break; }
                await Task.Run(() =>
                {
                    if (oSearchDoc == null || oSearchMov == null || oSearchPag == null)
                    {
                        MessageBox.Show("ERROR AL ENVIAR PROCESO DE IMPRESION");
                        bError = true;  
                    }
                    else
                    {
                        if (tipoDOC== "out_invoice")
                        {
                            //MessageBox.Show("FACTURA");
                            oFiscal.PrintInvoice(oSearchDoc, oSearchMov, oSearchPag);
                        }
                        else
                        {
                            MessageBox.Show("NOTA DE CREDITO - EN PRUEBA");
                            //oFiscal.PrintCredit(oSearchDoc, oSearchMov, oSearchPag);
                        }


                        bError = false;
                    }
                    Thread.Sleep(1000);

                });

                if (!bRun) { break; }
                await Task.Run(() =>
                {
                    if (!bError)
                    {
                        string cUltimaFactura;

                        oFiscal.PFstatus();
                        Thread.Sleep(1000);
                        nUltimaFactura = oFiscal.nS1LastInvoice;
                        nUltimaCredito = oFiscal.nS1LastCredit;

                        if (tipoDOC == "out_invoice")
                        {
                            cUltimaFactura = nUltimaFactura.ToString();
                            cUltimaFactura = cUltimaFactura.PadLeft(8, '0');

                        }
                        else
                        {
                            cUltimaFactura = nUltimaCredito.ToString();
                            cUltimaFactura = cUltimaFactura.PadLeft(8, '0');
                        }


                        //MessageBox.Show(cUltimaFactura, "cUltimaFactura");
                        // Actualizar Factura
                        bool lActualizar = oHandle.UpdateInvoice(cUltimaFactura, numberID);
                    }


                });
            }
        }


    }


    //int nDoc = 0;
    //string cName = "";
    //string cRef = "";
    //var lEndTask = new TaskCompletionSource<bool>();

    //System.Threading.Thread.Sleep(1000);
    //oFiscal.PFstatus();
    //rTextBox.Text = oFiscal.IFErrorCodigo.ToString()+"\r\n"+ oFiscal.IFEstatusCodigo.ToString();
    //rTextBox.Text = oFiscal.ErrorValidity.ToString();

    // rTextBox.Text = oFiscal.cPFinfo;




    //_ = oHandle.Invoice(nDoc);

    //rTextBox.Text = oFiscal.cPFinfo;




    //rTextBox.Clear();

    //rTextBox.Text = oHandle.Handleinfo;

    //private void Spooler()
    //{
    //    //int result = 0;
    //    int nDoc = 0;
    //    string cRef = "";

    //    while (bRun)
    //    {
    //        if (!bRun) { break; }

    //        //result = Int32.Parse(nUltimaFactura);

    //        while (bRun & bFind)
    //        {
    //            DataTable oData = oHandle.Invoice(cSerialPrinter, 1);
    //            rTextBox.Text = "ESTADO DE CONEXION: \r\n" + oHandle.Handleinfo;
    //            if (oData.Rows.Count == 0)
    //            {
    //                System.Threading.Thread.Sleep(3000);
    //            }
    //            else
    //            {
    //                foreach (DataRow row in oData.Rows)
    //                {
    //                    nDoc = Convert.ToInt16(row["Id"]);
    //                    cRef = Convert.ToString(row["Doc_Asociado"]);
    //                    cRef = cRef.Trim();
    //                }
    //                bFind = false;
    //            }
    //        }

    //        if (bRun)
    //        {
    //            // Imprimir Factura
    //            _ = oHandle.Invoice(cRef);

    //            //result++;
    //            //result *= 0;
    //            //NumeroFacturaFiscal = result.ToString();
    //            //NumeroFacturaFiscal = NumeroFacturaFiscal.Replace(",", "").Replace(".", "");
    //            //NumeroFacturaFiscal = NumeroFacturaFiscal.PadLeft(8, '0');
    //            System.Threading.Thread.Sleep(3000);

    //            //ConsultarValores();

    //            //MessageBox.Show("Documento encontrado: " + cRef + " FACTURA :" + NumeroFacturaFiscal);

    //            
    //            bFind = true;
    //            System.Threading.Thread.Sleep(3000);

    //        }
    //    }
    //}


    //////private async Task ConnectAsync()
    //////{
    //////    var config = new OdooConfig(
    //////        apiUrl: "https://nombre_cliente.odoo.com",
    //////        dbName: "nombre_cliente-master-5604257",
    //////        userName: "nombre_usuario@dominio.com",
    //////        password: "mi_clave_base");

    //////    var odooClient = new OdooClient(config);
    //////    var versionResult = await odooClient.GetVersionAsync();

    //////    //var loginResult = await odooClient.LoginAsync();

    //////    var tableName = "account.move";
    //////    var modelResult = await odooClient.GetModelAsync(tableName);

    //////    var model = OdooModelMapper.GetDotNetModel(tableName, modelResult.Value);

    //////    var respository = new OdooRepository<model>(config);


    //////    //var repository = new OdooRepository<model>(config);
    //////    //var products = await repository.Query().ToListAsync();

    //////    MessageBox.Show(model.ToString());
    //////}


}
