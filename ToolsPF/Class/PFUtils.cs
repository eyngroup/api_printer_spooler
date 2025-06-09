using Npgsql;
using System;
using System.Linq;
using System.Data;
using System.Windows.Forms;
using System.Xml.Linq;

namespace ToolsPF.Class
{
    public class PFUtils
    {
        private readonly static NpgsqlConnection oConn; //Objeto para Conexion
        private static NpgsqlCommand oCmd; //Objeto para Comandos
        private static string cConexString = LoadSettings(); //Load port to settings.xml
                                                             //private static string cConexString = "server= 'localhost'; port='5432'; " +
                                                             //"database='database_empresa'; user id='odoo'; password='odoo'; commandtimeout=900";


        static PFUtils()
        {
            oConn = new NpgsqlConnection(cConexString);
        }
        private static string LoadSettings()
        {
            try
            {
                XElement xmlSettings = XElement.Load("Settings.xml");
                var cPSerial =
                    (from c in xmlSettings.Descendants("Settings")
                     select c.Element("PrinterSerial").Value).FirstOrDefault();
                if (cPSerial != null)
                    cPSerial = cPSerial.ToString();
                var cServer =
                    (from c in xmlSettings.Descendants("PostgreSQL")
                     select c.Element("PostgresqlServer").Value).FirstOrDefault();
                if (cServer != null)
                    cServer = cServer.ToString();
                var cPort =
                    (from c in xmlSettings.Descendants("PostgreSQL")
                     select c.Element("PostgresqlPort").Value).FirstOrDefault();
                if (cPort != null)
                    cPort = cPort.ToString();
                var cData =
                    (from c in xmlSettings.Descendants("PostgreSQL")
                     select c.Element("PostgresqlDataBase").Value).FirstOrDefault();
                if (cData != null)
                    cData = cData.ToString();
                var cUser =
                  (from c in xmlSettings.Descendants("PostgreSQL")
                   select c.Element("PostgresqlUser").Value).FirstOrDefault();
                if (cUser != null)
                    cUser = cUser.ToString();
                var cPass =
                    (from c in xmlSettings.Descendants("PostgreSQL")
                     select c.Element("PostgresqlPassword").Value).FirstOrDefault();
                if (cPass != null)
                    cPass = cPass.ToString();
                string cConexString = "server=" + cServer + "; port=" + cPort + "; database=" + cData +
                    "; user id=" + cUser + "; password=" + cPass + "; commandtimeout=900";
                return cConexString;
            }
            catch (Exception e)
            {
                MessageBox.Show(e.Message);
            }
            return cConexString;
        }
        public static DataTable GetDataTable(string cQuery)
        {
            DataTable oDataGrid = new DataTable();
            try
            {
                oCmd = new NpgsqlCommand();
                oCmd.Connection = oConn; //Inicializar la Conexion
                oCmd.CommandText = cQuery; //Inicializar el Comando
                oConn.Open();
                NpgsqlDataReader oDataReader = oCmd.ExecuteReader(); //Ejecutar el Comando
                oDataGrid.Load(oDataReader); //Agrega los datos consultados al dataset

                oConn.Close();
                return oDataGrid;
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
            }
            
            return oDataGrid;
        }

        public void Update(string cUpdate)
        {
            try
            {
                NpgsqlCommand oProcesar = new NpgsqlCommand(cUpdate, oConn);
                oConn.Open();
                oProcesar.ExecuteNonQuery();
                oConn.Close();
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
            }

        }

        //public static DataTable GetData(string cQuery)
        //{
        //    DataTable oDataGrid = new DataTable();
        //    try
        //    {
        //        //MessageBox.Show(cConexString);
        //        //oConn = new NpgsqlConnection(cConexString);
        //        //oConn.Open();
        //        //NpgsqlDataAdapter oDataAdapter = new NpgsqlDataAdapter(cQuery, oConn);
        //        //oDataAdapter.Fill(oDataSet);
        //        //oConn.Close();
        //        NpgsqlDataAdapter oDataAdapter = new NpgsqlDataAdapter(cQuery, oConn); //Almacena los datos consultados
        //        oDataAdapter.Fill(oDataGrid); //Agrega los datos consultados al dataset
        //        oConn.Close();
        //        return oDataGrid;
        //    }
        //    catch (System.InvalidOperationException e)
        //    {
        //        MessageBox.Show(e.Message);
        //    }
        //    catch (System.NullReferenceException e)
        //    {
        //        MessageBox.Show(e.Message);
        //    }
        //    catch (Exception e)
        //    {
        //        MessageBox.Show(e.Message);
        //    }
        //    return oDataGrid;
        //}



    }
}
