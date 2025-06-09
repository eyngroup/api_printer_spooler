using System.Threading.Tasks;
using System.Collections.Generic;
using Newtonsoft.Json.Linq;

namespace ApiPrinterServer.Interfaces
{
    public interface IHandler
    {
        Task<JObject> ProcessRequest(string method, Dictionary<string, string> parameters);
    }
}
