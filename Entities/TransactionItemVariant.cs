using System.ComponentModel.DataAnnotations;

namespace AccountingERP.Infrastructure.Entities
{
    public class TransactionItemVariant
    {
        public Guid Id { get; set; } = Guid.NewGuid();
        public Guid TransactionItemId { get; set; }
        public TransactionItem TransactionItem { get; set; } = null!;

        public Guid ProductVariantId { get; set; }
        public ProductVariant ProductVariant { get; set; } = null!;

        [Required]
        public string VariantCode { get; set; } = string.Empty;

        [Required]
        public string VariantName { get; set; } = string.Empty;

        public decimal Quantity { get; set; }

        public decimal UnitPrice { get; set; }

        public decimal SellingPrice { get; set; }

        public decimal CurrentQuantity { get; set; }

        public int SerialNumber { get; set; }

        public string? Description { get; set; }
    }
} 