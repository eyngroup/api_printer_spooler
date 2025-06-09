using SpoolerAPI.Models;
using SpoolerAPI.PrinterComm;

namespace SpoolerAPI
{
    public class DeviceValidator
    {
        private static PrinterHka hka;
        private static Class _msg;
        private string printerSerial;
        public bool _deviceConnected;
        private readonly string authorizedSerial = "Z1F0008536";

        public DeviceValidator()
        {
            CheckDeviceSerial();
        }

        public bool CheckDeviceSerial()
        {
            _msg = new Class();
            hka = new PrinterHka();
            if (_msg.DBG)
            {
                _msg.Wrn("Modo Developer");
                _deviceConnected = true;
            }
            else
            {
                hka.PFopen();
                printerSerial = hka.PFregisteredSerial();
                hka.PFclose();
                if (printerSerial != authorizedSerial)
                {
                    _msg.Wrn("Serial No Autorizado: " + printerSerial);
                    _deviceConnected = false;
                }
                else
                {
                    _msg.Inf("Serial Autorizado: " + printerSerial);
                    _deviceConnected = true;
                }
            }
            return _deviceConnected;
        }
    }
}
