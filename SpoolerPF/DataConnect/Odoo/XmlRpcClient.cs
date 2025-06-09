using CookComputing.XmlRpc;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SpoolerPF.DataConnect.Odoo
{
    public interface IOdooCommon : IXmlRpcProxy
    {
        [XmlRpcMethod("login")]
        int Login(string dbName, string dbUser, string dbPwrd);

        [XmlRpcMethod("logout")]
        int Logout(string dbName, string dbUser, string dbPwrd);

    }

    public interface IOdooObject : IXmlRpcProxy
    {
        [XmlRpcMethod("execute")]
        int[] search(string dbName, int userId, string pwd, string model, string method, object[] where);

        [XmlRpcMethod("execute")]
        object[] read(string dbName, int userId, string pwd, string model, string method, int[] ids, string[] fieldNames);

        [XmlRpcMethod("execute")]
        object[] search_read(string dbName, int userId, string pwd, string model, string method, object[] where, string[] fieldNames);

        [XmlRpcMethod("execute")]
        int search_count(string dbName, int userId, string pwd, string model, string method, object[] where);

        [XmlRpcMethod("execute")]
        int create(string dbName, int userId, string pwd, string model, string method, XmlRpcStruct fieldValues);

        [XmlRpcMethod("execute")]
        bool write(string dbName, int userId, string pwd, string model, string method, int[] ids, XmlRpcStruct fieldValues);

        [XmlRpcMethod("execute")]
        bool unlink(string dbName, int userId, string pwd, string model, string method, int[] ids);

        [XmlRpcMethod("execute")]
        object execute(string dbName, int userId, string pwd, string model, string method, int[] ids);

        [XmlRpcMethod("execute")]
        bool action_produce(string dbName, int userId, string pwd, string model, string method, int id, double qty, string consumeMethod);

        [XmlRpcMethod("execute")]
        void message_post(string dbName, int userId, string pwd, string model, string method, int[] ids, string message);

    }

    public interface Ixmlrpcconnect : IOdooCommon, IOdooObject
    {
    }

    public class XmlRpcClient : Ixmlrpcconnect
    {
        Ixmlrpcconnect rpcclient = XmlRpcProxyGen.Create<Ixmlrpcconnect>();
        public XmlRpcClient(string ServiceUrl)
        {
            rpcclient.Url = ServiceUrl;
        }

        public int Login(string dbname, string username, string pwd)
        {
            try
            {
                return rpcclient.Login(dbname, username, pwd);
            }
            catch (Exception)
            {
                return 0;
            }

        }

        public int Logout(string dbname, string username, string pwd)
        {
            return rpcclient.Logout(dbname, username, pwd);
        }

        public int[] search(string dbName, int userId, string pwd, string model, string method, object[] filters)
        {
            return rpcclient.search(dbName, userId, pwd, model, method, filters);
        }

        public object[] read(string dbName, int userId, string pwd, string model, string method, int[] ids, string[] fieldNames)
        {
            return rpcclient.read(dbName, userId, pwd, model, method, ids, fieldNames);
        }

        public object[] search_read(string dbName, int userId, string pwd, string model, string method, object[] where, string[] fieldNames)
        {
            return rpcclient.search_read(dbName, userId, pwd, model, method, where, fieldNames);
        }

        public int search_count(string dbName, int userId, string pwd, string model, string method, object[] filters)
        {
            return rpcclient.search_count(dbName, userId, pwd, model, method, filters);
        }

        public int create(string dbName, int userId, string pwd, string model, string method, XmlRpcStruct fieldValues)
        {
            return rpcclient.create(dbName, userId, pwd, model, method, fieldValues);
        }

        public bool write(string dbName, int userId, string pwd, string model, string method, int[] ids, XmlRpcStruct fieldValues)
        {
            return rpcclient.write(dbName, userId, pwd, model, method, ids, fieldValues);
        }

        public bool unlink(string dbName, int userId, string pwd, string model, string method, int[] ids)
        {
            return rpcclient.unlink(dbName, userId, pwd, model, method, ids);
        }

        public object execute(string dbName, int userId, string pwd, string model, string method, int[] ids)
        {
            return rpcclient.execute(dbName, userId, pwd, model, method, ids);
        }

        public bool action_produce(string dbName, int userId, string pwd, string model, string method, int id, double qty, string consumeMethod)
        {
            return rpcclient.action_produce(dbName, userId, pwd, model, method, id, qty, consumeMethod);
        }

        public void message_post(string dbName, int userId, string pwd, string model, string method, int[] ids, string message)
        {
            Console.WriteLine(method + " " + ids.ToString() + " " + message);
            Console.ReadLine();
            rpcclient.message_post(dbName, userId, pwd, model, method, ids, message);
        }

        #region NotImplemanted

        public bool AllowAutoRedirect
        {
            get
            {
                throw new NotImplementedException();
            }
            set
            {
                throw new NotImplementedException();
            }
        }

        public System.Security.Cryptography.X509Certificates.X509CertificateCollection ClientCertificates
        {
            get { throw new NotImplementedException(); }
        }

        public string ConnectionGroupName
        {
            get
            {
                throw new NotImplementedException();
            }
            set
            {
                throw new NotImplementedException();
            }
        }

        public System.Net.CookieContainer CookieContainer
        {
            get { throw new NotImplementedException(); }
        }

        public System.Net.ICredentials Credentials
        {
            get
            {
                throw new NotImplementedException();
            }
            set
            {
                throw new NotImplementedException();
            }
        }

        public bool EnableCompression
        {
            get
            {
                throw new NotImplementedException();
            }
            set
            {
                throw new NotImplementedException();
            }
        }

        public bool Expect100Continue
        {
            get
            {
                throw new NotImplementedException();
            }
            set
            {
                throw new NotImplementedException();
            }
        }

        public System.Net.WebHeaderCollection Headers
        {
            get { throw new NotImplementedException(); }
        }

        public Guid Id
        {
            get { throw new NotImplementedException(); }
        }

        public int Indentation
        {
            get
            {
                throw new NotImplementedException();
            }
            set
            {
                throw new NotImplementedException();
            }
        }

        public bool KeepAlive
        {
            get
            {
                throw new NotImplementedException();
            }
            set
            {
                throw new NotImplementedException();
            }
        }

        public XmlRpcNonStandard NonStandard
        {
            get
            {
                throw new NotImplementedException();
            }
            set
            {
                throw new NotImplementedException();
            }
        }

        public bool PreAuthenticate
        {
            get
            {
                throw new NotImplementedException();
            }
            set
            {
                throw new NotImplementedException();
            }
        }

        public Version ProtocolVersion
        {
            get
            {
                throw new NotImplementedException();
            }
            set
            {
                throw new NotImplementedException();
            }
        }

        public System.Net.IWebProxy Proxy
        {
            get
            {
                throw new NotImplementedException();
            }
            set
            {
                throw new NotImplementedException();
            }
        }

        public System.Net.CookieCollection ResponseCookies
        {
            get { throw new NotImplementedException(); }
        }

        public System.Net.WebHeaderCollection ResponseHeaders
        {
            get { throw new NotImplementedException(); }
        }

        public int Timeout
        {
            get
            {
                throw new NotImplementedException();
            }
            set
            {
                throw new NotImplementedException();
            }
        }

        public string Url
        {
            get
            {
                throw new NotImplementedException();
            }
            set
            {
                throw new NotImplementedException();
            }
        }

        public bool UseEmptyParamsTag
        {
            get
            {
                throw new NotImplementedException();
            }
            set
            {
                throw new NotImplementedException();
            }
        }

        public bool UseIndentation
        {
            get
            {
                throw new NotImplementedException();
            }
            set
            {
                throw new NotImplementedException();
            }
        }

        public bool UseIntTag
        {
            get
            {
                throw new NotImplementedException();
            }
            set
            {
                throw new NotImplementedException();
            }
        }

        public bool UseStringTag
        {
            get
            {
                throw new NotImplementedException();
            }
            set
            {
                throw new NotImplementedException();
            }
        }

        public string UserAgent
        {
            get
            {
                throw new NotImplementedException();
            }
            set
            {
                throw new NotImplementedException();
            }
        }

        public Encoding XmlEncoding
        {
            get
            {
                throw new NotImplementedException();
            }
            set
            {
                throw new NotImplementedException();
            }
        }

        public string XmlRpcMethod
        {
            get
            {
                throw new NotImplementedException();
            }
            set
            {
                throw new NotImplementedException();
            }
        }

        public bool UseNagleAlgorithm { get => throw new NotImplementedException(); set => throw new NotImplementedException(); }

        public bool UseEmptyElementTags { get => throw new NotImplementedException(); set => throw new NotImplementedException(); }

        public string[] SystemListMethods()
        {
            throw new NotImplementedException();
        }

        public object[] SystemMethodSignature(string MethodName)
        {
            throw new NotImplementedException();
        }

        public string SystemMethodHelp(string MethodName)
        {
            throw new NotImplementedException();
        }

        public void AttachLogger(XmlRpcLogger logger)
        {
            throw new NotImplementedException();
        }

        public event XmlRpcRequestEventHandler RequestEvent;

        public event XmlRpcResponseEventHandler ResponseEvent;

        #endregion

    }
}
