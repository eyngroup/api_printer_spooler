using CookComputing.XmlRpc;
using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SpoolerPF.DataConnect.Odoo
{
    public class ServiceUrl : Attribute
    {
        string _url;

        public ServiceUrl(string url) { _url = url; }

        public string SvrUrl { get { return _url; } }

        public override string ToString() { return _url; }

    }

    public enum OdooXmlRpc
    {
        [ServiceUrl("/xmlrpc/object")]
        Object = 1,
        [ServiceUrl("/xmlrpc/db")]
        DB = 2,
        [ServiceUrl("/xmlrpc/common")]
        Common = 3

    }

    public class OdooConnect
    {
        int userId;
        string svrUrl;
        string dbName;
        string dbUser;
        string dbPass;
        XmlRpcClient rpcclient;

        /// <summary>
        /// Obtendrá y establecerá el valor del id de usuario.
        /// </summary>
        public int GetUserId { get { return userId; } set { userId = value; } }

        /// <summary>
        /// Obtendrá y establecerá el valor del url del servidor.
        /// </summary>
        public string GetSvrUrl { get { return svrUrl; } set { svrUrl = value; } }

        /// <summary>
        /// Obtendrá y establecerá el valor del nombre de la base de datos.
        /// </summary>
        public string GetDbName { get { return dbName; } set { dbName = value; } }

        /// <summary>
        /// Obtendrá y establecerá el valor del nombre de usuario.
        /// </summary>
        public string GetDbUser { get { return dbUser; } set { dbUser = value; } }

        /// <summary>
        /// Obtendrá y establecerá el valor de la contraseña.
        /// </summary>
        public string GetDbPass { get { return dbPass; } set { dbPass = value; } }

        /// <summary>
        /// Comprobará si se ha iniciado sesión con éxito en Odoo o no.
        /// </summary>
        public bool IsLoggedIn { get { if (userId > 0) { return true; } return false; } }

        /// <summary>
        /// Constructor para conectarse al servidor
        /// </summary>
        /// <param name="svrUrl">url del servidor y el puerto.</param>
        /// <param name="dbName">base de datos.</param>
        /// <param name="dbUser">usuario de inicio de sesión.</param>
        /// <param name="dbPass">contraseña de inicio de sesión.</param>
        public OdooConnect(string svrUrl, string dbName, string dbUser, string dbPass)
        {
            this.svrUrl = svrUrl;
            this.dbName = dbName;
            this.dbUser = dbUser;
            this.dbPass = dbPass;
        }

        /// <summary>
        /// Abrir rpcclient por servicio.
        /// </summary>
        /// <param name="service_url">servicio del svrUrl</param>
        void Open(string service_url)
        {
            rpcclient = new XmlRpcClient(svrUrl + service_url);

        }

        void Open(Enum service)
        {
            string url = null;
            Type type = service.GetType();

            ServiceUrl[] _urls =
               type.GetField(service.ToString()).GetCustomAttributes(typeof(ServiceUrl),
                                       false) as ServiceUrl[];
            if (_urls.Length > 0)
            {
                url = _urls[0].SvrUrl;
            }

            Open(url);

        }

        /// <summary>
        /// Cerrar rpcclient.
        /// </summary>
        void Close()
        {
            rpcclient = null;

        }

        /// <summary>
        /// Comprobará si los valores introducidos son correctos o no.
        /// </summary>
        public void Login()
        {
            Open(OdooXmlRpc.Common);
            int isLogin = rpcclient.Login(dbName, dbUser, dbPass);
            userId = 0;
            if (Convert.ToBoolean(isLogin))
            {
                userId = Convert.ToInt32(isLogin);
            }

            Close();

        }

        /// <summary>
        /// Metodo: Buscar
        /// </summary>
        /// <param name="model">nombre del modelo</param>
        /// <param name="where">condición [[campo, operador, valor],[...]]</param>
        /// <returns>int[] (identificadores encontrados)</returns>
        public int[] Search(string model, object[] where)
        {
            Open(OdooXmlRpc.Object);
            int[] ids = rpcclient.search(dbName, userId, dbPass, model, "search", where);
            Close();
            return ids;
        }

        /// <summary>
        /// Metodo: Leer
        /// </summary>
        /// <param name="model">nombre del modelo</param>
        /// <param name="ids">ids de registros de los que se pueden obtener datos</param>
        /// <param name="fields">nombres de los campos del modelo que desea leer</param>
        /// <returns>XmlRpcStruct[] (data [[("id", 1), ("name", "Test")]])</returns>
        public XmlRpcStruct[] Read(string model, int[] ids, string[] fields)
        {
            Open(OdooXmlRpc.Object);
            var data = rpcclient.read(dbName, userId, dbPass, model, "read", ids, fields);
            Close();
            ArrayList records = new ArrayList(data);
            return records.ToArray(typeof(XmlRpcStruct)) as XmlRpcStruct[];
        }

        /// <summary>
        /// Metodo: Buscar y Leer
        /// </summary>
        /// <param name="model">nombre del modelo</param>
        /// <param name="where">condición [[campo, operador, valor],[...]]</param>
        /// <param name="fields">nombres de los campos del modelo que desea leer</param>
        /// <returns>XmlRpcStruct[] (data [[("id", 1), ("name", "Test")]])</returns>
        public XmlRpcStruct[] SearchRead(string model, object[] where, string[] fields)
        {
            Open(OdooXmlRpc.Object);
            var data = rpcclient.search_read(dbName, userId, dbPass, model, "search_read", where, fields);
            Close();
            ArrayList records = new ArrayList(data);
            return records.ToArray(typeof(XmlRpcStruct)) as XmlRpcStruct[];
        }

        /// <summary>
        /// Metodo: Contar
        /// </summary>
        /// <param name="model">nombre del modelo</param>
        /// <param name="where">condición [[campo, operador, valor],[...]]</param>
        /// <returns>int (conteo total)</returns>
        public int SearchCount(string model, object[] where)
        {
            Open(OdooXmlRpc.Object);
            int qty = rpcclient.search_count(dbName, userId, dbPass, model, "search_count", where);
            Close();
            return qty;
        }

        /// <summary>
        /// Metodo: Insertar
        /// </summary>
        /// <param name="model">nombre del modelo</param>
        /// <param name="fieldValues">estructura con datos para insertar [clave, valor]</param>
        /// <returns>int (se crea nuevo id)</returns>
        public int Create(string model, XmlRpcStruct fieldValues)
        {
            Open(OdooXmlRpc.Object);
            int new_id = rpcclient.create(dbName, userId, dbPass, model, "create", fieldValues);
            Close();
            return new_id;
        }

        /// <summary>
        /// Metodo: Actualizar
        /// </summary>
        /// <param name="model">nombre del modelo</param>
        /// <param name="ids">ids de registros de los que se pueden escribir datos</param>
        /// <param name="fieldValues">estructura con datos para actualizar [clave, valor]</param>
        /// <returns>bool (Verdadero o Falso)</returns>
        public bool Write(string model, int[] ids, XmlRpcStruct fieldValues)
        {
            Open(OdooXmlRpc.Object);
            bool result = rpcclient.write(dbName, userId, dbPass, model, "write", ids, fieldValues);
            Close();
            return result;
        }

        /// <summary>
        /// Metodo: Eliminar
        /// </summary>
        /// <param name="model">nombre del modelo</param>
        /// <param name="ids">ids de registros para eliminar</param>
        /// <returns>bool (Verdadero o Falso)</returns>
        public bool Unlink(string model, int[] ids)
        {
            Open(OdooXmlRpc.Object);
            bool result = rpcclient.unlink(dbName, userId, dbPass, model, "unlink", ids);
            Close();
            return result;
        }

        /// <summary>
        /// Metodo: Ejecutar
        /// </summary>
        /// <param name="model">nombre del modelo</param>
        /// <param name="method">nombre del método a ejecutar</param>
        /// <param name="ids">ids de registros que se pueden actualizar</param>
        /// <returns>Object (depende del método)</returns>
        public object Execute(string model, string method, int[] ids)
        {
            Open(OdooXmlRpc.Object);
            object res = rpcclient.execute(dbName, userId, dbPass, model, method, ids);
            Close();
            return res;
        }

        /// <summary>
        /// Metodo: [SIN PROBAR] Mensaje POST
        /// </summary>
        /// <param name="model">nombre del modelo</param>
        /// <param name="ids">ids de registros que se pueden actualizar</param>
        /// <param name="message">mensaje para enviar</param>
        public void MessagePost(string model, int[] ids, string message)
        {
            Open(OdooXmlRpc.Object);
            rpcclient.message_post(dbName, userId, dbPass, model, "message_post", ids, message);
            Close();
        }

        /// <summary>
        /// Metodo:[SIN PROBAR] 
        /// </summary>
        /// <param name="id"></param>
        /// <param name="qty"></param>
        /// <param name="consumeMethod"></param>
        /// <returns>Object (depende del método)</returns>
        public bool ActionProduce(int id, double qty, string consumeMethod)
        {
            /* 
             * Ejecuta el método action_produce
             * :param model : _nombre del modelo donde se define el método
             * :param method : nombre del método a ejecutar
             * :param args : lista de argumentos
             * :param kwargs : lista de argumentos de diccionario
             * :return : Object (depends on method)
             */
            Open(OdooXmlRpc.Object);
            bool res = rpcclient.action_produce(dbName, userId, dbPass, "mrp.production", "action_produce", id, qty, consumeMethod);
            Close();
            return res;
        }

    }
}
