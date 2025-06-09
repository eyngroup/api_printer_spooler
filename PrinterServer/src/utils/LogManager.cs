using System;
using Microsoft.Extensions.Logging;
using NLog;
using NLog.Config;
using NLog.Targets;
using LogLevel = Microsoft.Extensions.Logging.LogLevel;

namespace ApiPrinterServer.Utils
{
    public class LogManager
    {
        private static readonly NLog.ILogger Logger = NLog.LogManager.GetCurrentClassLogger();
        
        public static void Initialize(string logPath, bool enabled, string level)
        {
            var config = new LoggingConfiguration();

            // Configurar target de archivo
            var fileTarget = new FileTarget("file")
            {
                FileName = string.Format("{0}/api_printer_server_{1:yyyy-MM-dd}.log", logPath, DateTime.Now),
                Layout = "${longdate}|${level:uppercase=true}|${logger}|${message}${onexception:${newline}${exception:format=tostring}}",
                ArchiveFileName = string.Format("{0}/archive/api_printer_server_{{#}}.log", logPath),
                ArchiveEvery = FileArchivePeriod.Day,
                ArchiveNumbering = ArchiveNumberingMode.Date,
                MaxArchiveFiles = 7
            };

            // Configurar target de consola
            var consoleTarget = new ConsoleTarget("console")
            {
                Layout = "${longdate}|${level:uppercase=true}|${logger}|${message}"
            };

            // Agregar reglas
            if (enabled)
            {
                var logLevel = ParseLogLevel(level);
                config.AddRule(NLog.LogLevel.FromOrdinal((int)logLevel), NLog.LogLevel.Fatal, fileTarget);
                config.AddRule(NLog.LogLevel.FromOrdinal((int)logLevel), NLog.LogLevel.Fatal, consoleTarget);
            }

            // Aplicar configuración
            NLog.LogManager.Configuration = config;
            Logger.Info("Sistema de logs inicializado");
        }

        private static LogLevel ParseLogLevel(string level)
        {
            string upperLevel = level.ToUpper();
            if (upperLevel == "TRACE")
                return LogLevel.Trace;
            if (upperLevel == "DEBUG")
                return LogLevel.Debug;
            if (upperLevel == "INFO")
                return LogLevel.Information;
            if (upperLevel == "WARN")
                return LogLevel.Warning;
            if (upperLevel == "ERROR")
                return LogLevel.Error;
            if (upperLevel == "FATAL")
                return LogLevel.Critical;
            return LogLevel.Information;
        }

        public static void UpdateLogLevel(string level)
        {
            var logLevel = ParseLogLevel(level);
            var config = NLog.LogManager.Configuration;
            
            foreach (var rule in config.LoggingRules)
            {
                rule.SetLoggingLevels(NLog.LogLevel.FromOrdinal((int)logLevel), NLog.LogLevel.Fatal);
            }
            
            NLog.LogManager.ReconfigExistingLoggers();
            Logger.Info(string.Format("Nivel de log actualizado a: {0}", level));
        }

        public static void Shutdown()
        {
            Logger.Info("Sistema de logs detenido");
            NLog.LogManager.Shutdown();
        }
    }
}
