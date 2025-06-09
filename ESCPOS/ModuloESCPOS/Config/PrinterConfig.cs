using System;
using System.IO;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace ModuloESCPOS.Config
{
    public class PrinterConfig
    {
        private static PrinterConfig _instance;
        private JObject _config;

        public static PrinterConfig Instance
        {
            get
            {
                if (_instance == null)
                {
                    _instance = new PrinterConfig();
                }
                return _instance;
            }
        }

        private PrinterConfig()
        {
            LoadConfig();
        }

        private void LoadConfig()
        {
            var configPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "config.json");
            if (!File.Exists(configPath))
            {
                throw new FileNotFoundException("Archivo de configuración no encontrado", configPath);
            }

            _config = JObject.Parse(File.ReadAllText(configPath));
        }

        public string GetPrinterName()
        {
            return _config["printer"]?["name"]?.ToString() ?? "POS-80C";
        }

        public string GetActiveTemplate()
        {
            var templateName = _config["template"]?["active"]?.ToString() ?? "simple";
            var templatePath = _config["template"]?["templates"]?[templateName]?.ToString();
            
            if (string.IsNullOrEmpty(templatePath))
            {
                throw new Exception($"Plantilla '{templateName}' no encontrada en la configuración");
            }

            return Path.Combine(AppDomain.CurrentDomain.BaseDirectory, templatePath);
        }

        public bool IsLogoEnabled()
        {
            return _config["features"]?["logo"]?["enabled"]?.Value<bool>() ?? false;
        }

        public string GetLogoPath()
        {
            if (!IsLogoEnabled()) return null;
            var path = _config["features"]?["logo"]?["path"]?.ToString();
            return path != null ? Path.Combine(AppDomain.CurrentDomain.BaseDirectory, path) : null;
        }

        public int GetLogoMaxWidth()
        {
            return _config["features"]?["logo"]?["maxWidth"]?.Value<int>() ?? 380;
        }

        public bool IsBarcodeEnabled()
        {
            return _config["features"]?["barcode"]?["enabled"]?.Value<bool>() ?? false;
        }

        public (byte type, byte height, byte width, bool hri) GetBarcodeConfig()
        {
            if (!IsBarcodeEnabled()) return (0, 0, 0, false);

            var config = _config["features"]?["barcode"];
            return (
                GetBarcodeType(config?["type"]?.ToString() ?? "CODE128"),
                (byte)(config?["height"]?.Value<int>() ?? 64),
                (byte)(config?["width"]?.Value<int>() ?? 2),
                config?["hri"]?.Value<bool>() ?? true
            );
        }

        public bool IsQREnabled()
        {
            return _config["features"]?["qr"]?["enabled"]?.Value<bool>() ?? false;
        }

        public (byte size, byte correction) GetQRConfig()
        {
            if (!IsQREnabled()) return (0, 0);

            var config = _config["features"]?["qr"];
            return (
                (byte)(config?["size"]?.Value<int>() ?? 4),
                GetQRErrorCorrection(config?["correction"]?.ToString() ?? "M")
            );
        }

        private byte GetBarcodeType(string type)
        {
            switch (type.ToUpper())
            {
                case "UPC-A": return 0;
                case "UPC-E": return 1;
                case "EAN13": return 2;
                case "EAN8": return 3;
                case "CODE39": return 4;
                case "ITF": return 5;
                case "CODABAR": return 6;
                case "CODE128": return 73;
                default: return 73;
            }
        }

        private byte GetQRErrorCorrection(string level)
        {
            switch (level.ToUpper())
            {
                case "L": return 48; // 7%
                case "M": return 49; // 15%
                case "Q": return 50; // 25%
                case "H": return 51; // 30%
                default: return 49;  // M
            }
        }

        public string GetDateFormat()
        {
            return _config["formatting"]?["dateFormat"]?.ToString() ?? "dd/MM/yyyy";
        }

        public (int decimals, string decimalSep, string thousandsSep) GetNumberFormat()
        {
            var config = _config["formatting"]?["numberFormat"];
            return (
                config?["decimals"]?.Value<int>() ?? 2,
                config?["decimalSeparator"]?.ToString() ?? ",",
                config?["thousandsSeparator"]?.ToString() ?? "."
            );
        }

        public bool IsCondensedModeEnabled()
        {
            return _config["formatting"]?["condensedMode"]?["enabled"]?.Value<bool>() ?? false;
        }

        public int GetCondensedColumns()
        {
            return _config["formatting"]?["condensedMode"]?["columns"]?.Value<int>() ?? 56;
        }
    }
}
