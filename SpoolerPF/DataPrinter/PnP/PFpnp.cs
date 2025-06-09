using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading.Tasks;

namespace SpoolerPF.DataPrinter.PnP
{
    /// <summary>
    /// Classe con la declaración de las funciones PNPDLL.dll
    /// </summary>
    public class PFpnp
    {
        private const string LibraryDLL = "Drivers/PnP/pnpdlltest.dll";
        public static string IFErrorInfo;


        public PFpnp()
        {
        }
        #region DECLARACIÓN DE LAS FUNCIONES de PNPDLL.DLL
        [DllImport("LibraryDLL")] public static extern string PFAbreNF();
        [DllImport("LibraryDLL")] public static extern string PFabrefiscal(String Razon, String RIF);
        [DllImport("LibraryDLL")] public static extern string PFComando(String comando);
        [DllImport("LibraryDLL")] public static extern string PFtotal();
        [DllImport("LibraryDLL")] public static extern string PFrepz();
        [DllImport("LibraryDLL")] public static extern string PFrepx();
        [DllImport("LibraryDLL")]
        public static extern string PFrenglon(String Descripcion, String
        cantidad, String monto, String iva);
        [DllImport("LibraryDLL")] public static extern string PFabrepuerto(String numero);
        [DllImport("LibraryDLL")] public static extern string PFcierrapuerto();
        [DllImport("LibraryDLL")] public static extern string PFDisplay950(String edlinea);
        [DllImport("LibraryDLL")] public static extern string PFLineaNF(String edlinea);
        [DllImport("LibraryDLL")] public static extern string PFCierraNF();
        [DllImport("LibraryDLL")] public static extern string PFCortar();
        [DllImport("LibraryDLL")] public static extern string PFTfiscal(String edlinea);
        [DllImport("LibraryDLL")] public static extern string PFparcial();
        [DllImport("LibraryDLL")] public static extern string PFSerial();
        [DllImport("LibraryDLL")] public static extern string PFtoteconomico();
        [DllImport("LibraryDLL")]
        public static extern string PFCancelaDoc(String edlinea, String
        monto);
        [DllImport("LibraryDLL")] public static extern string PFGaveta();
        [DllImport("LibraryDLL")]
        public static extern string PFDevolucion(String razon, String rif,
        String comp, String maqui, String fecha, String hora);
        [DllImport("LibraryDLL")] public static extern string PFSlipON();
        [DllImport("LibraryDLL")] public static extern string PFSLIPOFF();
        [DllImport("LibraryDLL")] public static extern string PFestatus(String edlinea);
        [DllImport("LibraryDLL")] public static extern string PFreset();
        [DllImport("LibraryDLL")]
        public static extern string PFendoso(String campo1, String campo2,
        String campo3, String tipoendoso);
        [DllImport("LibraryDLL")]
        public static extern string PFvalida675(String campo1, String
        campo2, String campo3, String campo4);
        [DllImport("LibraryDLL")]
        public static extern string PFCheque2(String mon, String ben, String
        fec, String c1, String c2, String c3, String c4, String campo1, String campo2);
        [DllImport("LibraryDLL")]
        public static extern string PFcambiofecha(String edfecha, String
        edhora);
        [DllImport("LibraryDLL")]
        public static extern string PFcambiatasa(String t1, String t2, String
        t3);
        [DllImport("LibraryDLL")] public static extern string PFBarra(String edbarra);
        [DllImport("LibraryDLL")] public static extern string PFVoltea();
        [DllImport("LibraryDLL")] public static extern string PFLeereloj();
        [DllImport("LibraryDLL")]
        public static extern string PFrepMemNF(String desf, String hasf,
        String modmem);
        [DllImport("LibraryDLL")]
        public static extern string PFRepMemoriaNumero(String desn, String
        hasn, String modmem);
        [DllImport("LibraryDLL")] public static extern string PFCambtipoContrib(String tip);
        [DllImport("LibraryDLL")] public static extern string PFultimo();
        [DllImport("LibraryDLL")] public static extern string PFTipoImp(String edtexto);
        #endregion

        public static bool IFAbrirPuerto(string cPort)
        {
            string resp = PFabrepuerto(cPort);
            bool ok = Respuesta(resp);
            return ok;
        }

        public static bool IFCerrarPuerto()
        {
            string resp = PFcierrapuerto();
            bool ok = Respuesta(resp);
            return ok;
        }

        private static bool Respuesta(string resp)
        {
            bool ok = true;

            switch (resp)
            {
                case "ER":
                    IFErrorInfo = "Existe un error";
                    ok = false;
                    break;
                case "NP":
                    IFErrorInfo = "Puerto no abierto";
                    ok = false;
                    break;
                case "TO":
                    IFErrorInfo = "Se excedió el tiempo de respuesta esperado del equipo";
                    ok = false;
                    break;
                default:
                    IFErrorInfo = "OK";
                    break;
            }

            return ok;
        }
    }
}
