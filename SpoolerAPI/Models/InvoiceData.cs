using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;

namespace SpoolerAPI.Models
{
    public class InvoiceData
    {
        public string InvoiceType { get; set; }
        public string InvoiceDate { get; set; }
        public string Reference { get; set; }

        [Required]
        [RegularExpression(@"^[a-zA-Z]\d{9}$")]
        public string FiscalID { get; set; }

        [Required]
        public string Customer { get; set; }
        public string Address { get; set; }
        public string Phone { get; set; }
        public string Email { get; set; }

        [Required]
        [MinLength(1)]
        public List<Item> Items { get; set; } = new List<Item>();

        [Required]
        [MinLength(1)]
        public List<Payment> Payments { get; set; } = new List<Payment>();
    }

    public class Item
    {
        public string Product { get; set; }
        public double Quantity { get; set; }
        public double Price { get; set; }
        public double Tax { get; set; }
        public double Discount { get; set; }
        public string DiscountType { get; set; }
    }

    public class Payment
    {
        public string Code { get; set; }
        public double Amount { get; set; }
    }
}
