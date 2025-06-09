using System.Web.Http;

namespace ApiServer.Controllers
{
    public class TestController : ApiController
    {
        [HttpGet]
        public IHttpActionResult Get()
        {
            return Ok(new { message = "API Server funcionando correctamente" });
        }
    }
}
