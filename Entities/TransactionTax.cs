using System.ComponentModel.DataAnnotations;

namespace AccountingERP.Infrastructure.Entities
{
    public class TransactionTax
    {
        public Guid Id { get; set; } = Guid.NewGuid();
        public Guid TransactionId { get; set; }
        public Transaction Transaction { get; set; } = null!;

        public Guid TaxLedgerId { get; set; }
        public Ledger TaxLedger { get; set; } = null!;

        public decimal TaxableAmount { get; set; }

        public decimal TaxAmount { get; set; }

        [StringLength(50)]
        public string CalculationMethod { get; set; } = "ItemSubtotal"; // Default to ItemSubtotal

        public bool IsApplied { get; set; } = false;

        public DateTime? AppliedDate { get; set; }

        [StringLength(50)]
        public string? ReferenceNumber { get; set; }

        [StringLength(500)]
        public string? Description { get; set; }

        public int SerialNumber { get; set; } // Serial number for ordering taxes based on calculation method
    }
}