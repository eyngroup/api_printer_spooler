from datetime import (timedelta, datetime as dt, date as pyDate, time as pyTime)
from operator import index

import sys
from DataPrinter.Hka import Tfhka

import serial
import os
import time

class Principal():

	def __init__(self):
		self.printer = Tfhka.Tfhka()
		self.puerto = ['COM3']
	
	def open_port(self):
		puerto = self.puerto[0]
		try:
			resp = self.printer.OpenFpctrl(puerto)
			if resp:
				print("Impresora Conectada Correctamente en: " + puerto)
		except serial.SerialException:
			print("Impresora no Conectada o Error Accediendo al Puerto")
	
	def recognize_port(self):
		for opciones in ['COM12', 'COM11', 'COM10','COM9', 'COM8', 'COM7', 'COM6', 'COM5', 'COM4', 'COM3']:
			try:
				resp = self.printer.OpenFpctrl(opciones)
				if resp:
					print("Impresora Conectada Correctamente en: " + opciones)
					self.puerto[0] = opciones
					response = True
			except:
				response = False
		return response 

	def close_port(self):
		resp = self.printer.CloseFpctrl()
		if not resp:
			print("Impresora Desconectada")
		else:
			print("Error")

	def programming(self):
		self.printer.SendCmd("D")

	def send_cmd(self,txt_cmd):
		cmd = txt_cmd.text()
		self.printer.SendCmd(str(cmd))

	def estado_error(self):
		self.txt_informacion.setText("")
		self.estado = self.printer.ReadFpStatus()
		self.txt_informacion.setText("Estado: " + self.estado[0] + "\n" + "Error: " + self.estado[5])

	def imprimir_ReporteZ(self):
		self.printer.PrintZReport()

	def imprimir_ReporteX(self):
		self.printer.PrintXReport()

	def obtener_estado(self):
		estado = 'S1'

		if estado == "S1":
			estado_s1 = self.printer.GetS1PrinterData()
			salida= "---Estado S1---\n" 
			salida+= "\nNumero Cajero: "+ str(estado_s1._cashierNumber) 
			salida+= "\nSubtotal Ventas: " + str(estado_s1._totalDailySales) 
			salida+= "\nNumero Ultima Factura: " + str(estado_s1._lastInvoiceNumber)
			salida+= "\nCantidad Facturas Hoy: " + str(estado_s1._quantityOfInvoicesToday)  
			salida+= "\nNumero Ultima Nota de Debito: " + str(estado_s1._lastDebtNoteNumber) 
			salida+= "\nCantidad Notas de Debito Hoy: " + str(estado_s1._quantityDebtNoteToday) 
			salida+= "\nNumero Ultima Nota de Credito: " + str(estado_s1._lastNCNumber) 
			salida+= "\nCantidad Notas de Credito Hoy: " + str(estado_s1._quantityOfNCToday) 
			salida+= "\nNumero Ultimo Documento No Fiscal: " + str(estado_s1._numberNonFiscalDocuments) 
			salida+= "\nCantidad de Documentos No Fiscales: " + str(estado_s1._quantityNonFiscalDocuments) 
			salida+= "\nCantidad de Reportes de Auditoria: " + str(estado_s1._auditReportsCounter) 
			salida+= "\nCantidad de Reportes Fiscales: " + str(estado_s1._fiscalReportsCounter)
			salida+= "\nCantidad de Reportes Z: " + str(estado_s1._dailyClosureCounter)
			salida+= "\nNumero de RIF: " + str(estado_s1._rif)
			salida+= "\nNumero de Registro: " + str(estado_s1._registeredMachineNumber)
			salida+= "\nHora de la Impresora: " + str(estado_s1._currentPrinterTime)
			salida+= "\nFecha de la Impresora: " + str(estado_s1._currentPrinterDate)
			print(salida)
			# self.txt_informacion.setText(salida)

		if estado == "S2":
			estado_s2 = self.printer.GetS2PrinterData()
			salida= "---Estado S2---\n" 
			salida+= "\nSubtotal de BI: "+ str(estado_s2._subTotalBases)  
			salida+= "\nSubtotal de Impuesto: " + str(estado_s2._subTotalTax) 
			salida+= "\nData Dummy: " + str(estado_s2._dataDummy)
			salida+= "\nCantidad de articulos: " + str(estado_s2._quantityArticles)  
			salida+= "\nMonto por Pagar: " + str(estado_s2._amountPayable) 
			salida+= "\nNumero de Pagos Realizados: " + str(estado_s2._numberPaymentsMade) 
			salida+= "\nTipo de Documento: " + str(estado_s2._typeDocument) 
			self.txt_informacion.setText(salida)

		if estado == "S3":
			estado_s3 = self.printer.GetS3PrinterData()
			salida= "---Estado S3---\n"
			salida+= "\nTipo Tasa 1 (1 = Incluido, 2= Excluido): "+ str(estado_s3._typeTax1) 
			salida+= "\nValor Tasa 1: "+ str(estado_s3._tax1) + " %"
			salida+= "\nTipo Tasa 2 (1 = Incluido, 2= Excluido): " + str(estado_s3._typeTax2) 
			salida+= "\nValor Tasa2: " + str(estado_s3._tax2) + " %"
			salida+= "\nTipo Tasa 3 (1 = Incluido, 2= Excluido): " + str(estado_s3._typeTax3)  
			salida+= "\nValor Tasa 3: " + str(estado_s3._tax3) + " %"
			salida+= "\n\nLista de Flags: " + str(estado_s3._systemFlags)
			self.txt_informacion.setText(salida)

		if estado == "S4":
			estado_s4 = self.printer.GetS4PrinterData()
			salida= "---Estado S4---\n"
			salida+= "\nMontos en Medios de Pago: " + str(estado_s4._allMeansOfPayment)
			self.txt_informacion.setText(salida)

		if estado == "S5":
			estado_s5 = self.printer.GetS5PrinterData()
			salida= "---Estado S5---\n"
			salida+= "\nNumero de RIF: "+ str(estado_s5._rif) 
			salida+= "\nNumero de Registro: " + str(estado_s5._registeredMachineNumber) 
			salida+= "\nNumero de Memoria de Auditoria : " + str(estado_s5._auditMemoryNumber)
			salida+= "\nCapacidad Total de Memoria Auditoria: " + str(estado_s5._auditMemoryTotalCapacity) + " MB" 
			salida+= "\nEspacio Disponible: " + str(estado_s5._auditMemoryFreeCapacity) + " MB" 
			salida+= "\nCantidad Documentos Registrados: " + str(estado_s5._numberRegisteredDocuments)
			self.txt_informacion.setText(salida)

		if estado == "S6":
			estado_s6 = self.printer.GetS6PrinterData()
			salida= "---Estado S6---\n"
			salida+= "\nModo Facturacion: "+ str(estado_s6._bit_Facturacion) 
			salida+= "\nModo Slip: " + str(estado_s6._bit_Slip) 
			salida+= "\nModo Validacion: " + str(estado_s6._bit_Validacion) 
			self.txt_informacion.setText(salida)

	def obtener_reporteZ(self):
		reporte = self.printer.GetZReport()
		salida= "Numero Ultimo Reporte Z: "+ str(reporte._numberOfLastZReport) 
		salida+= "\nFecha Ultimo Reporte Z: "+ str(reporte._zReportDate) 
		salida+= "\nHora Ultimo Reporte Z: "+ str(reporte._zReportTime) 
		salida+= "\nNumero Ultima Factura: "+ str(reporte._numberOfLastInvoice) 
		salida+= "\nFecha Ultima Factura: "+ str(reporte._lastInvoiceDate) 
		salida+= "\nHora Ultima Factura: "+ str(reporte._lastInvoiceTime)
		salida+= "\nNumero Ultima Nota de Debito: "+ str(reporte._numberOfLastDebitNote)
		salida+= "\nNumero Ultima Nota de Credito: "+ str(reporte._numberOfLastCreditNote)
		salida+= "\nNumero Ultimo Doc No Fiscal: "+ str(reporte._numberOfLastNonFiscal)
		salida+= "\nVentas Exento: "+ str(reporte._freeSalesTax)
		salida+= "\nBase Imponible Ventas IVA G: "+ str(reporte._generalRate1Sale)
		salida+= "\nImpuesto IVA G: "+ str(reporte._generalRate1Tax)
		salida+= "\nBase Imponible Ventas IVA R: "+ str(reporte._reducedRate2Sale)
		salida+= "\nImpuesto IVA R: "+ str(reporte._reducedRate2Tax)
		salida+= "\nBase Imponible Ventas IVA A: "+ str(reporte._additionalRate3Sal)
		salida+= "\nImpuesto IVA A: "+ str(reporte._additionalRate3Tax)
		salida+= "\nNota de Debito Exento: "+ str(reporte._freeTaxDebit)
		salida+= "\nBI IVA G en Nota de Debito: "+ str(reporte._generalRateDebit)
		salida+= "\nImpuesto IVA G en Nota de Debito: "+ str(reporte._generalRateTaxDebit)
		salida+= "\nBI IVA R en Nota de Debito: "+ str(reporte._reducedRateDebit)
		salida+= "\nImpuesto IVA R en Nota de Debito: "+ str(reporte._reducedRateTaxDebit)
		salida+= "\nBI IVA A en Nota de Debito: "+ str(reporte._additionalRateDebit)
		salida+= "\nImpuesto IVA A en Nota de Debito: "+ str(reporte._additionalRateTaxDebit)
		salida+= "\nNota de Credito Exento: "+ str(reporte._freeTaxDevolution)
		salida+= "\nBI IVA G en Nota de Credito: "+ str(reporte._generalRateDevolution)
		salida+= "\nImpuesto IVA G en Nota de Credito: "+ str(reporte._generalRateTaxDevolution)
		salida+= "\nBI IVA R en Nota de Credito: "+ str(reporte._reducedRateDevolution)
		salida+= "\nImpuesto IVA R en Nota de Credito: "+ str(reporte._reducedRateTaxDevolution)
		salida+= "\nBI IVA A en Nota de Credito: "+ str(reporte._additionalRateDevolution)
		salida+= "\nImpuesto IVA A en Nota de Credito: "+ str(reporte._additionalRateTaxDevolution)
		self.txt_informacion.setText(salida)

	def obtener_reporteX(self):
		reporte = self.printer.GetXReport()
		return reporte

	def ImpZpornumero(self):
		n_ini = self.imp_num_ini.value()
		n_fin = self.imp_num_fin.value()
		self.printer.PrintZReport("A",n_ini,n_fin)

	def ImpZporfecha(self):
		n_ini = self.imp_date_ini.date().toPyDate()
		n_fin = self.imp_date_fin.date().toPyDate()
		self.printer.PrintZReport("A",n_ini,n_fin)

	def factura(self, **params):	
		metodos_pago = {"TRANSFERENCE":"TRANSFERENCIA", "MOBILE PAYMENT":"PAGO MOVIL", "CASH": "EFECTIVO", "CARD":"TARJETA DEBITO",\
			 "WALLET": "TRANSFERENCIA", "CREDIT": "CREDITO"}
		self.printer.SendCmd(str(f"i00CLIENTE: {params.get('cliente')}"))
		self.printer.SendCmd(str(f"i01DOCUMENTO: {params.get('documento')}"))
		self.printer.SendCmd(str(f"i02DIRECCION: {params.get('direccion')}"))
		self.printer.SendCmd(str(f"i03TELEFONO: {params.get('telefono')}"))
		self.printer.SendCmd(str(f"i04CAJERO: {params.get('cajero').get('seller')}"))
		self.printer.SendCmd(str(f"i05{params.get('cajero').get('safeBox')}"))
		for producto in params.get("lista_productos"):
			self.printer.SendCmd(producto)
		self.printer.SendCmd(str("3"))
		if len(params.get("pago")) > 1:
			for index, metodo in enumerate(params.get("pago"), start=1):
				p_entero, p_decimal = metodo.get("amount").split('.')
				tipo = metodos_pago.get(metodo.get("paymentMethod"))
				self.printer.SendCmd(str(f"20{index}{(('0') * (10 - len(p_entero))) + p_entero}{p_decimal}{tipo}")) # Tipo de pago
		else:
			self.printer.SendCmd(str(f"101{metodos_pago.get(params.get('pago')[0].get('paymentMethod'))}"))

	def facturaper(self):
		#Factura Personalizada
		self.printer.SendCmd(str("iR*21.122.012"))
		self.printer.SendCmd(str("iS*Pedro Perez"))
		self.printer.SendCmd(str("i00Direccion: Ppal Siempre Viva"))
		self.printer.SendCmd(str("i01Telefono: +58(212)555-55-55"))
		self.printer.SendCmd(str("i02CAJERO: 00001"))
		self.printer.SendCmd(str("@COMMENT/COMENTARIO"))
		self.printer.SendCmd(str(" 000000030000001000Tax Free/Producto Exento"))
		self.printer.SendCmd(str("!000000050000001000Tax Rate 1/Producto Tasa General"))
		self.printer.SendCmd(str('"' + "000000070000001000Tax Rate 2/ Producto Tasa Reducida"))
		self.printer.SendCmd(str("#000000090000001000Tax Rate 3/ Producto Tasa Adicional"))
		self.printer.SendCmd(str("3"))
		self.printer.SendCmd(str("101"))

	def facturaanu(self):
		#Factura Anulada
		self.printer.SendCmd(str("iR*21.122.012"))
		self.printer.SendCmd(str("iS*Pedro Perez"))
		self.printer.SendCmd(str("i00Direccion: Ppal Siempre Viva"))
		self.printer.SendCmd(str("i01Telefono: +58(212)555-55-55"))
		self.printer.SendCmd(str("i02CAJERO: 00001"))
		self.printer.SendCmd(str("@COMMENT/COMENTARIO"))
		self.printer.SendCmd(str(" 000000030000001000Tax Free/Producto Exento"))
		self.printer.SendCmd(str("!000000050000001000Tax Rate 1/Producto Tasa General"))
		self.printer.SendCmd(str('"' + "000000070000001000Tax Rate 2/ Producto Tasa Reducida"))
		self.printer.SendCmd(str("#000000090000001000Tax Rate 3/ Producto Tasa Adicional"))
		self.printer.SendCmd(str("7"))

	def documentoNF(self):
		#Documento No Fiscal
		self.printer.SendCmd(str("80$Documento de Prueba"))
		self.printer.SendCmd(str("80¡Esto es un documento de texto"))
		self.printer.SendCmd(str("80!Es un documento no fiscal"))
		self.printer.SendCmd(str("80*Es bastante util y versatil"))
		self.printer.SendCmd(str("810Fin del Documento no Fiscal"))

	def notaCredito(self, **params):
		metodos_pago = {"TRANSFERENCE":"TRANSFERENCIA", "MOBILE PAYMENT":"PAGO MOVIL", "CASH": "EFECTIVO", "CARD":"TARJETA DEBITO",\
				"WALLET": "TRANSFERENCIA"}
		#Nota de Credito
		self.printer.SendCmd(f"iR*{params.get('documento')}")
		self.printer.SendCmd(f"iS*{params.get('cliente')}")
		self.printer.SendCmd(f"i00TELEFONO: {params.get('telefono')}")
		self.printer.SendCmd(f"i02DIRECCION: {params.get('direccion')}")
		self.printer.SendCmd(f"iF*{params.get('n_factura')}")
		self.printer.SendCmd(f"iD*{dt.now().strftime('%d/%m/%y')}")
		self.printer.SendCmd(f"iI*{params.get('serial')}")
		for producto in params.get("lista_productos"):
			self.printer.SendCmd(producto)
		self.printer.SendCmd("3")
		if len(params.get("pago")) > 1:
			for index, metodo in enumerate(params.get("pago"), start=1):
				p_entero, p_decimal = metodo.get("amount").split('.')
				tipo = metodos_pago.get(metodo.get("paymentMethod"))
				self.printer.SendCmd(str(f"20{index}{(('0') * (10 - len(p_entero))) + p_entero}{p_decimal}{tipo}")) # Tipo de pago
		else:
			self.printer.SendCmd(str(f"101{metodos_pago.get(params.get('pago')[0].get('paymentMethod'))}"))

	def notaDebito(self):
		self.printer.SendCmd(str("iR*21.122.012"))
		self.printer.SendCmd(str("iS*Pedro Perez"))
		self.printer.SendCmd(str("iF*00000000001"))
		self.printer.SendCmd(str("iD*22/08/2016"))
		self.printer.SendCmd(str("iI*Z1F1234567"))
		self.printer.SendCmd(str("i00Direccion: Ppal Siempre Viva"))
		self.printer.SendCmd(str("i01Telefono: +58(212)555-55-55"))
		self.printer.SendCmd(str("i02CAJERO: 00001"))
		self.printer.SendCmd(str("BCOMENTARIO NOTA DE DEBITO"))
		self.printer.SendCmd(str("`0" + "000000003000000100Tax Free/Producto Exento"))
		self.printer.SendCmd(str("`1" + "100000005000000100Tax Rate 1/Producto Tasa General"))
		self.printer.SendCmd(str("`2" + "200000007000000100Tax Rate 2/ Producto Tasa Reducida"))
		self.printer.SendCmd(str("`3" + "300000009000000100Tax Rate 3/ Producto Tasa Adicional"))
		self.printer.SendCmd(str("3"))
		self.printer.SendCmd(str("101"))

	def ReimprimirFacturas(self, value):
		value = value[1:]
		n_ini = value
		n_fin = value

		starString = str(n_ini)
		while (len(starString) < 7):
			starString = "0" + starString
		endString = str(n_fin)
		while (len(endString) < 7):
			endString = "0" + endString
		self.printer.SendCmd("RF" + starString + endString)

	def ObtZpornumero(self):
		n_ini = self.obt_num_ini.value()
		n_fin = self.obt_num_fin.value()
		reportes = self.printer.GetZReport("A",n_ini,n_fin)
		CR = len(reportes)
		Enc = "Lista de Reportes\n"+"\n"
		salida = ""
		for NR in range(CR):
			salida+= "Numero de Reporte Z: "+ str(reportes[NR]._numberOfLastZReport)
			salida+= "\nFecha Ultimo Reporte Z: "+ str(reportes[NR]._zReportDate)
			salida+= "\nHora Ultimo Reporte Z: "+ str(reportes[NR]._zReportTime)
			salida+= "\nNumero Ultima Factura: "+ str(reportes[NR]._numberOfLastInvoice)
			salida+= "\nFecha Ultima Factura: "+ str(reportes[NR]._lastInvoiceDate)
			salida+= "\nHora Ultima Factura: "+ str(reportes[NR]._lastInvoiceTime)
			salida+= "\nNumero Ultima Nota de Credito: "+ str(reportes[NR]._numberOfLastCreditNote)
			salida+= "\nNumero Ultima Nota de Debito: "+ str(reportes[NR]._numberOfLastDebitNote)
			salida+= "\nNumero Ultimo Doc No Fiscal: "+ str(reportes[NR]._numberOfLastNonFiscal)
			salida+= "\nVentas Exento: "+ str(reportes[NR]._freeSalesTax)
			salida+= "\nBase Imponible Ventas IVA G: "+ str(reportes[NR]._generalRate1Sale)
			salida+= "\nImpuesto IVA G: "+ str(reportes[NR]._generalRate1Tax)
			salida+= "\nBase Imponible Ventas IVA R: "+ str(reportes[NR]._reducedRate2Sale)
			salida+= "\nImpuesto IVA R: "+ str(reportes[NR]._reducedRate2Tax)
			salida+= "\nBase Imponible Ventas IVA A: "+ str(reportes[NR]._additionalRate3Sal)
			salida+= "\nImpuesto IVA A: "+ str(reportes[NR]._additionalRate3Tax)
			salida+= "\nNota de Debito Exento: "+ str(reportes[NR]._freeTaxDebit)
			salida+= "\nBI IVA G en Nota de Debito: "+ str(reportes[NR]._generalRateDebit)
			salida+= "\nImpuesto IVA G en Nota de Debito: "+ str(reportes[NR]._generalRateTaxDebit)
			salida+= "\nBI IVA R en Nota de Debito: "+ str(reportes[NR]._reducedRateDebit)
			salida+= "\nImpuesto IVA R en Nota de Debito: "+ str(reportes[NR]._reducedRateTaxDebit)
			salida+= "\nBI IVA A en Nota de Debito: "+ str(reportes[NR]._additionalRateDebit)
			salida+= "\nImpuesto IVA A en Nota de Debito: "+ str(reportes[NR]._additionalRateTaxDebit)
			salida+= "\nNota de Credito Exento: "+ str(reportes[NR]._freeTaxDevolution)
			salida+= "\nBI IVA G en Nota de Credito: "+ str(reportes[NR]._generalRateDevolution)
			salida+= "\nImpuesto IVA G en Nota de Credito: "+ str(reportes[NR]._generalRateTaxDevolution)
			salida+= "\nBI IVA R en Nota de Credito: "+ str(reportes[NR]._reducedRateDevolution)
			salida+= "\nImpuesto IVA R en Nota de Credito: "+ str(reportes[NR]._reducedRateTaxDevolution)
			salida+= "\nBI IVA A en Nota de Credito: "+ str(reportes[NR]._additionalRateDevolution)
			salida+= "\nImpuesto IVA A en Nota de Credito: "+ str(reportes[NR]._additionalRateTaxDevolution)+"\n"+"\n"
			print(salida)			
		self.txt_informacion.setText(Enc+salida)

	def ObtZporfecha(self):
		n_ini = self.obt_date_ini.date().toPyDate()
		n_fin = self.obt_date_fin.date().toPyDate()
		reportes = self.printer.GetZReport("A",n_ini,n_fin)
		CR = len(reportes)
		Enc = "Lista de Reportes\n"+"\n"
		salida = ""
		for NR in range(CR):
			salida+= "Numero de Reporte Z: "+ str(reportes[NR]._numberOfLastZReport) 
			salida+= "\nFecha Ultimo Reporte Z: "+ str(reportes[NR]._zReportDate) 
			salida+= "\nHora Ultimo Reporte Z: "+ str(reportes[NR]._zReportTime) 
			salida+= "\nNumero Ultima Factura: "+ str(reportes[NR]._numberOfLastInvoice) 
			salida+= "\nFecha Ultima Factura: "+ str(reportes[NR]._lastInvoiceDate) 
			salida+= "\nHora Ultima Factura: "+ str(reportes[NR]._lastInvoiceTime)
			salida+= "\nNumero Ultima Nota de Credito: "+ str(reportes[NR]._numberOfLastCreditNote)
			salida+= "\nNumero Ultima Nota de Debito: "+ str(reportes[NR]._numberOfLastDebitNote)			
			salida+= "\nNumero Ultimo Doc No Fiscal: "+ str(reportes[NR]._numberOfLastNonFiscal)
			salida+= "\nVentas Exento: "+ str(reportes[NR]._freeSalesTax)
			salida+= "\nBase Imponible Ventas IVA G: "+ str(reportes[NR]._generalRate1Sale)
			salida+= "\nImpuesto IVA G: "+ str(reportes[NR]._generalRate1Tax)
			salida+= "\nBase Imponible Ventas IVA R: "+ str(reportes[NR]._reducedRate2Sale)
			salida+= "\nImpuesto IVA R: "+ str(reportes[NR]._reducedRate2Tax)
			salida+= "\nBase Imponible Ventas IVA A: "+ str(reportes[NR]._additionalRate3Sal)
			salida+= "\nImpuesto IVA A: "+ str(reportes[NR]._additionalRate3Tax)
			salida+= "\nNota de Debito Exento: "+ str(reportes[NR]._freeTaxDebit)
			salida+= "\nBI IVA G en Nota de Debito: "+ str(reportes[NR]._generalRateDebit)
			salida+= "\nImpuesto IVA G en Nota de Debito: "+ str(reportes[NR]._generalRateTaxDebit)
			salida+= "\nBI IVA R en Nota de Debito: "+ str(reportes[NR]._reducedRateDebit)
			salida+= "\nImpuesto IVA R en Nota de Debito: "+ str(reportes[NR]._reducedRateTaxDebit)
			salida+= "\nBI IVA A en Nota de Debito: "+ str(reportes[NR]._additionalRateDebit)
			salida+= "\nImpuesto IVA A en Nota de Debito: "+ str(reportes[NR]._additionalRateTaxDebit)
			salida+= "\nNota de Credito Exento: "+ str(reportes[NR]._freeTaxDevolution)
			salida+= "\nBI IVA G en Nota de Credito: "+ str(reportes[NR]._generalRateDevolution)
			salida+= "\nImpuesto IVA G en Nota de Credito: "+ str(reportes[NR]._generalRateTaxDevolution)
			salida+= "\nBI IVA R en Nota de Credito: "+ str(reportes[NR]._reducedRateDevolution)
			salida+= "\nImpuesto IVA R en Nota de Credito: "+ str(reportes[NR]._reducedRateTaxDevolution)
			salida+= "\nBI IVA A en Nota de Credito: "+ str(reportes[NR]._additionalRateDevolution)
			salida+= "\nImpuesto IVA A en Nota de Credito: "+ str(reportes[NR]._additionalRateTaxDevolution)+"\n"+"\n"
			print(salida)
		self.txt_informacion.setText(Enc+salida)