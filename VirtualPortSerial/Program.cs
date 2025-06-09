using System;
using System.IO.Ports;
using System.Text;

namespace VirtualPortSerial
{
    class Program
    {
        static void Main(string[] args)
        {
            // Crear un objeto SerialPort para el puerto virtual COM3
            var serialPort = new SerialPort("COM99", 9600, Parity.None, 8, StopBits.One);

            // Configurar el puerto serie
            serialPort.Open();
            serialPort.DataReceived += (sender, e) =>
            {
                // Leer los datos recibidos
                var buffer = new byte[serialPort.BytesToRead];
                serialPort.Read(buffer, 0, buffer.Length);
                var data = Encoding.ASCII.GetString(buffer);

                // Mostrar los datos recibidos en la consola
                Console.WriteLine($"Recibido: {data}");

                // Responder con una trama "true"
                var response = Encoding.ASCII.GetBytes("true");
                serialPort.Write(response, 0, response.Length);
            };

            // Mantener la aplicación en ejecución
            while (true)
            {
                // Esperar un tiempo antes de volver a escuchar
                System.Threading.Thread.Sleep(100);
            }
        }
    }
}
