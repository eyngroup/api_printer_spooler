namespace SpoolerPF.Main
{
    partial class WndConfig
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            this.btnClose = new System.Windows.Forms.Button();
            this.lblPortComm = new System.Windows.Forms.Label();
            this.lblPrinterSerial = new System.Windows.Forms.Label();
            this.lblSqlServer = new System.Windows.Forms.Label();
            this.lblSQLPort = new System.Windows.Forms.Label();
            this.lblSQLDataBase = new System.Windows.Forms.Label();
            this.lblSQLUser = new System.Windows.Forms.Label();
            this.lblSQLPassword = new System.Windows.Forms.Label();
            this.lblOdooUrl = new System.Windows.Forms.Label();
            this.lblOdooDb = new System.Windows.Forms.Label();
            this.lblOdooUser = new System.Windows.Forms.Label();
            this.lblOdooPass = new System.Windows.Forms.Label();
            this.lblOdooCompany = new System.Windows.Forms.Label();
            this.lblCompanyVAT = new System.Windows.Forms.Label();
            this.txtPrinterSerial = new System.Windows.Forms.TextBox();
            this.txtCompanyVAT = new System.Windows.Forms.TextBox();
            this.txtSQLServer = new System.Windows.Forms.TextBox();
            this.txtSQLDataBase = new System.Windows.Forms.TextBox();
            this.txtSQLUser = new System.Windows.Forms.TextBox();
            this.txtSQLPassword = new System.Windows.Forms.TextBox();
            this.txtOdooUrl = new System.Windows.Forms.TextBox();
            this.txtOdooDb = new System.Windows.Forms.TextBox();
            this.txtOdooUser = new System.Windows.Forms.TextBox();
            this.txtOdooPass = new System.Windows.Forms.TextBox();
            this.txtOdooCompany = new System.Windows.Forms.TextBox();
            this.groupPrinter = new System.Windows.Forms.GroupBox();
            this.txtPortComm = new System.Windows.Forms.TextBox();
            this.groupServer = new System.Windows.Forms.GroupBox();
            this.txtSQLPort = new System.Windows.Forms.TextBox();
            this.groupOdoo = new System.Windows.Forms.GroupBox();
            this.btnRecord = new System.Windows.Forms.Button();
            this.btnLoad = new System.Windows.Forms.Button();
            this.groupPrinter.SuspendLayout();
            this.groupServer.SuspendLayout();
            this.groupOdoo.SuspendLayout();
            this.SuspendLayout();
            // 
            // btnClose
            // 
            this.btnClose.AutoSizeMode = System.Windows.Forms.AutoSizeMode.GrowAndShrink;
            this.btnClose.BackColor = System.Drawing.SystemColors.ControlDarkDark;
            this.btnClose.Font = new System.Drawing.Font("Segoe UI Semilight", 9.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.btnClose.ForeColor = System.Drawing.SystemColors.ControlLightLight;
            this.btnClose.Location = new System.Drawing.Point(610, 30);
            this.btnClose.Name = "btnClose";
            this.btnClose.Size = new System.Drawing.Size(90, 60);
            this.btnClose.TabIndex = 13;
            this.btnClose.Text = "Cerrar";
            this.btnClose.UseVisualStyleBackColor = false;
            this.btnClose.Click += new System.EventHandler(this.BtnClose_Click);
            // 
            // lblPortComm
            // 
            this.lblPortComm.AutoSize = true;
            this.lblPortComm.Font = new System.Drawing.Font("Trebuchet MS", 9.75F, ((System.Drawing.FontStyle)((System.Drawing.FontStyle.Bold | System.Drawing.FontStyle.Italic))), System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblPortComm.Location = new System.Drawing.Point(6, 15);
            this.lblPortComm.Name = "lblPortComm";
            this.lblPortComm.Size = new System.Drawing.Size(193, 18);
            this.lblPortComm.TabIndex = 15;
            this.lblPortComm.Text = "Puerto de Conexión Impresora";
            // 
            // lblPrinterSerial
            // 
            this.lblPrinterSerial.AutoSize = true;
            this.lblPrinterSerial.Font = new System.Drawing.Font("Trebuchet MS", 9.75F, ((System.Drawing.FontStyle)((System.Drawing.FontStyle.Bold | System.Drawing.FontStyle.Italic))), System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblPrinterSerial.Location = new System.Drawing.Point(6, 40);
            this.lblPrinterSerial.Name = "lblPrinterSerial";
            this.lblPrinterSerial.Size = new System.Drawing.Size(146, 18);
            this.lblPrinterSerial.TabIndex = 16;
            this.lblPrinterSerial.Text = "Serial de la Impresora";
            // 
            // lblSqlServer
            // 
            this.lblSqlServer.AutoSize = true;
            this.lblSqlServer.Font = new System.Drawing.Font("Trebuchet MS", 9.75F, ((System.Drawing.FontStyle)((System.Drawing.FontStyle.Bold | System.Drawing.FontStyle.Italic))), System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblSqlServer.Location = new System.Drawing.Point(6, 15);
            this.lblSqlServer.Name = "lblSqlServer";
            this.lblSqlServer.Size = new System.Drawing.Size(186, 18);
            this.lblSqlServer.TabIndex = 17;
            this.lblSqlServer.Text = "Servidor de Base de Datos IP";
            // 
            // lblSQLPort
            // 
            this.lblSQLPort.AutoSize = true;
            this.lblSQLPort.Font = new System.Drawing.Font("Trebuchet MS", 9.75F, ((System.Drawing.FontStyle)((System.Drawing.FontStyle.Bold | System.Drawing.FontStyle.Italic))), System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblSQLPort.Location = new System.Drawing.Point(6, 40);
            this.lblSQLPort.Name = "lblSQLPort";
            this.lblSQLPort.Size = new System.Drawing.Size(196, 18);
            this.lblSQLPort.TabIndex = 18;
            this.lblSQLPort.Text = "Puerto Servidor Base de Datos";
            // 
            // lblSQLDataBase
            // 
            this.lblSQLDataBase.AutoSize = true;
            this.lblSQLDataBase.Font = new System.Drawing.Font("Trebuchet MS", 9.75F, ((System.Drawing.FontStyle)((System.Drawing.FontStyle.Bold | System.Drawing.FontStyle.Italic))), System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblSQLDataBase.Location = new System.Drawing.Point(6, 65);
            this.lblSQLDataBase.Name = "lblSQLDataBase";
            this.lblSQLDataBase.Size = new System.Drawing.Size(182, 18);
            this.lblSQLDataBase.TabIndex = 19;
            this.lblSQLDataBase.Text = "Nombre de la Base de Datos";
            // 
            // lblSQLUser
            // 
            this.lblSQLUser.AutoSize = true;
            this.lblSQLUser.Font = new System.Drawing.Font("Trebuchet MS", 9.75F, ((System.Drawing.FontStyle)((System.Drawing.FontStyle.Bold | System.Drawing.FontStyle.Italic))), System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblSQLUser.Location = new System.Drawing.Point(6, 90);
            this.lblSQLUser.Name = "lblSQLUser";
            this.lblSQLUser.Size = new System.Drawing.Size(181, 18);
            this.lblSQLUser.TabIndex = 20;
            this.lblSQLUser.Text = "Usuario de la Base de Datos";
            // 
            // lblSQLPassword
            // 
            this.lblSQLPassword.AutoSize = true;
            this.lblSQLPassword.Font = new System.Drawing.Font("Trebuchet MS", 9.75F, ((System.Drawing.FontStyle)((System.Drawing.FontStyle.Bold | System.Drawing.FontStyle.Italic))), System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblSQLPassword.Location = new System.Drawing.Point(6, 115);
            this.lblSQLPassword.Name = "lblSQLPassword";
            this.lblSQLPassword.Size = new System.Drawing.Size(193, 18);
            this.lblSQLPassword.TabIndex = 21;
            this.lblSQLPassword.Text = "Password de la Base de Datos";
            // 
            // lblOdooUrl
            // 
            this.lblOdooUrl.AutoSize = true;
            this.lblOdooUrl.Font = new System.Drawing.Font("Trebuchet MS", 9.75F, ((System.Drawing.FontStyle)((System.Drawing.FontStyle.Bold | System.Drawing.FontStyle.Italic))), System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblOdooUrl.Location = new System.Drawing.Point(6, 15);
            this.lblOdooUrl.Name = "lblOdooUrl";
            this.lblOdooUrl.Size = new System.Drawing.Size(114, 18);
            this.lblOdooUrl.TabIndex = 22;
            this.lblOdooUrl.Text = "Servidor de Odoo";
            // 
            // lblOdooDb
            // 
            this.lblOdooDb.AutoSize = true;
            this.lblOdooDb.Font = new System.Drawing.Font("Trebuchet MS", 9.75F, ((System.Drawing.FontStyle)((System.Drawing.FontStyle.Bold | System.Drawing.FontStyle.Italic))), System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblOdooDb.Location = new System.Drawing.Point(6, 40);
            this.lblOdooDb.Name = "lblOdooDb";
            this.lblOdooDb.Size = new System.Drawing.Size(149, 18);
            this.lblOdooDb.TabIndex = 23;
            this.lblOdooDb.Text = "Base de Datos de Odoo";
            // 
            // lblOdooUser
            // 
            this.lblOdooUser.AutoSize = true;
            this.lblOdooUser.Font = new System.Drawing.Font("Trebuchet MS", 9.75F, ((System.Drawing.FontStyle)((System.Drawing.FontStyle.Bold | System.Drawing.FontStyle.Italic))), System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblOdooUser.Location = new System.Drawing.Point(6, 65);
            this.lblOdooUser.Name = "lblOdooUser";
            this.lblOdooUser.Size = new System.Drawing.Size(109, 18);
            this.lblOdooUser.TabIndex = 24;
            this.lblOdooUser.Text = "Usuario de Odoo";
            // 
            // lblOdooPass
            // 
            this.lblOdooPass.AutoSize = true;
            this.lblOdooPass.Font = new System.Drawing.Font("Trebuchet MS", 9.75F, ((System.Drawing.FontStyle)((System.Drawing.FontStyle.Bold | System.Drawing.FontStyle.Italic))), System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblOdooPass.Location = new System.Drawing.Point(6, 90);
            this.lblOdooPass.Name = "lblOdooPass";
            this.lblOdooPass.Size = new System.Drawing.Size(121, 18);
            this.lblOdooPass.TabIndex = 25;
            this.lblOdooPass.Text = "Password de Odoo";
            // 
            // lblOdooCompany
            // 
            this.lblOdooCompany.AutoSize = true;
            this.lblOdooCompany.Font = new System.Drawing.Font("Trebuchet MS", 9.75F, ((System.Drawing.FontStyle)((System.Drawing.FontStyle.Bold | System.Drawing.FontStyle.Italic))), System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblOdooCompany.Location = new System.Drawing.Point(6, 115);
            this.lblOdooCompany.Name = "lblOdooCompany";
            this.lblOdooCompany.Size = new System.Drawing.Size(113, 18);
            this.lblOdooCompany.TabIndex = 26;
            this.lblOdooCompany.Text = "ID de la Empresa";
            // 
            // lblCompanyVAT
            // 
            this.lblCompanyVAT.AutoSize = true;
            this.lblCompanyVAT.Font = new System.Drawing.Font("Trebuchet MS", 9.75F, ((System.Drawing.FontStyle)((System.Drawing.FontStyle.Bold | System.Drawing.FontStyle.Italic))), System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.lblCompanyVAT.Location = new System.Drawing.Point(6, 65);
            this.lblCompanyVAT.Name = "lblCompanyVAT";
            this.lblCompanyVAT.Size = new System.Drawing.Size(123, 18);
            this.lblCompanyVAT.TabIndex = 27;
            this.lblCompanyVAT.Text = "Rif de la Empresa:";
            // 
            // txtPrinterSerial
            // 
            this.txtPrinterSerial.Font = new System.Drawing.Font("Segoe UI", 8.25F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.txtPrinterSerial.Location = new System.Drawing.Point(230, 40);
            this.txtPrinterSerial.Name = "txtPrinterSerial";
            this.txtPrinterSerial.Size = new System.Drawing.Size(90, 22);
            this.txtPrinterSerial.TabIndex = 28;
            // 
            // txtCompanyVAT
            // 
            this.txtCompanyVAT.Font = new System.Drawing.Font("Segoe UI", 8.25F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.txtCompanyVAT.Location = new System.Drawing.Point(230, 65);
            this.txtCompanyVAT.Name = "txtCompanyVAT";
            this.txtCompanyVAT.Size = new System.Drawing.Size(90, 22);
            this.txtCompanyVAT.TabIndex = 29;
            // 
            // txtSQLServer
            // 
            this.txtSQLServer.Font = new System.Drawing.Font("Segoe UI", 8.25F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.txtSQLServer.Location = new System.Drawing.Point(230, 15);
            this.txtSQLServer.Name = "txtSQLServer";
            this.txtSQLServer.Size = new System.Drawing.Size(90, 22);
            this.txtSQLServer.TabIndex = 30;
            // 
            // txtSQLDataBase
            // 
            this.txtSQLDataBase.Font = new System.Drawing.Font("Segoe UI", 8.25F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.txtSQLDataBase.Location = new System.Drawing.Point(230, 65);
            this.txtSQLDataBase.Name = "txtSQLDataBase";
            this.txtSQLDataBase.Size = new System.Drawing.Size(90, 22);
            this.txtSQLDataBase.TabIndex = 32;
            // 
            // txtSQLUser
            // 
            this.txtSQLUser.Font = new System.Drawing.Font("Segoe UI", 8.25F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.txtSQLUser.Location = new System.Drawing.Point(230, 90);
            this.txtSQLUser.Name = "txtSQLUser";
            this.txtSQLUser.Size = new System.Drawing.Size(90, 22);
            this.txtSQLUser.TabIndex = 33;
            // 
            // txtSQLPassword
            // 
            this.txtSQLPassword.Font = new System.Drawing.Font("Segoe UI", 8.25F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.txtSQLPassword.Location = new System.Drawing.Point(230, 115);
            this.txtSQLPassword.Name = "txtSQLPassword";
            this.txtSQLPassword.Size = new System.Drawing.Size(90, 22);
            this.txtSQLPassword.TabIndex = 34;
            // 
            // txtOdooUrl
            // 
            this.txtOdooUrl.Font = new System.Drawing.Font("Segoe UI", 8.25F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.txtOdooUrl.Location = new System.Drawing.Point(180, 15);
            this.txtOdooUrl.Name = "txtOdooUrl";
            this.txtOdooUrl.Size = new System.Drawing.Size(160, 22);
            this.txtOdooUrl.TabIndex = 35;
            // 
            // txtOdooDb
            // 
            this.txtOdooDb.Font = new System.Drawing.Font("Segoe UI", 8.25F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.txtOdooDb.Location = new System.Drawing.Point(180, 40);
            this.txtOdooDb.Name = "txtOdooDb";
            this.txtOdooDb.Size = new System.Drawing.Size(160, 22);
            this.txtOdooDb.TabIndex = 36;
            // 
            // txtOdooUser
            // 
            this.txtOdooUser.Font = new System.Drawing.Font("Segoe UI", 8.25F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.txtOdooUser.Location = new System.Drawing.Point(180, 65);
            this.txtOdooUser.Name = "txtOdooUser";
            this.txtOdooUser.Size = new System.Drawing.Size(160, 22);
            this.txtOdooUser.TabIndex = 37;
            // 
            // txtOdooPass
            // 
            this.txtOdooPass.Font = new System.Drawing.Font("Segoe UI", 8.25F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.txtOdooPass.Location = new System.Drawing.Point(180, 90);
            this.txtOdooPass.Name = "txtOdooPass";
            this.txtOdooPass.Size = new System.Drawing.Size(160, 22);
            this.txtOdooPass.TabIndex = 38;
            // 
            // txtOdooCompany
            // 
            this.txtOdooCompany.Font = new System.Drawing.Font("Segoe UI", 8.25F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.txtOdooCompany.Location = new System.Drawing.Point(180, 115);
            this.txtOdooCompany.Name = "txtOdooCompany";
            this.txtOdooCompany.Size = new System.Drawing.Size(40, 22);
            this.txtOdooCompany.TabIndex = 39;
            // 
            // groupPrinter
            // 
            this.groupPrinter.BackColor = System.Drawing.SystemColors.InactiveCaption;
            this.groupPrinter.Controls.Add(this.txtPortComm);
            this.groupPrinter.Controls.Add(this.lblPortComm);
            this.groupPrinter.Controls.Add(this.lblPrinterSerial);
            this.groupPrinter.Controls.Add(this.lblCompanyVAT);
            this.groupPrinter.Controls.Add(this.txtPrinterSerial);
            this.groupPrinter.Controls.Add(this.txtCompanyVAT);
            this.groupPrinter.Location = new System.Drawing.Point(12, 12);
            this.groupPrinter.Name = "groupPrinter";
            this.groupPrinter.RightToLeft = System.Windows.Forms.RightToLeft.Yes;
            this.groupPrinter.Size = new System.Drawing.Size(330, 100);
            this.groupPrinter.TabIndex = 41;
            this.groupPrinter.TabStop = false;
            this.groupPrinter.Text = "Parámetros de Impresora Fiscal";
            // 
            // txtPortComm
            // 
            this.txtPortComm.Font = new System.Drawing.Font("Segoe UI", 8.25F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.txtPortComm.Location = new System.Drawing.Point(230, 15);
            this.txtPortComm.Name = "txtPortComm";
            this.txtPortComm.Size = new System.Drawing.Size(90, 22);
            this.txtPortComm.TabIndex = 30;
            // 
            // groupServer
            // 
            this.groupServer.BackColor = System.Drawing.SystemColors.GradientActiveCaption;
            this.groupServer.Controls.Add(this.txtSQLPort);
            this.groupServer.Controls.Add(this.lblSqlServer);
            this.groupServer.Controls.Add(this.txtSQLServer);
            this.groupServer.Controls.Add(this.lblSQLPort);
            this.groupServer.Controls.Add(this.lblSQLDataBase);
            this.groupServer.Controls.Add(this.lblSQLUser);
            this.groupServer.Controls.Add(this.lblSQLPassword);
            this.groupServer.Controls.Add(this.txtSQLPassword);
            this.groupServer.Controls.Add(this.txtSQLDataBase);
            this.groupServer.Controls.Add(this.txtSQLUser);
            this.groupServer.Location = new System.Drawing.Point(12, 115);
            this.groupServer.Name = "groupServer";
            this.groupServer.RightToLeft = System.Windows.Forms.RightToLeft.Yes;
            this.groupServer.Size = new System.Drawing.Size(330, 150);
            this.groupServer.TabIndex = 42;
            this.groupServer.TabStop = false;
            this.groupServer.Text = "Parámetros del Servidor de Base de Datos";
            // 
            // txtSQLPort
            // 
            this.txtSQLPort.Font = new System.Drawing.Font("Segoe UI", 8.25F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.txtSQLPort.Location = new System.Drawing.Point(230, 40);
            this.txtSQLPort.Name = "txtSQLPort";
            this.txtSQLPort.Size = new System.Drawing.Size(90, 22);
            this.txtSQLPort.TabIndex = 31;
            // 
            // groupOdoo
            // 
            this.groupOdoo.BackColor = System.Drawing.SystemColors.GradientActiveCaption;
            this.groupOdoo.Controls.Add(this.lblOdooUrl);
            this.groupOdoo.Controls.Add(this.lblOdooDb);
            this.groupOdoo.Controls.Add(this.lblOdooUser);
            this.groupOdoo.Controls.Add(this.txtOdooCompany);
            this.groupOdoo.Controls.Add(this.lblOdooPass);
            this.groupOdoo.Controls.Add(this.txtOdooPass);
            this.groupOdoo.Controls.Add(this.lblOdooCompany);
            this.groupOdoo.Controls.Add(this.txtOdooUser);
            this.groupOdoo.Controls.Add(this.txtOdooUrl);
            this.groupOdoo.Controls.Add(this.txtOdooDb);
            this.groupOdoo.ForeColor = System.Drawing.SystemColors.ControlDarkDark;
            this.groupOdoo.Location = new System.Drawing.Point(349, 115);
            this.groupOdoo.Name = "groupOdoo";
            this.groupOdoo.RightToLeft = System.Windows.Forms.RightToLeft.Yes;
            this.groupOdoo.Size = new System.Drawing.Size(350, 150);
            this.groupOdoo.TabIndex = 43;
            this.groupOdoo.TabStop = false;
            this.groupOdoo.Text = "Parámetros de Conexion con Odoo";
            // 
            // btnRecord
            // 
            this.btnRecord.AutoSizeMode = System.Windows.Forms.AutoSizeMode.GrowAndShrink;
            this.btnRecord.BackColor = System.Drawing.SystemColors.ControlDarkDark;
            this.btnRecord.Font = new System.Drawing.Font("Segoe UI Semilight", 9.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.btnRecord.ForeColor = System.Drawing.SystemColors.ControlLightLight;
            this.btnRecord.Location = new System.Drawing.Point(479, 30);
            this.btnRecord.Name = "btnRecord";
            this.btnRecord.Size = new System.Drawing.Size(90, 60);
            this.btnRecord.TabIndex = 44;
            this.btnRecord.Text = "Grabar";
            this.btnRecord.UseVisualStyleBackColor = false;
            this.btnRecord.Click += new System.EventHandler(this.btnRecord_Click);
            // 
            // btnLoad
            // 
            this.btnLoad.AutoSizeMode = System.Windows.Forms.AutoSizeMode.GrowAndShrink;
            this.btnLoad.BackColor = System.Drawing.SystemColors.ControlDarkDark;
            this.btnLoad.Font = new System.Drawing.Font("Segoe UI Semilight", 9.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.btnLoad.ForeColor = System.Drawing.SystemColors.ControlLightLight;
            this.btnLoad.Location = new System.Drawing.Point(360, 30);
            this.btnLoad.Name = "btnLoad";
            this.btnLoad.Size = new System.Drawing.Size(90, 60);
            this.btnLoad.TabIndex = 45;
            this.btnLoad.Text = "Cargar";
            this.btnLoad.UseVisualStyleBackColor = false;
            this.btnLoad.Click += new System.EventHandler(this.btnLoad_Click);
            // 
            // WndConfig
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(712, 276);
            this.Controls.Add(this.btnLoad);
            this.Controls.Add(this.btnRecord);
            this.Controls.Add(this.groupOdoo);
            this.Controls.Add(this.groupServer);
            this.Controls.Add(this.groupPrinter);
            this.Controls.Add(this.btnClose);
            this.Name = "WndConfig";
            this.Text = "WndConfig";
            this.groupPrinter.ResumeLayout(false);
            this.groupPrinter.PerformLayout();
            this.groupServer.ResumeLayout(false);
            this.groupServer.PerformLayout();
            this.groupOdoo.ResumeLayout(false);
            this.groupOdoo.PerformLayout();
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.Button btnClose;
        private System.Windows.Forms.Label lblPortComm;
        private System.Windows.Forms.TextBox txtPrinterSerial;
        private System.Windows.Forms.Label lblPrinterSerial;
        private System.Windows.Forms.TextBox txtCompanyVAT;
        private System.Windows.Forms.Label lblCompanyVAT;
        private System.Windows.Forms.Label lblSqlServer;
        private System.Windows.Forms.TextBox txtSQLServer;
        private System.Windows.Forms.Label lblSQLPort;
        private System.Windows.Forms.Label lblSQLDataBase;
        private System.Windows.Forms.TextBox txtSQLDataBase;
        private System.Windows.Forms.Label lblSQLUser;
        private System.Windows.Forms.TextBox txtSQLUser;
        private System.Windows.Forms.Label lblSQLPassword;
        private System.Windows.Forms.TextBox txtSQLPassword;
        private System.Windows.Forms.Label lblOdooUrl;
        private System.Windows.Forms.TextBox txtOdooUrl;
        private System.Windows.Forms.Label lblOdooDb;
        private System.Windows.Forms.TextBox txtOdooDb;
        private System.Windows.Forms.Label lblOdooUser;
        private System.Windows.Forms.TextBox txtOdooUser;
        private System.Windows.Forms.Label lblOdooPass;
        private System.Windows.Forms.TextBox txtOdooPass;
        private System.Windows.Forms.Label lblOdooCompany;
        private System.Windows.Forms.TextBox txtOdooCompany;
        private System.Windows.Forms.GroupBox groupPrinter;
        private System.Windows.Forms.GroupBox groupServer;
        private System.Windows.Forms.GroupBox groupOdoo;
        private System.Windows.Forms.Button btnRecord;
        private System.Windows.Forms.Button btnLoad;
        private System.Windows.Forms.TextBox txtPortComm;
        private System.Windows.Forms.TextBox txtSQLPort;
    }
}