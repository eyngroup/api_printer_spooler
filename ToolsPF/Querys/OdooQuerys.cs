using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace ToolsPF.Querys
{
    public class OdooQuerys
    {
        #region SELECT
        /// <summary>
        /// Consulta LIMITADA al modelo ACCOUNT_MOVE
        /// </summary>
        /// <param name="cPFSerial"></param>
        /// <param name="nLimit"></param>
        /// <returns></returns>
        public string AccountMove(string cPFSerial, int nLimit)
        {
            //string queryAccountMove = string.Format
            //        ("SELECT DOC.ID AS Id,DOC.NAME as Doc_Numero,DOC.REF as Doc_Asociado," +
            //        "DOC.MOVE_TYPE as Doc_Tipo,DOC.PF_INVOICE as PF_Invoice,DOC.PF_PRINTER as Check " +
            //        "FROM PUBLIC.ACCOUNT_MOVE AS DOC " +
            //        "INNER JOIN PUBLIC.ACCOUNT_JOURNAL AS DIARIO ON DIARIO.ID = DOC.JOURNAL_ID " +
            //        "WHERE (DOC.MOVE_TYPE = 'out_invoice' OR DOC.MOVE_TYPE = 'out_refund') AND " +
            //        "DOC.PF_SERIAL ISNULL AND DOC.PF_INVOICE ISNULL AND DIARIO.ACTIVE = true AND " +
            //        "DIARIO.TYPE = 'sale' AND DIARIO.PF_SERIAL = '{0}'  LIMIT '{1}';", cPFSerial, nLimit);

            //AutoRepuestos ATM
            string queryAccountMove = string.Format
                    ("SELECT DOC.ID AS Id,DOC.NAME as Doc_Numero,DOC.REF as Doc_Asociado," +
                    "DOC.MOVE_TYPE as Doc_Tipo,DOC.NUM_DOC_FISCAL as Doc_Invoice,DOC.IS_PRINT as Check " +
                    "FROM PUBLIC.ACCOUNT_MOVE AS DOC " +
                    "INNER JOIN PUBLIC.ACCOUNT_JOURNAL AS DIARIO ON DIARIO.ID = DOC.JOURNAL_ID " +
                    "WHERE (DOC.MOVE_TYPE = 'out_invoice' OR DOC.MOVE_TYPE = 'out_refund') AND " +
                    "DOC.IS_PRINT ISNULL AND DIARIO.ACTIVE = true AND " +
                    "DIARIO.TYPE = 'sale' AND DOC.REF IS NOT NULL AND DIARIO.SERIAL_PRINTER = '{0}'  LIMIT '{1}';", cPFSerial, nLimit);

           // MessageBox.Show(queryAccountMove);

            return queryAccountMove;
        }
        /// <summary>
        /// Consulta al modelo ACCOUNT_MOVE para datos del documento, cliente y usuario
        /// </summary>
        /// <param name="cSerial">Serial de la Impresora</param>
        /// <returns>string query</returns>
        public string AccountMove(string cRef)
        {
            /* Estrutura de Datos:
             * * COL0 tipo:string 'Numero del Documento' = Doc_Numero
             * * COL1 tipo:string 'Referencia Asociada' = Doc_Asociado
             * * COL2 tipo:string 'Tipo de Documento' = Doc_Tipo
             * * COL3 tipo:string 'Nombre del Cliente' = Cli_Nombre
             * * COL4 tipo:string 'Rif del Cliente' = Cli_Rif
             * * COL5 tipo:string 'Email del Cliente' = Cli_Email
             * * COL6 tipo:string 'Telefono del Cliente' = Cli_Telefono
             * * COL7 tipo:string 'Direccion del Cliente' = Cli_Direccion
             * * COL8 tipo:string 'Usuario Asociado' = User_Login
             * * COL9 tipo:int32 'Codigo del Usuario' = User_ID
             * * COL10 tipo:int32 'Codigo del Diario Asociado' = Journal
             * * COL11 tipo:date 'Fecha del Documento' = Doc_Fecha
             * * COL11 tipo:int32 'ID del DOCUMENTO' = UpdateID
             */
            //string queryAccountMove = string.Format
            //        ("SELECT DOC.NAME as Doc_Numero,DOC.REF as Doc_Asociado,DOC.MOVE_TYPE as Doc_Tipo," +
            //        "CLI.NAME as Cli_Nombre,CLI.VAT as Cli_Rif,CLI.EMAIL_NORMALIZED as Cli_Email," +
            //        "CLI.PHONE_SANITIZED as Cli_Telefono,CLI.CONTACT_ADDRESS_COMPLETE as Cli_Direccion," +
            //        "VEN.LOGIN as User_Login,VEN.PARTNER_ID as User_ID,DIARIO.ID Journal,DOC.DATE as Doc_Fecha,DOC.ID as UpdateID " +
            //        "FROM PUBLIC.ACCOUNT_MOVE AS DOC " +
            //        "INNER JOIN PUBLIC.ACCOUNT_JOURNAL AS DIARIO ON DIARIO.ID = DOC.JOURNAL_ID " +
            //        "INNER JOIN PUBLIC.RES_PARTNER AS CLI ON CLI.ID = DOC.PARTNER_ID " +
            //        "INNER JOIN PUBLIC.RES_USERS AS VEN ON VEN.ID = DOC.INVOICE_USER_ID " +
            //        "WHERE DOC.PF_SERIAL IS NULL AND DOC.REF = '{0}' ;", cRef);

            //Para ATM
            string queryAccountMove = string.Format
                   ("SELECT DOC.NAME as Doc_Numero,DOC.REF as Doc_Asociado,DOC.MOVE_TYPE as Doc_Tipo," +
                   "CLI.NAME as Cli_Nombre,CLI.VAT as Cli_Rif,CLI.EMAIL_NORMALIZED as Cli_Email," +
                   "CLI.PHONE_SANITIZED as Cli_Telefono,CLI.CONTACT_ADDRESS_COMPLETE as Cli_Direccion," +
                   "VEN.LOGIN as User_Login,VEN.PARTNER_ID as User_ID,DIARIO.ID Journal,DOC.DATE as Doc_Fecha,DOC.ID as UpdateID " +
                   "FROM PUBLIC.ACCOUNT_MOVE AS DOC " +
                   "INNER JOIN PUBLIC.ACCOUNT_JOURNAL AS DIARIO ON DIARIO.ID = DOC.JOURNAL_ID " +
                   "INNER JOIN PUBLIC.RES_PARTNER AS CLI ON CLI.ID = DOC.PARTNER_ID " +
                   "INNER JOIN PUBLIC.RES_USERS AS VEN ON VEN.ID = DOC.INVOICE_USER_ID " +
                   "WHERE DOC.NUM_DOC_FISCAL IS NULL AND DOC.REF = '{0}' ;", cRef);

            return queryAccountMove;
        }
        /// <summary>
        /// Consulta al modelo ACCOUNT_MOVE_LINE para obtener los datos de los movimientos del documento
        /// </summary>
        /// <param name="cReferencia">Referencia de la Operacion</param>
        /// <returns>string query</returns>
        public string AccountMoveLine(string cRef)
        {
            /* Estrutura de Datos:
             * * COL0 tipo:string 'Referencia Asociada' = Mov_Asociado
             * * COL1 tipo:string 'Nombre del Producto' = Mov_Producto
             * * COL2 tipo:decimal 'Cantidad' = Mov_Cantidad
             * * COL3 tipo:decimal 'Precio Unitario' = Mov_PrecioU
             * * COL4 tipo:decimal 'Descuento' = Mov_Descuento
             * * COL5 tipo:int32 'Codigo del Tipo de IVA' = Iva_Codigo
             * * COL6 tipo:decimal 'Porcentaje de IVA' = Iva_Porcentaje
             */
            string queryAccountMoveLine = string.Format
                    ("SELECT LIN.REF as Mov_Asociado,LIN.NAME as Mov_Producto,ROUND(LIN.QUANTITY,3) as Mov_Cantidad," +
                    "ROUND(LIN.PRICE_UNIT,2) as Mov_PrecioU,LIN.DISCOUNT as Mov_Descuento," +
                    "IVA.ACCOUNT_TAX_ID as Iva_Codigo,TAX.AMOUNT as Iva_Porcentaje " +
                    "FROM PUBLIC.ACCOUNT_MOVE_LINE AS LIN " +
                    "LEFT JOIN PUBLIC.ACCOUNT_MOVE_LINE_ACCOUNT_TAX_REL AS IVA ON IVA.ACCOUNT_MOVE_LINE_ID = LIN.ID " +
                    "LEFT JOIN PUBLIC.ACCOUNT_TAX AS TAX ON TAX.ID = IVA.account_tax_id " +
                    "WHERE LIN.EXCLUDE_FROM_INVOICE_TAB = FALSE AND LIN.REF = '{0}' ;", cRef);
            return queryAccountMoveLine;
        }
        /// <summary>
        /// Consulta al modelo POS_ORDER para obtener los datos de la forma de pago
        /// </summary>
        /// <param name="cReferencia">Referencia de la Operacion</param>
        /// <returns>string query</returns>
        public string PosOrder(string cRef)
        {
            /* Estrutura de Datos:
            * * COL0 tipo:string 'Referencia Asociada' = Pag_Asociado
            * * COL1 tipo:decimal 'Tasa de Cambio' = Pag_Tasa
            * * COL2 tipo:string 'Referencia del Pago' = Pag_Referencia
            * * COL3 tipo:decimal 'Monto Pagado' = Pag_Monto
            * * COL4 tipo:bool 'Es un Cambio' = Pag_Cambio
            * * COL5 tipo:int32 'Codigo de la Forma de Pago' = Pag_ID
            * * COL6 tipo:decimal 'Nombre de la Forma de Pago' = Pag_Forma
            */
            string queryPosOrder = string.Format
                    ("SELECT POS.NAME as Pag_Asociado,POS.CURRENCY_RATE as Pag_Tasa," +
                    "PAY.NAME as Pag_Referencia,ROUND(PAY.AMOUNT,2) as Pag_Monto," +
                    "PAY.IS_CHANGE as Pag_Cambio,FORMA.ID as Pag_ID,FORMA.NAME as Pag_Forma " +
                    "FROM PUBLIC.POS_ORDER AS POS " +
                    "INNER JOIN PUBLIC.POS_PAYMENT AS PAY ON PAY.POS_ORDER_ID = POS.ID " +
                    "INNER JOIN POS_PAYMENT_METHOD AS FORMA ON FORMA.ID = PAY.PAYMENT_METHOD_ID " +
                    "WHERE POS.STATE = 'invoiced' AND POS.TO_INVOICE = TRUE AND FORMA.ACTIVE = true " +
                    "AND POS.NAME = '{0}' ;", cRef);
            return queryPosOrder;
        }
        #endregion
        #region UPDATE
        public string UpdateAccountMove(string cSerial,string cInvoice, int nID)
        {

            if (string.IsNullOrEmpty(cSerial) || string.IsNullOrEmpty(cInvoice) || nID == 0)
            {
                return string.Empty;
            }

            //string queryUpdate = string.Format
            //        ("UPDATE PUBLIC.ACCOUNT_MOVE SET PF_SERIAL = '{0}',PF_INVOICE = '{1}' " +
            //        "WHERE ID= '{2}' ;", cSerial, cInvoice, nID);

            //Para ATM
            string queryUpdate = string.Format
                   ("UPDATE PUBLIC.ACCOUNT_MOVE SET NUM_DOC_FISCAL = '{0}',IS_PRINT = '{1}' " +
                   "WHERE ID= '{2}' ;", cInvoice, true, nID);

            //UPDATE "public"."account_move"
            //SET "PF_SERIAL" = 'Z1B1234567', "is_print" = 'true' WHERE  "id" = 15;
            return queryUpdate;
        }
        #endregion
    }
}
