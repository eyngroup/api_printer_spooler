using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.IO;
using System.Net;
using Newtonsoft.Json;
using Serilog;
using SpoolerAPI.Models;
using SpoolerAPI.PrinterComm;
using System.Globalization;
using System.Linq;
using System.Text;

namespace SpoolerAPI.Controllers
{
    public class InvoiceController
    {
        private static PrinterHka printer;
        private static readonly bool validate;
        private static Information printerData;
        private static Class _msg = new Class();

        public static void Invoice(HttpListenerContext context)
        {
            if (context.Request.HttpMethod == "POST" && context.Request.Url.AbsolutePath == "/api/invoice")
            {
                using (StreamReader reader = new StreamReader(context.Request.InputStream))
                {
                    _msg.Wrn("Solicitud 'ReportX' iniciada en " + context.Request.Url);

                    string requestBody = reader.ReadToEnd();
                    _msg.Dbg("Json recibido: " + requestBody);

                    if (!ValidateJson(requestBody))
                    {
                        dynamic response = new { error = "El JSON recibido es inválido" };

                        string responseJson = JsonConvert.SerializeObject(response);

                        byte[] buffer = System.Text.Encoding.UTF8.GetBytes(responseJson);
                        context.Response.ContentType = "application/json";
                        context.Response.ContentLength64 = buffer.Length;
                        context.Response.OutputStream.Write(buffer, 0, buffer.Length);

                        context.Response.Close();
                        return;
                    }

                    try
                    {
                        InvoiceData invoiceData = JsonConvert.DeserializeObject<InvoiceData>(requestBody);
                        string typeDocument = invoiceData.InvoiceType;

                        // Aquí procesamos el objeto "invoiceData" para enviarlo a la impresora
                        if (typeDocument == "out_invoice") { PrintInvoice(invoiceData); }
                        if (typeDocument == "out_refund") { PrintCreditNote(invoiceData); }

                        dynamic response = new { message = "La impresión se realizó correctamente" };

                        string responseJson = JsonConvert.SerializeObject(response);

                        byte[] buffer = System.Text.Encoding.UTF8.GetBytes(responseJson);
                        context.Response.ContentType = "application/json";
                        context.Response.ContentLength64 = buffer.Length;
                        context.Response.OutputStream.Write(buffer, 0, buffer.Length);
                    }
                    catch (ValidationException ex)
                    {
                        dynamic response = new { error = ex.Message };

                        string responseJson = JsonConvert.SerializeObject(response);

                        byte[] buffer = System.Text.Encoding.UTF8.GetBytes(responseJson);
                        context.Response.ContentType = "application/json";
                        context.Response.ContentLength64 = buffer.Length;
                        context.Response.OutputStream.Write(buffer, 0, buffer.Length);
                    }
                }

                context.Response.Close();
            }
        }

