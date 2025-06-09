using System;
using System.Collections.Generic;
using Newtonsoft.Json;

namespace ModuloESCPOS.Models
{
    public class PrintDocument
    {
        [JsonProperty("customer_vat")]
        public string CustomerVat { get; set; }

        [JsonProperty("customer_name")]
        public string CustomerName { get; set; }

        [JsonProperty("customer_address")]
        public string CustomerAddress { get; set; }

        [JsonProperty("customer_phone")]
        public string CustomerPhone { get; set; }

        [JsonProperty("document_name")]
        public string DocumentName { get; set; }

        [JsonProperty("document_number")]
        public string DocumentNumber { get; set; }

        [JsonProperty("document_date")]
        public string DocumentDate { get; set; }

        [JsonProperty("document_currency")]
        public string DocumentCurrency { get; set; }

        [JsonProperty("items")]
        public List<PrintDocumentItem> Items { get; set; }

        [JsonProperty("payments")]
        public List<PrintDocumentPayment> Payments { get; set; }

        [JsonProperty("delivery_comments")]
        public List<string> DeliveryComments { get; set; }

        [JsonProperty("delivery_barcode")]
        public string DeliveryBarcode { get; set; }
    }

    public class PrintDocumentItem
    {
        [JsonProperty("item_ref")]
        public string ItemRef { get; set; }

        [JsonProperty("item_name")]
        public string ItemName { get; set; }

        [JsonProperty("item_quantity")]
        public decimal ItemQuantity { get; set; }

        [JsonProperty("item_price")]
        public decimal ItemPrice { get; set; }

        [JsonProperty("item_tax")]
        public decimal ItemTax { get; set; }

        [JsonProperty("item_discount")]
        public decimal ItemDiscount { get; set; }

        [JsonProperty("item_discount_type")]
        public string ItemDiscountType { get; set; }

        [JsonProperty("item_comment")]
        public string ItemComment { get; set; }

        public decimal Total => ItemQuantity * ItemPrice;
        public decimal TaxAmount => Total * (ItemTax / 100);
        public decimal TotalWithTax => Total + TaxAmount;
    }

    public class PrintDocumentPayment
    {
        [JsonProperty("payment_method")]
        public string PaymentMethod { get; set; }

        [JsonProperty("payment_name")]
        public string PaymentName { get; set; }

        [JsonProperty("payment_amount")]
        public decimal PaymentAmount { get; set; }
    }
}
