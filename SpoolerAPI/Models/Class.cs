using Serilog;

namespace SpoolerAPI.Models
{
    internal class Class
    {
        public  bool DBG { get; set; } = true;
        private bool INF { get; set; } = true;
        private bool WRN { get; set; } = true;
        private bool ERR { get; set; } = true;
        private bool FTL { get; set; } = true;

        public void Dbg(string message) { if (DBG) { Log.Debug(message); } }
        public void Inf(string message) { if (INF) { Log.Information(message); } }
        public void Wrn(string message) { if (WRN) { Log.Warning(message); } }
        public void Err(string message) { if (ERR) { Log.Error(message); } }
        public void Ftl(string message) { if (FTL) { Log.Fatal(message); } }
    }

    public class AppSettings
    {
        public ServerSetting ServerSetting { get; set; }
        public PrinterSetting PrinterSetting { get; set; }
        public UserSetting UserSetting { get; set; }
    }

    public class ServerSetting
    {
        public string ServerIp { get; set; }
        public int ServerPort { get; set; }
    }

    public class PrinterSetting
    {
        public string PrinterName { get; set; }
        public string PrinterPort { get; set; }
    }

    public class UserSetting
    {
        public bool MinimizeConsole { get; set; }
        public bool OpenBrowser { get; set; }
    }

    public class ReportResult
    {
        public bool Success { get; set; }
        public string Message { get; set; }
    }

    public class Information
    {
        public string InfoSerial { get; set; }
        public string InfoRif { get; set; }
        public int InfoLastInvoice { get; set; }
        public int InfoLastCredit { get; set; }
    }
}
