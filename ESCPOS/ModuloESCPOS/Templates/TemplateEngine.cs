using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using ModuloESCPOS.Commands;
using ModuloESCPOS.Models;
using ModuloESCPOS.Config;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace ModuloESCPOS.Templates
{
    public class TemplateEngine
    {
        private readonly string _templatePath;
        private readonly PrinterConfig _config;
        private JObject _template;

        public TemplateEngine(string templatePath)
        {
            _templatePath = templatePath;
            _config = PrinterConfig.Instance;
            LoadTemplate();
        }

        private void LoadTemplate()
        {
            if (!File.Exists(_templatePath))
                throw new FileNotFoundException($"Template file not found: {_templatePath}");

            var json = File.ReadAllText(_templatePath);
            _template = JObject.Parse(json);
        }

        public List<byte[]> GenerateTicket(PrintDocument document)
        {
            var commands = new List<byte[]>();

            // Inicializar impresora
            commands.Add(EscPosCommands.InitializePrinter);

            // Configurar modo condensado si está habilitado
            if (_config.IsCondensedModeEnabled())
            {
                commands.Add(EscPosCommands.CondensedMode);
            }

            // Imprimir logo si está habilitado
            if (_config.IsLogoEnabled())
            {
                var logoPath = _config.GetLogoPath();
                if (File.Exists(logoPath))
                {
                    commands.Add(EscPosCommands.AlignCenter);
                    commands.Add(EscPosCommands.PrintImage(logoPath, _config.GetLogoMaxWidth()));
                    commands.Add(EscPosCommands.NewLine);
                }
            }

            // Procesar secciones de la plantilla
            var sections = _template["sections"] as JArray;
            foreach (var section in sections)
            {
                ProcessSection(section, document, commands);
            }

            // Desactivar modo condensado si estaba habilitado
            if (_config.IsCondensedModeEnabled())
            {
                commands.Add(EscPosCommands.NormalMode);
            }

            return commands;
        }

        private void ProcessSection(JToken section, PrintDocument document, List<byte[]> commands)
        {
            var type = section["type"].ToString();
            
            switch (type)
            {
                case "init":
                    ProcessCommands(section["commands"], commands);
                    break;

                case "finish":
                    ProcessCommands(section["commands"], commands);
                    break;

                case "header":
                case "customer":
                case "totals":
                case "footer":
                    ProcessTextSection(section, document, commands);
                    break;

                case "items":
                    ProcessItemsSection(section, document, commands);
                    break;

                case "payments":
                    ProcessPaymentsSection(section, document, commands);
                    break;

                case "barcode":
                    if (_config.IsBarcodeEnabled())
                    {
                        ProcessBarcodeSection(section, document, commands);
                    }
                    break;

                case "qr":
                    if (_config.IsQREnabled())
                    {
                        ProcessQRSection(section, document, commands);
                    }
                    break;
            }
        }

        private void ProcessBarcodeSection(JToken section, PrintDocument document, List<byte[]> commands)
        {
            var text = FormatText(section["text"].ToString(), document);
            var align = section["align"]?.ToString() ?? "center";
            var config = _config.GetBarcodeConfig();

            commands.Add(GetAlignmentCommand(align));
            commands.Add(EscPosCommands.PrintBarcode(text, config.type, config.height, config.width, config.hri));
            commands.Add(EscPosCommands.NewLine);
        }

        private void ProcessQRSection(JToken section, PrintDocument document, List<byte[]> commands)
        {
            var text = FormatText(section["text"].ToString(), document);
            var align = section["align"]?.ToString() ?? "center";
            var config = _config.GetQRConfig();

            commands.Add(GetAlignmentCommand(align));
            commands.Add(EscPosCommands.PrintQRCode(text, config.size, config.correction));
            commands.Add(EscPosCommands.NewLine);
        }

        private void ProcessTextSection(JToken section, PrintDocument document, List<byte[]> commands)
        {
            var align = section["align"]?.ToString() ?? "left";
            commands.Add(GetAlignmentCommand(align));

            if (section["header"] != null)
            {
                ProcessTextItem(section["header"], document, commands);
            }

            var items = section["items"] as JArray;
            if (items != null)
            {
                foreach (var item in items)
                {
                    ProcessTextItem(item, document, commands);
                }
            }
        }

        private void ProcessItemsSection(JToken section, PrintDocument document, List<byte[]> commands)
        {
            var align = section["align"]?.ToString() ?? "left";
            commands.Add(GetAlignmentCommand(align));

            if (section["header"] != null)
            {
                ProcessTextItem(section["header"], document, commands);
            }

            var format = section["itemFormat"] as JArray;
            foreach (var item in document.Items)
            {
                foreach (var formatLine in format)
                {
                    if (ShouldSkip(formatLine, item)) continue;

                    var text = formatLine["text"].ToString();
                    text = FormatText(text, item);
                    
                    if (formatLine["style"]?.ToString() == "bold")
                        commands.Add(EscPosCommands.Bold);

                    commands.Add(EscPosCommands.GetTextBytes(text));

                    if (formatLine["style"]?.ToString() == "bold")
                        commands.Add(EscPosCommands.BoldOff);
                }
            }
        }

        private void ProcessPaymentsSection(JToken section, PrintDocument document, List<byte[]> commands)
        {
            var align = section["align"]?.ToString() ?? "left";
            commands.Add(GetAlignmentCommand(align));

            if (section["header"] != null)
            {
                ProcessTextItem(section["header"], document, commands);
            }

            var format = section["itemFormat"] as JArray;
            foreach (var payment in document.Payments)
            {
                foreach (var formatLine in format)
                {
                    if (ShouldSkip(formatLine, payment)) continue;

                    var text = formatLine["text"].ToString();
                    text = FormatText(text, payment);
                    
                    if (formatLine["style"]?.ToString() == "bold")
                        commands.Add(EscPosCommands.Bold);

                    commands.Add(EscPosCommands.GetTextBytes(text));

                    if (formatLine["style"]?.ToString() == "bold")
                        commands.Add(EscPosCommands.BoldOff);
                }
            }
        }

        private void ProcessTextItem(JToken item, object data, List<byte[]> commands)
        {
            if (item["type"]?.ToString() == "line")
            {
                commands.Add(EscPosCommands.CreateLine());
                return;
            }

            if (ShouldSkip(item, data)) return;

            var text = item["text"].ToString();
            text = FormatText(text, data);

            if (item["style"]?.ToString() == "bold")
                commands.Add(EscPosCommands.Bold);

            commands.Add(EscPosCommands.GetTextBytes(text));

            if (item["style"]?.ToString() == "bold")
                commands.Add(EscPosCommands.BoldOff);
        }

        private void ProcessCommands(JToken commandList, List<byte[]> commands)
        {
            if (commandList == null) return;

            foreach (var cmd in commandList)
            {
                var cmdStr = cmd.ToString();
                var parts = cmdStr.Split(':');
                var command = parts[0];
                var param = parts.Length > 1 ? parts[1] : null;

                switch (command)
                {
                    case "SetLineSpacing":
                        commands.Add(EscPosCommands.SetLineSpacing((byte)int.Parse(param)));
                        break;
                    case "Feed":
                        commands.Add(EscPosCommands.Feed((byte)int.Parse(param)));
                        break;
                    case "Cut":
                        commands.Add(EscPosCommands.Cut);
                        break;
                    case "NewLine":
                        commands.Add(EscPosCommands.NewLine);
                        break;
                }
            }
        }

        private string FormatText(string template, object data)
        {
            var dateFormat = _config.GetDateFormat();
            var numberFormat = _config.GetNumberFormat();

            while (template.Contains("{"))
            {
                var start = template.IndexOf('{');
                var end = template.IndexOf('}', start);
                if (end == -1) break;

                var placeholder = template.Substring(start + 1, end - start - 1);
                var format = "";

                if (placeholder.Contains(":"))
                {
                    var parts = placeholder.Split(':');
                    placeholder = parts[0];
                    format = parts[1];
                }

                var value = GetPropertyValue(data, placeholder);
                string replacement;

                if (value is DateTime dateValue)
                {
                    replacement = dateValue.ToString(format ?? dateFormat);
                }
                else if (value is decimal decimalValue)
                {
                    if (string.IsNullOrEmpty(format))
                    {
                        format = "N" + numberFormat.decimals;
                    }
                    replacement = decimalValue.ToString(format)
                        .Replace(".", numberFormat.decimalSep)
                        .Replace(",", numberFormat.thousandsSep);
                }
                else
                {
                    replacement = value?.ToString() ?? "";
                }

                template = template.Remove(start, end - start + 1)
                                 .Insert(start, replacement);
            }

            return template;
        }

        private bool ShouldSkip(JToken item, object data)
        {
            var condition = item["condition"]?.ToString();
            if (string.IsNullOrEmpty(condition)) return false;

            // Implementación simple de condiciones
            if (condition.Contains("!="))
            {
                var parts = condition.Split(new[] { "!=" }, StringSplitOptions.None);
                var prop = GetPropertyValue(data, parts[0].Trim());
                return prop?.ToString() == parts[1].Trim();
            }
            else if (condition.Contains(">"))
            {
                var parts = condition.Split('>');
                var prop = GetPropertyValue(data, parts[0].Trim());
                if (prop is decimal value)
                {
                    return !(value > 0);
                }
            }

            return false;
        }

        private object GetPropertyValue(object obj, string propertyName)
        {
            var property = obj.GetType().GetProperty(propertyName);
            return property?.GetValue(obj);
        }

        private byte[] GetAlignmentCommand(string align)
        {
            switch (align.ToLower())
            {
                case "center":
                    return EscPosCommands.AlignCenter;
                case "right":
                    return EscPosCommands.AlignRight;
                default:
                    return EscPosCommands.AlignLeft;
            }
        }
    }
}
