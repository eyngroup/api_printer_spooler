using Npgsql;
using System;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Xml.Linq;

namespace SpoolerPF.DataSQL.Pgsql
{
    public class PFpgsql
    {
        public string cPFinfo;
        private readonly static NpgsqlConnection oConn;
        private static NpgsqlCommand oCmd;

        static PFpgsql()
        {
            string cPSerial = SpoolerPF.DataConfig.PFconfig.cPrinterSerial;
            string pgServer = SpoolerPF.DataConfig.PFconfig.cSQLServer;
            string pgPort = SpoolerPF.DataConfig.PFconfig.cSQLPort;
            string pgDataBase = SpoolerPF.DataConfig.PFconfig.cSQLDataBase;
            string pgUser = SpoolerPF.DataConfig.PFconfig.cSQLUser;
            string pgPassword = SpoolerPF.DataConfig.PFconfig.cSQLPassword;

            string cConexString = "server=" + pgServer + "; port=" + pgPort + "; database=" + 
                pgDataBase + "; user id=" + pgUser + "; password=" + pgPassword + "; commandtimeout=900";

            oConn = new NpgsqlConnection(cConexString);
        }

        public DataTable GetDataTable(string cQuery)
        {
            DataTable oDataGrid = new DataTable();
            try
            {
                oCmd = new NpgsqlCommand();
                oCmd.Connection = oConn;                                //Inicializar la Conexion
                oCmd.CommandText = cQuery;                              //Inicializar el Comando
                oConn.Open();
                NpgsqlDataReader oDataReader = oCmd.ExecuteReader();    //Ejecutar el Comando
                oDataGrid.Load(oDataReader);                            //Agrega los datos consultados al dataset

                oConn.Close();
                return oDataGrid;
            }
            catch (Exception ex)
            {
                _ = (ex.Message);
            }
            return oDataGrid;
        }

        public bool SqlUpdate(string cUpdate)
        {
            try
            {
                NpgsqlCommand oProcesar = new NpgsqlCommand(cUpdate, oConn);
                oConn.Open();
                oProcesar.ExecuteNonQuery();
                oConn.Close();
                return true;
            }
            catch (Exception ex)
            {
                cPFinfo = (ex.Message);
            }
            return false;
        }

    }
}
