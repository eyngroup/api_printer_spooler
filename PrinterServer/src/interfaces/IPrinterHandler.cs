using System.Threading.Tasks;
using System.Collections.Generic;
using Newtonsoft.Json.Linq;

namespace ApiPrinterServer.Interfaces
{
    public interface IPrinterHandler
    {
        Task<bool> Initialize(JObject config);
        Task<JObject> ProcessDocument(JObject document);
        Task<JObject> ProcessRequest(string method, Dictionary<string, string> parameters);
        Task<JObject> CheckStatus();
        Task Shutdown();
    }
}
