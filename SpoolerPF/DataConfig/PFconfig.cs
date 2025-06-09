using System;
using System.Collections.Generic;
using System.Data;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Xml;

namespace SpoolerPF.DataConfig
{
    public class PFconfig
    {
        static public string cPortComm;
        static public string cPrinterSerial;
        static public string cCompanyVAT;
        static public string cOdooUrl;
        static public string cOdooDb;
        static public string cOdooUser;
        static public string cOdooPass;
        static public string cOdooCompany;
        static public string cSQLServer;
        static public string cSQLPort;
        static public string cSQLDataBase;
        static public string cSQLUser;
        static public string cSQLPassword;
        static private string xmlFile = Path.Combine(Directory.GetCurrentDirectory(), "Parameters.xml");

        public PFconfig()
        {
            LoadXML();
        }

        private static void LoadXML()
        {

            XmlReader oReaderXML = XmlReader.Create(xmlFile);
            while (oReaderXML.Read())
            {
                if (oReaderXML.IsStartElement())
                {
                    switch (oReaderXML.Name.ToString())
                    {
                        case "PortComm":
                            cPortComm = oReaderXML.ReadString();
                            break;
                        case "PrinterSerial":
                            cPrinterSerial = oReaderXML.ReadString();
                            break;
                        case "CompanyVAT":
                            cCompanyVAT = oReaderXML.ReadString();
                            break;
                        case "OdooUrl":
                            cOdooUrl = oReaderXML.ReadString();
                            break;
                        case "OdooDb":
                            cOdooDb = oReaderXML.ReadString();
                            break;
                        case "OdooUser":
                            cOdooUser = oReaderXML.ReadString();
                            break;
                        case "OdooPass":
                            cOdooPass = oReaderXML.ReadString();
                            break;
                        case "OdooCompany":
                            cOdooCompany = oReaderXML.ReadString();
                            break;
                        case "SQLServer":
                            cSQLServer = oReaderXML.ReadString();
                            break;
                        case "SQLPort":
                            cSQLPort = oReaderXML.ReadString();
                            break;
                        case "SQLDataBase":
                            cSQLDataBase = oReaderXML.ReadString();
                            break;
                        case "SQLUser":
                            cSQLUser = oReaderXML.ReadString();
                            break;
                        case "SQLPassword":
                            cSQLPassword = oReaderXML.ReadString();
                            break;
                    }
                }
            }
            oReaderXML.Close();
        }

        public void RecordXML()
        {
            XmlWriter oWrite = XmlWriter.Create(xmlFile);



            //XmlDocument doc = new XmlDocument();
            //XmlDeclaration xmlDeclaration = doc.CreateXmlDeclaration("1.0", "UTF-8", null);
            //XmlElement root = doc.DocumentElement;
            //doc.InsertBefore(xmlDeclaration, root);
            //XmlElement element1 = doc.CreateElement(string.Empty, "cuerpo", string.Empty);
            //doc.AppendChild(element1);
            //XmlElement element2 = doc.CreateElement(string.Empty, "nivel1", string.Empty);
            //element1.AppendChild(element2);
            //XmlElement element3 = doc.CreateElement(string.Empty, "nivel2", string.Empty);
            //XmlText text1 = doc.CreateTextNode("texto");
            //element3.AppendChild(text1);
            //element2.AppendChild(element3);
            //XmlElement element4 = doc.CreateElement(string.Empty, "nivel3", string.Empty);
            //XmlText text2 = doc.CreateTextNode("más texto");
            //element4.AppendChild(text2);
            //element2.AppendChild(element4);
            //doc.Save("C://ruta//xml_ejemplo.xml");



        }

    }
}
