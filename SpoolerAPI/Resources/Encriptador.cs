using System;
using System.Security.Cryptography;
using System.Text;


namespace SpoolerAPI.Resources
{
    public class Encriptador
    {
        public static string EncriptarSerial(string serial, string clave)
        {
            byte[] claveBytes = Encoding.UTF8.GetBytes(clave);
            byte[] serialBytes = Encoding.UTF8.GetBytes(serial);

            using (Aes aes = Aes.Create())
            {
                aes.Key = claveBytes;
                aes.IV = new byte[16];

                using (var ms = new System.IO.MemoryStream())
                {
                    using (var cs = new CryptoStream(ms, aes.CreateEncryptor(), CryptoStreamMode.Write))
                    {
                        cs.Write(serialBytes, 0, serialBytes.Length);
                    }

                    byte[] encriptado = ms.ToArray();
                    return Convert.ToBase64String(encriptado);
                }
            }
        }

        //private static void Ejemplo()
        //{
        //    string serial = "A1B2C3D4E5";
        //    string clave = "miClaveSecreta";

        //    if (serial.Length == 10 && char.IsLetter(serial[0]) && char.IsDigit(serial[9]))
        //    {
        //        string serialEncriptado = EncriptarSerial(serial, clave);

        //        if (serialEncriptado == "fwYkR+Zf7zZ9d3yv0z2OJw=="
        //            || serialEncriptado == "mYJYRtLeM9I1X9tqGnLHJQ==")
        //        {
        //            Console.WriteLine("Serial válido");
        //        }
        //        else
        //        {
        //            Console.WriteLine("Serial inválido");
        //        }
        //    }
        //    else
        //    {
        //        Console.WriteLine("Serial inválido");
        //    }


        //    string serial = "A1B2C3D4E5";
        //    string clave = "miClaveSecreta";
        //    string serialEncriptado = Encriptador.EncriptarSerial(serial, clave);


        //}
    }
}
