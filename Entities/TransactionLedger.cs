using System.ComponentModel.DataAnnotations;

namespace AccountingERP.Infrastructure.Entities
{
    public class TransactionLedger
    {
        public Guid Id { get; set; } = Guid.NewGuid();
        public int SerialNumber { get; set; } // Serial number for ordering transaction items
        public Guid TransactionId { get; set; }
        public Transaction Transaction { get; set; } = null!;

        public Guid LedgerId { get; set; }
        public Ledger Ledger { get; set; } = null!;

        [Required]
        public TransactionLedgerType Type { get; set; }

        public decimal Amount { get; set; }

        [StringLength(500)]
        public string? Description { get; set; }
        public bool? IsMainEntry { get; set; } // For primary ledger (customer/supplier)
        public bool? IsSystemEntry { get; set; } // For system generated entries (sales/purchase account)
    }
} 