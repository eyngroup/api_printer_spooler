namespace SpoolerPF.Main
{
    partial class WndDataCheck
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
            this.BtnClose = new System.Windows.Forms.Button();
            this.BtnGetData = new System.Windows.Forms.Button();
            this.DataGridView = new System.Windows.Forms.DataGridView();
            this.BtnGetStruct = new System.Windows.Forms.Button();
            ((System.ComponentModel.ISupportInitialize)(this.DataGridView)).BeginInit();
            this.SuspendLayout();
            // 
            // btnClose
            // 
            this.BtnClose.AutoSizeMode = System.Windows.Forms.AutoSizeMode.GrowAndShrink;
            this.BtnClose.BackColor = System.Drawing.SystemColors.ControlDarkDark;
            this.BtnClose.Font = new System.Drawing.Font("Segoe UI Semilight", 9.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.BtnClose.ForeColor = System.Drawing.SystemColors.ControlLightLight;
            this.BtnClose.Location = new System.Drawing.Point(618, 357);
            this.BtnClose.Name = "btnClose";
            this.BtnClose.Size = new System.Drawing.Size(90, 60);
            this.BtnClose.TabIndex = 12;
            this.BtnClose.Text = "Cerrar";
            this.BtnClose.UseVisualStyleBackColor = false;
            this.BtnClose.Click += new System.EventHandler(this.BtnClose_Click);
            // 
            // BtnGetData
            // 
            this.BtnGetData.AutoSizeMode = System.Windows.Forms.AutoSizeMode.GrowAndShrink;
            this.BtnGetData.BackColor = System.Drawing.SystemColors.ControlDarkDark;
            this.BtnGetData.Font = new System.Drawing.Font("Segoe UI Semilight", 9.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.BtnGetData.ForeColor = System.Drawing.SystemColors.ControlLightLight;
            this.BtnGetData.Location = new System.Drawing.Point(21, 357);
            this.BtnGetData.Name = "BtnGetData";
            this.BtnGetData.Size = new System.Drawing.Size(90, 60);
            this.BtnGetData.TabIndex = 13;
            this.BtnGetData.Text = "Obtener Datos";
            this.BtnGetData.UseVisualStyleBackColor = false;
            this.BtnGetData.Click += new System.EventHandler(this.BtnGetData_Click);
            // 
            // DataGridView
            // 
            this.DataGridView.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.DataGridView.Location = new System.Drawing.Point(12, 12);
            this.DataGridView.Name = "DataGridView";
            this.DataGridView.Size = new System.Drawing.Size(696, 328);
            this.DataGridView.TabIndex = 14;
            // 
            // BtnGetStruct
            // 
            this.BtnGetStruct.AutoSizeMode = System.Windows.Forms.AutoSizeMode.GrowAndShrink;
            this.BtnGetStruct.BackColor = System.Drawing.SystemColors.ControlDarkDark;
            this.BtnGetStruct.Font = new System.Drawing.Font("Segoe UI Semilight", 9.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.BtnGetStruct.ForeColor = System.Drawing.SystemColors.ControlLightLight;
            this.BtnGetStruct.Location = new System.Drawing.Point(142, 357);
            this.BtnGetStruct.Name = "BtnGetStruct";
            this.BtnGetStruct.Size = new System.Drawing.Size(90, 60);
            this.BtnGetStruct.TabIndex = 15;
            this.BtnGetStruct.Text = "Obtener Estructura";
            this.BtnGetStruct.UseVisualStyleBackColor = false;
            this.BtnGetStruct.Click += new System.EventHandler(this.BtnGetStruct_Click);
            // 
            // WndMonitor
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(718, 421);
            this.Controls.Add(this.BtnGetStruct);
            this.Controls.Add(this.DataGridView);
            this.Controls.Add(this.BtnGetData);
            this.Controls.Add(this.BtnClose);
            this.Name = "WndMonitor";
            this.Text = "Monitor Data";
            ((System.ComponentModel.ISupportInitialize)(this.DataGridView)).EndInit();
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.Button BtnClose;
        private System.Windows.Forms.Button BtnGetData;
        private System.Windows.Forms.DataGridView DataGridView;
        private System.Windows.Forms.Button BtnGetStruct;
    }
}