        private static void PrintInvoice(InvoiceData invoiceData)
        {
            Log.Information("Invoice {invoiceData}: ", invoiceData);

            printer = new PrinterHka();

            try
            {
                printer.PFopen();

                if (printer.PFcheck())
                {



                    #region <head>
                    string cFiscal_ID, cCustomer, cAddress, cPhone, cReference;
                    cFiscal_ID = invoiceData.FiscalID;
                    cCustomer = NormalizedString(invoiceData.Customer);
                    cAddress = NormalizedString(invoiceData.Address);
                    cPhone = NormalizedString(invoiceData.Phone);
                    cReference = NormalizedString(invoiceData.Reference);

                    // Format
                    cFiscal_ID = cFiscal_ID.Substring(0, cFiscal_ID.Length < 40 ? cFiscal_ID.Length : 40).Trim();
                    cCustomer = cCustomer.Substring(0, cCustomer.Length < 40 ? cCustomer.Length : 40).Trim();
                    cAddress = cAddress.Substring(0, cAddress.Length < 36 ? cAddress.Length : 36).Trim();
                    cPhone = cPhone.Substring(0, cPhone.Length < 36 ? cPhone.Length : 36).Trim();
                    cReference = cReference.Substring(0, cReference.Length < 36 ? cReference.Length : 36).Trim();

                    printer.PFsend($"iR*{cFiscal_ID}");
                    printer.PFsend($"iS*{cCustomer}");
                    printer.PFsend($"i00DIR: {cAddress}");
                    printer.PFsend($"i01TEL: {cPhone}");
                    printer.PFsend($"i02REF: {cReference}");

                    #endregion




                    #region <body>
                    string cTax, cPrice, cQuantity, cProduct;
                    foreach (var item in invoiceData.Items)
                    {
                        cTax = item.Tax.ToString();
                        if (cTax.Equals("")) { cTax = Convert.ToInt16(1).ToString(); }
                        else { cTax = Convert.ToInt16(cTax).ToString(); }
                        cPrice = Convert.ToDecimal(item.Price).ToString("###0.00");
                        cQuantity = Convert.ToDecimal(item.Quantity).ToString("###0.000");
                        cProduct = NormalizedString(Convert.ToString(item.Product));

                        // Format
                        switch (cTax)
                        {
                            case "0": cTax = " "; break;
                            case "12": cTax = "!"; break;
                            case "16": cTax = "!"; break;
                            case "8": cTax = "\""; break;
                            case "22": cTax = "#"; break;
                            case "31": cTax = "#"; break;
                            default: cTax = " "; break;
                        }
                        cPrice = NormalizedInt(cPrice).PadLeft(16, '0');
                        cQuantity = NormalizedInt(cQuantity).PadLeft(17, '0');
                        cProduct = cProduct.Substring(0, cProduct.Length < 127 ? cProduct.Length : 127).Trim();

                        printer.PFsend($"{cTax}{cPrice}{cQuantity}{cProduct}");
                    }
                    printer.PFsend("3");

                    #endregion




                    #region <footer>
                    string cCode, cAmount;
                    foreach (var pay in invoiceData.Payments)
                    {
                        cCode = pay.Code;

                        if (pay.Code == "false")
                        {
                            printer.PFsend("201");
                        }
                        else
                        {
                            // Format
                            cAmount = Convert.ToDecimal(pay.Amount).ToString("###0.00");
                            cAmount = NormalizedInt(cAmount).PadLeft(17, '0');

                            printer.PFsend($"{cCode}{cAmount}");
                        }
                    }
                    #endregion



                    #region <Close>
                    printer.PFsend("101");
                    printer.PFsend("199");
                    #endregion



                }
                printer.PFclose();
            }
            catch (System.NullReferenceException ex)
            {
                Log.Information("Se produjo un error al procesar la factura: " + ex.Message);
            }
            catch (Exception ex)
            {
                printer.PFclose();
                Log.Information("Se produjo un error al procesar la factura: " + ex.Message);
            }
        }


