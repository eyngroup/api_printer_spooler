using System;
using System.Collections.Generic;
using System.IO;
using ModuloESCPOS.Models;
using ModuloESCPOS.Templates;
using Newtonsoft.Json;

namespace ModuloESCPOS
{
    class Program
    {
        static void Main(string[] args)
        {
            // Cargar el documento desde invoice.json
            var jsonPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "invoice.json");
            if (!File.Exists(jsonPath))
            {
                Console.WriteLine($"Error: No se encontró el archivo {jsonPath}");
                Console.WriteLine("Presione una tecla para salir...");
                Console.ReadKey();
                return;
            }

            try
            {
                var document = JsonConvert.DeserializeObject<PrintDocument>(File.ReadAllText(jsonPath));

                // Usar la plantilla simple desde archivo JSON
                Console.WriteLine("Imprimiendo factura...");
                var templatePath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "Templates", "simple.template.json");
                var templateEngine = new TemplateEngine(templatePath);
                var printer = new TicketPrinter(templateEngine);
                
                if (printer.PrintDocument(document))
                {
                    Console.WriteLine("Impresión completada con éxito!");
                }
                else
                {
                    Console.WriteLine("Error al imprimir. Verifique que la impresora esté conectada y encendida.");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error al procesar el documento: {ex.Message}");
            }

            Console.WriteLine("\nPresione una tecla para salir...");
            Console.ReadKey();
        }

        static PrintDocument CreateExampleDocument()
        {
            return new PrintDocument
            {
                CustomerVat = "V131328526",
                CustomerName = "NOMBRE DEL CLIENTE",
                CustomerAddress = "DIRECCION DEL CLIENTE\n\nCIUDAD DEL CLIENTE  1021\nVenezuela",
                CustomerPhone = "02916419691",
                DocumentName = "Shop/0001",
                DocumentNumber = "00004-001-0002",
                DocumentDate = "2022-01-01",
                DocumentCurrency = "VEF",
                Items = new List<PrintDocumentItem>
                {
                    new PrintDocumentItem
                    {
                        ItemRef = "60-2005",
                        ItemName = "ACEITE REFRIGERANTE PAG-150 R134 AUTOM 8",
                        ItemQuantity = 1,
                        ItemPrice = 140.22m,
                        ItemTax = 16,
                        ItemDiscount = 0,
                        ItemDiscountType = "",
                        ItemComment = "oz GENETRON"
                    },
                    new PrintDocumentItem
                    {
                        ItemRef = "80-3007",
                        ItemName = "FILTRO DE ACEITE AUTOMOTRIZ",
                        ItemQuantity = 3,
                        ItemPrice = 45.00m,
                        ItemTax = 0,
                        ItemDiscount = 0,
                        ItemDiscountType = "",
                        ItemComment = ""
                    }
                },
                Payments = new List<PrintDocumentPayment>
                {
                    new PrintDocumentPayment
                    {
                        PaymentMethod = "01",
                        PaymentName = "EFECTIVO",
                        PaymentAmount = 140.22m
                    },
                    new PrintDocumentPayment
                    {
                        PaymentMethod = "02",
                        PaymentName = "TARJETA DE CRÉDITO",
                        PaymentAmount = 135.00m
                    }
                },
                DeliveryComments = new List<string>(),
                DeliveryBarcode = "00004-001-0002"
            };
        }
    }
}
