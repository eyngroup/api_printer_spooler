using System;
using System.Collections.Generic;

namespace ModuloESCPOS.Models
{
    public class TicketData
    {
        public string RIF { get; set; }
        public string CompanyName { get; set; }
        public string Address { get; set; }
        public string CajaNumber { get; set; }
        
        public string CustomerName { get; set; }
        public string CustomerRIF { get; set; }
        public string StoreId { get; set; }
        public string SellerId { get; set; }
        public string SellerName { get; set; }

        public string InvoiceNumber { get; set; }
        public DateTime InvoiceDate { get; set; }
        public string InvoiceTime { get; set; }

        public List<TicketItem> Items { get; set; }
        public decimal Subtotal { get; set; }
        public decimal Tax { get; set; }
        public decimal Total { get; set; }

        public List<PaymentMethod> PaymentMethods { get; set; }

        public string ControlNumber { get; set; }
    }

    public class TicketItem
    {
        public string Code { get; set; }
        public string Description { get; set; }
        public decimal Quantity { get; set; }
        public decimal UnitPrice { get; set; }
        public decimal Total { get; set; }
    }

    public class PaymentMethod
    {
        public string Method { get; set; }
        public decimal Amount { get; set; }
        public decimal? ExchangeRate { get; set; }
        public decimal? IGTF { get; set; }
    }
}
