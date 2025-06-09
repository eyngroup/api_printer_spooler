using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Reflection;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;
using ToolsPF.Class;
using ToolsPF.Querys;
using static System.Windows.Forms.VisualStyles.VisualStyleElement.StartPanel;


namespace ToolsPF
{
    public partial class WndMain : Form
    {
        readonly PFfiscal oEjecutar = new PFfiscal();
        readonly OdooQuerys oQuery = new OdooQuerys();
        readonly PFUtils oUtils = new PFUtils();
        private bool bRun = false;
        private bool bFind = false;
        private string NumeroFacturaFiscal;
        private string MontoAcumulado;
        private string UltimoReporteZ;
        private string SerialImpresora;

        public WndMain()
        {
            InitializeComponent();
        }
        private void BtnOnOff(bool bOnOff)
        {
            BtnRun.Enabled = bOnOff;
            BtnCheck.Enabled = bOnOff;
            BtnReportX.Enabled = bOnOff;
            BtnReportZ.Enabled = bOnOff;
            BtnAmount.Enabled = bOnOff;
            BtnExit.Enabled = bOnOff;

        }
        private void WndMain_Load(object sender, EventArgs e)
        {
            BtnStop.Enabled = false;
            //Que es System.Threading.Thread.Sleep(500);
        }
        private void BtnRun_Click(object sender, EventArgs e)
        {
            this.BtnOnOff(false);
            BtnStop.Enabled = true;
            bRun = true;
            bFind = true;
            ConsultarValores();
            //System.Threading.Thread.Sleep(2000);

            Task task = Task.Run(() => Conexion());
            //Thread thread = new Thread(() => Conexion());
            //thread.Start();

            //Conexion();

            

            //System.Threading.Thread.Sleep(800);
        }
        private void BtnStop_Click(object sender, EventArgs e)
        {
            bRun = false;
            this.BtnOnOff(true);
        }
        private void BtnCheck_Click(object sender, EventArgs e)
        {
            this.BtnOnOff(false);
            //oEjecutar.Factura("Punto de Venta/0004");
            //oEjecutar.ComprobarImpresora();

            //dataSQL.DataSource = PFUtils.GetDataTable(oQuery.AccountMove(SerialImpresora, 1));
            //oEjecutar.Reporte();
            TxtInformation.Text = oEjecutar.Reporte();
            this.BtnOnOff(true);
        }
        private void BtnReportX_Click(object sender, EventArgs e)
        {
            this.BtnOnOff(false);
            oEjecutar.EmitirX();
            this.BtnOnOff(true);
        }
        private void BtnReportZ_Click(object sender, EventArgs e)
        {
            this.BtnOnOff(false);
            oEjecutar.EmitirZ();
            this.BtnOnOff(true);
        }
        private void BtnAmount_Click(object sender, EventArgs e)
        {
            ConsultarValores();
            //dataSQL.DataSource = PFUtils.GetDataTable(oQuery.AccountMove(SerialImpresora, 1));
            //dataSQL.DataSource = PFUtils.GetDataTable(oQuery.AccountMove("Alberto-POS/1581"));
            //System.Threading.Thread.Sleep(5000);
            //dataSQL.DataSource = PFUtils.GetDataTable(oQuery.AccountMoveLine("Alberto-POS/1581"));
            //System.Threading.Thread.Sleep(5000);
            //dataSQL.DataSource = PFUtils.GetDataTable(oQuery.PosOrder("Alberto-POS/1581"));


            //oEjecutar.TestFacturaA();
            //oEjecutar.EnviarCommando("D");
            //System.Threading.Thread.Sleep(3000);
            //oEjecutar.EnviarCommando("I0X");
            //TxtInformation.Text = oEjecutar.Reporte();
            //System.Threading.Thread.Sleep(3000);
        }
        private void BtnExit_Click(object sender, EventArgs e)
        {
            this.Close();
        }

        private void Conexion()
        {
            int result = 0; 
            int nDoc = 0;
            string cRef = "";

            //MessageBox.Show("En Conexion: "+ bRun.ToString() + " - " + bFind.ToString());

            while (bRun)
            {
                if (!bRun) { break; }

                //ConsultarValores();

                //MessageBox.Show("En While: " + bRun.ToString() + " - " + bFind.ToString());


                result = Int32.Parse(NumeroFacturaFiscal);

                while (bRun & bFind)
                {
                    //MessageBox.Show("En Find: "+ SerialImpresora + " - "+ bRun.ToString() + " - " + bFind.ToString());

                    DataTable oData = PFUtils.GetDataTable(oQuery.AccountMove(SerialImpresora, 1));

                    if (oData.Rows.Count == 0)
                    {
                        System.Threading.Thread.Sleep(10000);
                    }
                    else
                    {
                        foreach (DataRow row in oData.Rows)
                        {
                            nDoc = Convert.ToInt16(row["Id"]);
                            cRef = Convert.ToString(row["Doc_Asociado"]);
                            cRef = cRef.Trim();
                        }
                        bFind = false;
                    }
                }


                //MessageBox.Show("Documento encontrado: " + cRef + " FACTURA :" + NumeroFacturaFiscal);

                if (bRun)
                {
                    // Imprimir Factura
                    oEjecutar.Factura(cRef);

                    result++;
                    //result *= 0;
                    NumeroFacturaFiscal = result.ToString();
                    NumeroFacturaFiscal = NumeroFacturaFiscal.Replace(",", "").Replace(".", "");
                    NumeroFacturaFiscal = NumeroFacturaFiscal.PadLeft(8, '0');
                    System.Threading.Thread.Sleep(3000);

                    //ConsultarValores();

                    //MessageBox.Show("Documento encontrado: " + cRef + " FACTURA :" + NumeroFacturaFiscal);

                    // Actualizar Factura
                    oUtils.Update(oQuery.UpdateAccountMove(SerialImpresora, NumeroFacturaFiscal, nDoc));
                    bFind = true;
                    System.Threading.Thread.Sleep(3000);

                }

                

                
            }
        }

        private void ConsultarValores()
        {
            string[] aValores = new string[4];
            aValores = oEjecutar.Valores();
            NumeroFacturaFiscal = aValores[0];
            MontoAcumulado = aValores[1];
            UltimoReporteZ = aValores[2];
            SerialImpresora = aValores[3];

            LblFactura.Text = "Ultima Factura: " + NumeroFacturaFiscal;
            LblMonto.Text = "Monto Facturado: " + MontoAcumulado;
            LblReporteZ.Text = "Ultimo Reporte Z: " + UltimoReporteZ;
            LblSerial.Text = "Serial Impresora: " + SerialImpresora;
        }

        private void BtnCmd_Click(object sender, EventArgs e)
        {
            oEjecutar.EnviarCommando("199");
        }
    }
}
