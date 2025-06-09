using System;
using System.Collections.Generic;
using ModuloESCPOS.Commands;
using ModuloESCPOS.Models;
using ModuloESCPOS.Printer;
using ModuloESCPOS.Templates;

namespace ModuloESCPOS
{
    public class TicketPrinter
    {
        private readonly UsbPrinterConnection _printer;
        private readonly TemplateEngine _templateEngine;
        private string _printerPort;

        public TicketPrinter(TemplateEngine templateEngine, string printerPort = "POS-80C")
        {
            _printer = new UsbPrinterConnection();
            _templateEngine = templateEngine;
            _printerPort = printerPort;
        }

        public bool PrintDocument(PrintDocument document)
        {
            try
            {
                if (!_printer.Connect(_printerPort))
                    return false;

                using (_printer)
                {
                    var commands = _templateEngine.GenerateTicket(document);
                    var finalData = EscPosCommands.CombineCommands(commands.ToArray());
                    return _printer.Write(finalData);
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error al imprimir documento: {ex.Message}");
                return false;
            }
        }
    }
}