        private static void PrintCreditNote(InvoiceData invoiceData)
        {
            Log.Information("Tipo de Documento: {invoiceData}", invoiceData.InvoiceType);

            printer = new PrinterHka();

            try
            {
                printer.PFopen();

                string cSerialPrinter = printer.PFregisteredSerial();



                if (printer.PFcheck())
                {
                    #region <head>
                    string dDocDate, cFiscal_ID, cCustomer, cAddress, cPhone, cReference;
                    DateTime dDate = Convert.ToDateTime(invoiceData.InvoiceDate);
                    cFiscal_ID = invoiceData.FiscalID;
                    cCustomer = NormalizedString(invoiceData.Customer);
                    cAddress = NormalizedString(invoiceData.Address);
                    cPhone = NormalizedString(invoiceData.Phone);
                    cReference = NormalizedString(invoiceData.Reference);

                    // Format
                    dDocDate = dDate.ToString("dd-MM-yyyy");
                    cFiscal_ID = cFiscal_ID.Substring(0, cFiscal_ID.Length < 12 ? cFiscal_ID.Length : 12).Trim(); //Max 32
                    cCustomer = cCustomer.Substring(0, cCustomer.Length < 28 ? cCustomer.Length : 28).Trim(); //Max 28
                    cAddress = cAddress.Substring(0, cAddress.Length < 35 ? cAddress.Length : 35).Trim(); //Max 42 - 5
                    cPhone = cPhone.Substring(0, cPhone.Length < 34 ? cPhone.Length : 34).Trim(); //Max 42 - 5
                    cReference = cReference.Substring(0, cReference.Length < 15 ? cReference.Length : 15).Trim(); //Max 15

                    printer.PFsend($"iF*00000000001");
                    printer.PFsend($"iD*{dDocDate}");
                    printer.PFsend($"iI*{cSerialPrinter}");
                    printer.PFsend($"iR*{cFiscal_ID}");
                    printer.PFsend($"iS*{cCustomer}");
                    printer.PFsend($"i00DIR: {cAddress}");
                    printer.PFsend($"i01TEL: {cPhone}");
                    printer.PFsend($"i02REF: {cReference}");




                    #endregion

                    #region <body>
                    string cTax, cPrice, cQuantity, cProduct;
                    foreach (var item in invoiceData.Items)
                    {
                        cTax = item.Tax.ToString();
                        if (cTax.Equals("")) { cTax = Convert.ToInt16(1).ToString(); }
                        else { cTax = Convert.ToInt16(cTax).ToString(); }
                        cPrice = Convert.ToDecimal(item.Price).ToString("###0.00");
                        cQuantity = Convert.ToDecimal(item.Quantity).ToString("###0.000");
                        cProduct = NormalizedString(Convert.ToString(item.Product));

                        // Format
                        switch (cTax)
                        {
                            case "0": cTax = "d0"; break;
                            case "12": cTax = "d1"; break;
                            case "16": cTax = "d1"; break;
                            case "8": cTax = "d2"; break;
                            case "22": cTax = "d3"; break;
                            case "31": cTax = "d3"; break;
                            default: cTax = "d0"; break;
                        }
                        cPrice = NormalizedInt(cPrice).PadLeft(10, '0');
                        cQuantity = NormalizedInt(cQuantity).PadLeft(8, '0');
                        cProduct = cProduct.Substring(0, cProduct.Length < 40 ? cProduct.Length : 40).Trim(); //Max 66

                        printer.PFsend($"{cTax}{cPrice}{cQuantity}{cProduct}");
                    }
                    printer.PFsend("3");

                    #endregion

                    #region <footer>
                    string cCode, cAmount;
                    foreach (var pay in invoiceData.Payments)
                    {
                        cCode = pay.Code;

                        if (pay.Code == "false")
                        {
                            printer.PFsend("101");
                        }
                        else
                        {
                            // Format
                            cAmount = Convert.ToDecimal(pay.Amount).ToString("###0.00");
                            cAmount = NormalizedInt(cAmount).PadLeft(12, '0');

                            printer.PFsend($"{cCode}{cAmount}");
                        }
                    }
                    #endregion

                    #region <Close>
                    printer.PFsend("199");
                    #endregion

                }
                printer.PFclose();
            }
            catch (System.NullReferenceException ex)
            {
                Log.Information("Se produjo un error al procesar la factura: " + ex.Message);
            }
            catch (Exception ex)
            {
                printer.PFclose();
                Log.Information("Se produjo un error al procesar la factura: " + ex.Message);
            }

        }

        private static string NormalizedString(string str)
        {
            string originalString = str;
            string normalizedString = originalString.Normalize(NormalizationForm.FormD);
            string outputString = new string(normalizedString
                .Where(c => CharUnicodeInfo.GetUnicodeCategory(c) != UnicodeCategory.NonSpacingMark)
                .ToArray());

            outputString = outputString.Replace("+58", "").Replace("/", "").Replace(".", "")
                .Replace("[", "").Replace("]", "").Replace("Venezuela", "");

            return outputString;
        }

        private static string NormalizedInt(string number)
        {
            number = number.Replace(",", "").Replace(".", "");
            return number;
        }

        public static bool ValidateJson(string json)
        {
            try
            {
                var invoiceData = JsonConvert.DeserializeObject<InvoiceData>(json);
                var context = new ValidationContext(invoiceData, serviceProvider: null, items: null);
                var validationResults = new List<ValidationResult>();
                //bool isValid = Validator.TryValidateObject(invoiceData, context, validationResults, validateAllProperties: true);

                return Validator.TryValidateObject(invoiceData, context, validationResults);
            }
            catch (Exception ex)
            {
                Log.Information("Se produjo un error al procesar el json: " + ex.Message);
                return false;
            }
        }


    }
}