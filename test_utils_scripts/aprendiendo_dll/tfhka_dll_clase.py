import clr
from System.Reflection import Assembly
import os


class FiscalPrinter:
    def __init__(self, dll_path: str):
        self.assembly_path = os.path.abspath(dll_path)
        Assembly.LoadFrom(self.assembly_path)
        clr.AddReference("TfhkaNet")
        from TfhkaNet.IF.VE import Tfhka

        self.impresora = Tfhka()

    def open_port(self, port_comm: str) -> bool:
        resultado = self.impresora.OpenFpCtrl(port_comm)
        return resultado

    def printer_check(self) -> bool:
        resultado = self.impresora.CheckFPrinter()
        return resultado

    def send_command(self, comando: str) -> bool:
        resultado = self.impresora.SendCmd(comando)
        return resultado

    def report_x(self) -> bool:
        resultado = self.impresora.PrintXReport()
        return resultado

    def close_port(self) -> bool:
        resultado = self.impresora.CloseFpCtrl()
        return resultado


if __name__ == "__main__":
    dll_path = "./library/TfhkaNet.dll"
    printer = FiscalPrinter(dll_path)

    if printer.open_port("COM9"):
        print("Conexión abierta con éxito")

        if printer.printer_check():
            print("La impresora está funcionando correctamente")

        printer.report_x()
        printer.close_port()
    else:
        print("No se pudo abrir la conexión con la impresora")
