namespace ToolsPF
{
    partial class WndMain
    {
        /// <summary>
        /// Variable del diseñador necesaria.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Limpiar los recursos que se estén usando.
        /// </summary>
        /// <param name="disposing">true si los recursos administrados se deben desechar; false en caso contrario.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Código generado por el Diseñador de Windows Forms

        /// <summary>
        /// Método necesario para admitir el Diseñador. No se puede modificar
        /// el contenido de este método con el editor de código.
        /// </summary>
        private void InitializeComponent()
        {
            this.BtnCheck = new System.Windows.Forms.Button();
            this.BtnReportX = new System.Windows.Forms.Button();
            this.BtnReportZ = new System.Windows.Forms.Button();
            this.BtnAmount = new System.Windows.Forms.Button();
            this.BtnRun = new System.Windows.Forms.Button();
            this.BtnExit = new System.Windows.Forms.Button();
            this.dataSQL = new System.Windows.Forms.DataGridView();
            this.TxtInformation = new System.Windows.Forms.RichTextBox();
            this.BtnStop = new System.Windows.Forms.Button();
            this.LblMonto = new System.Windows.Forms.Label();
            this.LblFactura = new System.Windows.Forms.Label();
            this.LblReporteZ = new System.Windows.Forms.Label();
            this.LblSerial = new System.Windows.Forms.Label();
            this.BtnCmd = new System.Windows.Forms.Button();
            ((System.ComponentModel.ISupportInitialize)(this.dataSQL)).BeginInit();
            this.SuspendLayout();
            // 
            // BtnCheck
            // 
            this.BtnCheck.AutoSize = true;
            this.BtnCheck.BackColor = System.Drawing.SystemColors.Desktop;
            this.BtnCheck.FlatStyle = System.Windows.Forms.FlatStyle.System;
            this.BtnCheck.Font = new System.Drawing.Font("Segoe UI", 9.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.BtnCheck.ForeColor = System.Drawing.SystemColors.ButtonFace;
            this.BtnCheck.Location = new System.Drawing.Point(410, 107);
            this.BtnCheck.Name = "BtnCheck";
            this.BtnCheck.Size = new System.Drawing.Size(82, 43);
            this.BtnCheck.TabIndex = 0;
            this.BtnCheck.Text = "Impresora\r\nCheck";
            this.BtnCheck.UseVisualStyleBackColor = false;
            this.BtnCheck.Click += new System.EventHandler(this.BtnCheck_Click);
            // 
            // BtnReportX
            // 
            this.BtnReportX.AutoSize = true;
            this.BtnReportX.BackColor = System.Drawing.SystemColors.Desktop;
            this.BtnReportX.FlatStyle = System.Windows.Forms.FlatStyle.System;
            this.BtnReportX.Font = new System.Drawing.Font("Segoe UI", 9.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.BtnReportX.ForeColor = System.Drawing.SystemColors.ButtonFace;
            this.BtnReportX.Location = new System.Drawing.Point(324, 58);
            this.BtnReportX.Name = "BtnReportX";
            this.BtnReportX.Size = new System.Drawing.Size(82, 43);
            this.BtnReportX.TabIndex = 1;
            this.BtnReportX.Text = "Reporte\r\nX";
            this.BtnReportX.UseVisualStyleBackColor = false;
            this.BtnReportX.Click += new System.EventHandler(this.BtnReportX_Click);
            // 
            // BtnReportZ
            // 
            this.BtnReportZ.AutoSize = true;
            this.BtnReportZ.BackColor = System.Drawing.SystemColors.Desktop;
            this.BtnReportZ.FlatStyle = System.Windows.Forms.FlatStyle.System;
            this.BtnReportZ.Font = new System.Drawing.Font("Segoe UI", 9.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.BtnReportZ.ForeColor = System.Drawing.SystemColors.ButtonFace;
            this.BtnReportZ.Location = new System.Drawing.Point(412, 58);
            this.BtnReportZ.Name = "BtnReportZ";
            this.BtnReportZ.Size = new System.Drawing.Size(82, 43);
            this.BtnReportZ.TabIndex = 2;
            this.BtnReportZ.Text = "Reporte\r\nZ";
            this.BtnReportZ.UseVisualStyleBackColor = false;
            this.BtnReportZ.Click += new System.EventHandler(this.BtnReportZ_Click);
            // 
            // BtnAmount
            // 
            this.BtnAmount.AutoSize = true;
            this.BtnAmount.BackColor = System.Drawing.SystemColors.Desktop;
            this.BtnAmount.FlatStyle = System.Windows.Forms.FlatStyle.System;
            this.BtnAmount.Font = new System.Drawing.Font("Segoe UI", 9.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.BtnAmount.ForeColor = System.Drawing.SystemColors.ButtonFace;
            this.BtnAmount.Location = new System.Drawing.Point(322, 107);
            this.BtnAmount.Name = "BtnAmount";
            this.BtnAmount.Size = new System.Drawing.Size(82, 43);
            this.BtnAmount.TabIndex = 3;
            this.BtnAmount.Text = "Monto\r\nFacturado";
            this.BtnAmount.UseVisualStyleBackColor = false;
            this.BtnAmount.Click += new System.EventHandler(this.BtnAmount_Click);
            // 
            // BtnRun
            // 
            this.BtnRun.AutoSize = true;
            this.BtnRun.BackColor = System.Drawing.SystemColors.Desktop;
            this.BtnRun.FlatStyle = System.Windows.Forms.FlatStyle.System;
            this.BtnRun.Font = new System.Drawing.Font("Segoe UI", 9.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.BtnRun.ForeColor = System.Drawing.SystemColors.ButtonFace;
            this.BtnRun.Location = new System.Drawing.Point(324, 9);
            this.BtnRun.Name = "BtnRun";
            this.BtnRun.Size = new System.Drawing.Size(82, 43);
            this.BtnRun.TabIndex = 4;
            this.BtnRun.Text = "Iniciar\r\nConexion";
            this.BtnRun.UseVisualStyleBackColor = false;
            this.BtnRun.Click += new System.EventHandler(this.BtnRun_Click);
            // 
            // BtnExit
            // 
            this.BtnExit.AutoSize = true;
            this.BtnExit.BackColor = System.Drawing.SystemColors.Desktop;
            this.BtnExit.FlatStyle = System.Windows.Forms.FlatStyle.System;
            this.BtnExit.Font = new System.Drawing.Font("Segoe UI", 9.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.BtnExit.ForeColor = System.Drawing.SystemColors.ButtonFace;
            this.BtnExit.Location = new System.Drawing.Point(412, 156);
            this.BtnExit.Name = "BtnExit";
            this.BtnExit.Size = new System.Drawing.Size(82, 43);
            this.BtnExit.TabIndex = 5;
            this.BtnExit.Text = "Salir";
            this.BtnExit.UseVisualStyleBackColor = false;
            this.BtnExit.Click += new System.EventHandler(this.BtnExit_Click);
            // 
            // dataSQL
            // 
            this.dataSQL.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.dataSQL.Location = new System.Drawing.Point(5, 12);
            this.dataSQL.Name = "dataSQL";
            this.dataSQL.RowHeadersWidth = 30;
            this.dataSQL.Size = new System.Drawing.Size(80, 43);
            this.dataSQL.TabIndex = 6;
            // 
            // TxtInformation
            // 
            this.TxtInformation.Location = new System.Drawing.Point(5, 72);
            this.TxtInformation.Name = "TxtInformation";
            this.TxtInformation.Size = new System.Drawing.Size(80, 43);
            this.TxtInformation.TabIndex = 7;
            this.TxtInformation.Text = "";
            // 
            // BtnStop
            // 
            this.BtnStop.AutoSize = true;
            this.BtnStop.BackColor = System.Drawing.SystemColors.Desktop;
            this.BtnStop.FlatStyle = System.Windows.Forms.FlatStyle.System;
            this.BtnStop.Font = new System.Drawing.Font("Segoe UI", 9.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.BtnStop.ForeColor = System.Drawing.SystemColors.ButtonFace;
            this.BtnStop.Location = new System.Drawing.Point(412, 9);
            this.BtnStop.Name = "BtnStop";
            this.BtnStop.Size = new System.Drawing.Size(82, 43);
            this.BtnStop.TabIndex = 8;
            this.BtnStop.Text = "Detener\r\nConexion";
            this.BtnStop.UseVisualStyleBackColor = false;
            this.BtnStop.Click += new System.EventHandler(this.BtnStop_Click);
            // 
            // LblMonto
            // 
            this.LblMonto.AutoSize = true;
            this.LblMonto.Font = new System.Drawing.Font("Microsoft YaHei", 9F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.LblMonto.Location = new System.Drawing.Point(97, 133);
            this.LblMonto.Name = "LblMonto";
            this.LblMonto.Size = new System.Drawing.Size(121, 17);
            this.LblMonto.TabIndex = 9;
            this.LblMonto.Text = "Monto Facturado: ";
            // 
            // LblFactura
            // 
            this.LblFactura.AutoSize = true;
            this.LblFactura.Font = new System.Drawing.Font("Microsoft YaHei", 9F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.LblFactura.Location = new System.Drawing.Point(97, 58);
            this.LblFactura.Name = "LblFactura";
            this.LblFactura.Size = new System.Drawing.Size(105, 17);
            this.LblFactura.TabIndex = 10;
            this.LblFactura.Text = "Ultima Factura: ";
            // 
            // LblReporteZ
            // 
            this.LblReporteZ.AutoSize = true;
            this.LblReporteZ.Font = new System.Drawing.Font("Microsoft YaHei", 9F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.LblReporteZ.Location = new System.Drawing.Point(97, 98);
            this.LblReporteZ.Name = "LblReporteZ";
            this.LblReporteZ.Size = new System.Drawing.Size(121, 17);
            this.LblReporteZ.TabIndex = 11;
            this.LblReporteZ.Text = "Ultimo Reporte Z: ";
            // 
            // LblSerial
            // 
            this.LblSerial.AutoSize = true;
            this.LblSerial.Font = new System.Drawing.Font("Microsoft YaHei", 9F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.LblSerial.Location = new System.Drawing.Point(97, 12);
            this.LblSerial.Name = "LblSerial";
            this.LblSerial.Size = new System.Drawing.Size(115, 17);
            this.LblSerial.TabIndex = 12;
            this.LblSerial.Text = "Serial Impresora: ";
            // 
            // BtnCmd
            // 
            this.BtnCmd.AutoSize = true;
            this.BtnCmd.BackColor = System.Drawing.SystemColors.Desktop;
            this.BtnCmd.FlatStyle = System.Windows.Forms.FlatStyle.System;
            this.BtnCmd.Font = new System.Drawing.Font("Segoe UI", 9.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.BtnCmd.ForeColor = System.Drawing.SystemColors.ButtonFace;
            this.BtnCmd.Location = new System.Drawing.Point(324, 156);
            this.BtnCmd.Name = "BtnCmd";
            this.BtnCmd.Size = new System.Drawing.Size(82, 43);
            this.BtnCmd.TabIndex = 13;
            this.BtnCmd.Text = "Impresora\r\nCmd";
            this.BtnCmd.UseVisualStyleBackColor = false;
            this.BtnCmd.Click += new System.EventHandler(this.BtnCmd_Click);
            // 
            // WndMain
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(503, 204);
            this.Controls.Add(this.BtnCmd);
            this.Controls.Add(this.LblSerial);
            this.Controls.Add(this.LblReporteZ);
            this.Controls.Add(this.LblFactura);
            this.Controls.Add(this.LblMonto);
            this.Controls.Add(this.BtnStop);
            this.Controls.Add(this.TxtInformation);
            this.Controls.Add(this.dataSQL);
            this.Controls.Add(this.BtnExit);
            this.Controls.Add(this.BtnRun);
            this.Controls.Add(this.BtnAmount);
            this.Controls.Add(this.BtnReportZ);
            this.Controls.Add(this.BtnReportX);
            this.Controls.Add(this.BtnCheck);
            this.Name = "WndMain";
            this.Text = "Main";
            this.Load += new System.EventHandler(this.WndMain_Load);
            ((System.ComponentModel.ISupportInitialize)(this.dataSQL)).EndInit();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.Button BtnCheck;
        private System.Windows.Forms.Button BtnReportX;
        private System.Windows.Forms.Button BtnReportZ;
        private System.Windows.Forms.Button BtnAmount;
        private System.Windows.Forms.Button BtnRun;
        private System.Windows.Forms.Button BtnExit;
        private System.Windows.Forms.DataGridView dataSQL;
        private System.Windows.Forms.RichTextBox TxtInformation;
        private System.Windows.Forms.Button BtnStop;
        private System.Windows.Forms.Label LblMonto;
        private System.Windows.Forms.Label LblFactura;
        private System.Windows.Forms.Label LblReporteZ;
        private System.Windows.Forms.Label LblSerial;
        private System.Windows.Forms.Button BtnCmd;
    }
}

