import clr
import sys
from System.Reflection import Assembly
import time
import os
import serial.tools.list_ports


try:
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        print(port.device)

    assembly_path = os.path.abspath(r"./library/TfhkaNet.dll")
    print(f"Ruta absoluta del ensamblado: {assembly_path}")
    Assembly.LoadFrom(assembly_path)

    clr.AddReference("TfhkaNet")
    from TfhkaNet.IF.VE import Tfhka

    impresora = Tfhka()

    resultado = impresora.OpenFpCtrl("COM9")
    print(f"OpenFpCtrl: {resultado}")
    time.sleep(0.5)

    resultado = impresora.CheckFPrinter()
    print(f"CheckFPrinter: {resultado}")  # bool
    time.sleep(0.5)

    resultado = impresora.SendCmd("PH01Encabezado 1")
    print(f"SendCmd: {resultado}")
    time.sleep(0.5)

    resultado = impresora.SendCmd("800Documento de prueba")
    print(f"SendCmd: {resultado}")
    time.sleep(0.5)

    resultado = impresora.SendCmd("80*Documentos NO Fiscales 1")
    print(f"SendCmd: {resultado}")
    time.sleep(0.5)

    resultado = impresora.SendCmd("80>Documentos NO Fiscales 2")
    print(f"SendCmd: {resultado}")
    time.sleep(0.5)

    resultado = impresora.SendCmd("80$Documentos NO Fiscales 3")
    print(f"SendCmd: {resultado}")
    time.sleep(0.5)

    resultado = impresora.SendCmd("80!Documentos NO Fiscales 3")
    print(f"SendCmd: {resultado}")
    time.sleep(0.5)

    resultado = impresora.SendCmd("810fin del uso")
    print(f"SendCmd: {resultado}")
    time.sleep(0.5)

    objeto = impresora.GetSVPrinterData()
    print(f"Country: {objeto.Country}")  # str
    print(f"Model: {objeto.Model}")  # str
    print("=" * 50)
    time.sleep(0.5)

    objeto = impresora.GetPrinterStatus()
    print(f"Error Validity: {objeto.ErrorValidity}")  # bool
    print(f"Printer Error Code: {objeto.PrinterErrorCode}")  # int
    print(f"Printer Error Description: {objeto.PrinterErrorDescription}")  # str
    print(f"Printer Status Code: {objeto.PrinterStatusCode}")  # int
    print(f"Printer Status Description: {objeto.PrinterStatusDescription}")  # str
    print("=" * 50)
    time.sleep(0.5)

    objeto = impresora.GetS1PrinterData()
    print(f"Audit Reports Counter: {objeto.AuditReportsCounter}")  # int
    print(f"Cashier Number: {objeto.CashierNumber}")  # int
    print(f"Current Printer DateTime: {objeto.CurrentPrinterDateTime}")  # DateTime
    print(f"Daily Closure Counter: {objeto.DailyClosureCounter}")  # int
    print(f"Last Credit Note Number: {objeto.LastCreditNoteNumber}")  # int
    print(f"Last Debit Note Number: {objeto.LastDebitNoteNumber}")  # int
    print(f"Last Invoice Number: {objeto.LastInvoiceNumber}")  # int
    print(f"Last Non-Fiscal Document Number: {objeto.LastNonFiscalDocNumber}")  # int
    print(f"Quantity of Non-Fiscal Documents: {objeto.QuantityNonFiscalDocuments}")  # int
    print(f"Quantity of Credit Notes Today: {objeto.QuantityOfCreditNotesToday}")  # int
    print(f"Quantity of Debit Notes Today: {objeto.QuantityOfDebitNotesToday}")  # int
    print(f"Quantity of Invoices Today: {objeto.QuantityOfInvoicesToday}")  # int
    print(f"RIF: {objeto.RIF}")  # str
    print(f"Registered Machine Number: {objeto.RegisteredMachineNumber}")  # str
    print(f"Total Daily Sales: {objeto.TotalDailySales}")  # float
    print("=" * 50)
    time.sleep(0.5)

    objeto = impresora.GetS2PrinterData()
    print(f"Amount Payable: {objeto.AmountPayable}")  # float
    print(f"Condition: {objeto.Condition}")  # int
    print(f"Data Dummy: {objeto.DataDummy}")  # float
    print(f"Number of Payments Made: {objeto.NumberPaymentsMade}")  # int
    print(f"Quantity of Articles: {objeto.QuantityArticles}")  # int
    print(f"Sub Total Bases: {objeto.SubTotalBases}")  # float
    print(f"Sub Total Tax: {objeto.SubTotalTax}")  # float
    print(f"Type of Document: {objeto.TypeDocument}")  # str
    print("=" * 50)
    time.sleep(0.5)

    objeto = impresora.GetS3PrinterData()
    print(f"All System Flags: {objeto.AllSystemFlags}")  # list
    all_system_flags = objeto.get_AllSystemFlags()
    print("All System Flags:")
    for index, flag in enumerate(all_system_flags):
        print(f"Flag {index + 1} = {flag}")

    print(f"Tax 1: {objeto.Tax1}")  # float
    print(f"Tax 2: {objeto.Tax2}")  # float
    print(f"Tax 3: {objeto.Tax3}")  # float
    print(f"Tax IGTF: {objeto.TaxIGTF}")  # float
    print(f"Type Tax 1: {objeto.TypeTax1}")  # int
    print(f"Type Tax 2: {objeto.TypeTax2}")  # int
    print(f"Type Tax 3: {objeto.TypeTax3}")  # int
    print(f"Type Tax IGTF: {objeto.TypeTaxIGTF}")  # int
    print("=" * 50)
    time.sleep(0.5)

    objeto = impresora.GetS5PrinterData()
    print(f"Audit Memory Free Capacity: {objeto.AuditMemoryFreeCapacity}")  # float
    print(f"Audit Memory Number: {objeto.AuditMemoryNumber}")  # int
    print(f"Audit Memory Total Capacity: {objeto.AuditMemoryTotalCapacity}")  # float
    print(f"Number of Registered Documents: {objeto.NumberRegisteredDocuments}")  # int
    print(f"RIF: {objeto.RIF}")  # str
    print(f"Registered Machine Number: {objeto.RegisteredMachineNumber}")  # str
    print("=" * 50)
    time.sleep(0.5)

    resultado = impresora.PrintXReport()
    print(f"PrintXReport: {resultado}")  # None
    time.sleep(2)

    resultado = impresora.PrintZReport()
    print(f"PrintZReport: {resultado}")  # None
    time.sleep(2)

    resultado = impresora.UploadReportCmd("U1X", "FileReport.txt")  # U0X, U0Z, U1Z, U1X
    print(f"UploadReportCmd: {resultado}")
    time.sleep(1)

    resultado = impresora.UploadStatusCmd("S1", "FileStatus.txt")  # S1, S2, S3, S4, S5, S8E, S8P
    print(f"UploadStatusCmd: {resultado}")  # bool
    time.sleep(1)

    impresora.CloseFpCtrl()

except Exception as e:
    import traceback

    print(f"Ocurrió un error: {e}", file=sys.stderr)
    print(traceback.format_exc(), file=sys.stderr)
