using System;
using System.Drawing;
using System.Windows.Forms;

namespace ApiPrinter
{
    partial class Form1
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
        /// 


        //private System.ComponentModel.IContainer components = null;
        private System.Windows.Forms.NotifyIcon notifyIcon1;

        private void InitializeComponent()
        {
            this.components = new System.ComponentModel.Container(); // Inicializa this.components


            this.btnStart = new System.Windows.Forms.Button();
            this.btnStop = new System.Windows.Forms.Button();
            this.txtLog = new System.Windows.Forms.RichTextBox();
            this.btnOpenUrl = new System.Windows.Forms.Button();
            this.btnOpenZ = new System.Windows.Forms.Button();
            this.btnStatus = new System.Windows.Forms.Button();
            this.SuspendLayout();
            // 
            // btnStart
            // 
            this.btnStart.AutoEllipsis = true;
            this.btnStart.AutoSize = true;
            this.btnStart.Location = new System.Drawing.Point(12, 295);
            this.btnStart.Name = "btnStart";
            this.btnStart.Size = new System.Drawing.Size(140, 90);
            this.btnStart.TabIndex = 0;
            this.btnStart.Text = "Iniciar";
            this.btnStart.UseVisualStyleBackColor = true;
            this.btnStart.Click += new System.EventHandler(this.btnStart_Click);
            // 
            // btnStop
            // 
            this.btnStop.Location = new System.Drawing.Point(496, 295);
            this.btnStop.Name = "btnStop";
            this.btnStop.Size = new System.Drawing.Size(140, 90);
            this.btnStop.TabIndex = 1;
            this.btnStop.Text = "Detener / Cerrar";
            this.btnStop.UseVisualStyleBackColor = true;
            this.btnStop.Click += new System.EventHandler(this.btnStop_Click);
            // 
            // txtLog
            // 
            this.txtLog.Location = new System.Drawing.Point(12, 12);
            this.txtLog.Name = "txtLog";
            this.txtLog.Size = new System.Drawing.Size(626, 277);
            this.txtLog.TabIndex = 2;
            this.txtLog.Text = "";
            this.txtLog.TextChanged += new System.EventHandler(this.txtLog_TextChanged);
            // 
            // btnOpenUrl
            // 
            this.btnOpenUrl.AutoEllipsis = true;
            this.btnOpenUrl.AutoSize = true;
            this.btnOpenUrl.Location = new System.Drawing.Point(160, 295);
            this.btnOpenUrl.Name = "btnOpenUrl";
            this.btnOpenUrl.Size = new System.Drawing.Size(90, 40);
            this.btnOpenUrl.TabIndex = 3;
            this.btnOpenUrl.Text = "Reporte X";
            this.btnOpenUrl.UseVisualStyleBackColor = true;
            this.btnOpenUrl.Click += new System.EventHandler(this.btnOpenUrl_Click);
            // 
            // btnOpenZ
            // 
            this.btnOpenZ.Location = new System.Drawing.Point(400, 295);
            this.btnOpenZ.Name = "btnOpenZ";
            this.btnOpenZ.Size = new System.Drawing.Size(90, 40);
            this.btnOpenZ.TabIndex = 4;
            this.btnOpenZ.Text = "Reporte Z";
            this.btnOpenZ.UseVisualStyleBackColor = true;
            this.btnOpenZ.Click += new System.EventHandler(this.btnOpenZ_Click);
            // 
            // btnStatus
            // 
            this.btnStatus.Location = new System.Drawing.Point(276, 295);
            this.btnStatus.Name = "btnStatus";
            this.btnStatus.Size = new System.Drawing.Size(90, 40);
            this.btnStatus.TabIndex = 5;
            this.btnStatus.Text = "Estado";
            this.btnStatus.UseVisualStyleBackColor = true;
            this.btnStatus.Click += new System.EventHandler(this.btnStatus_Click);
            // 
            // Form1
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(8F, 16F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(650, 400);
            this.Controls.Add(this.btnStatus);
            this.Controls.Add(this.btnOpenZ);
            this.Controls.Add(this.btnOpenUrl);
            this.Controls.Add(this.txtLog);
            this.Controls.Add(this.btnStop);
            this.Controls.Add(this.btnStart);
            this.Name = "Form1";
            this.Text = "ApiPrinter";
            this.ResumeLayout(false);
            this.PerformLayout();

            this.notifyIcon1 = new System.Windows.Forms.NotifyIcon(this.components);
            this.notifyIcon1.Icon = SystemIcons.Application; // Puedes cambiar esto por el ícono que quieras
            this.notifyIcon1.Visible = false;
            this.notifyIcon1.DoubleClick += new System.EventHandler(this.notifyIcon1_DoubleClick);

        }

        private void btnMinimize_Click(object sender, EventArgs e)
        {
            this.WindowState = FormWindowState.Minimized;
            this.ShowInTaskbar = false;
            notifyIcon1.Visible = true;
        }

        private void notifyIcon1_DoubleClick(object sender, EventArgs e)
        {
            this.WindowState = FormWindowState.Normal;
            this.ShowInTaskbar = true;
            notifyIcon1.Visible = false;
        }

        #endregion

        private System.Windows.Forms.Button btnStart;
        private System.Windows.Forms.Button btnStop;
        private System.Windows.Forms.RichTextBox txtLog;
        private System.Windows.Forms.Button btnOpenUrl;
        private System.Windows.Forms.Button btnOpenZ;
        private System.Windows.Forms.Button btnStatus;


    }
}

