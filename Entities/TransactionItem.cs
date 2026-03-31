using System.ComponentModel.DataAnnotations;

namespace AccountingERP.Infrastructure.Entities
{
    public class TransactionItem
    {
        public Guid Id { get; set; } = Guid.NewGuid();
        public Guid TransactionId { get; set; }
        public Transaction Transaction { get; set; } = null!;

        public Guid ProductId { get; set; }
        public Product Product { get; set; } = null!;

        [Required]
        public string Description { get; set; } = string.Empty;

        public decimal Quantity { get; set; }
        public decimal UnitPrice { get; set; }
        public decimal TaxRate { get; set; }
        public decimal TaxAmount { get; set; }
        public decimal DiscountRate { get; set; }
        public decimal DiscountAmount { get; set; }
        public decimal LineTotal { get; set; }
        public decimal CurrentQuantity { get; set; }

        public int SerialNumber { get; set; } // Serial number for ordering transaction items

        // Physical Stock / Stock Reconciliation fields
        /// <summary>
        /// Stock quantity in system before reconciliation (for PhysicalStock transactions)
        /// </summary>
        public decimal? SystemQuantity { get; set; }

        /// <summary>
        /// Actual physical stock counted (for PhysicalStock transactions)
        /// </summary>
        public decimal? PhysicalQuantity { get; set; }

        /// <summary>
        /// Reason for stock adjustment (for PhysicalStock transactions)
        /// </summary>
        [StringLength(500)]
        public string? AdjustmentReason { get; set; }

        // Navigation property for variants
        public ICollection<TransactionItemVariant> Variants { get; set; } = new List<TransactionItemVariant>();
    }
} 