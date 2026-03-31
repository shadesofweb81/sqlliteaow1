using System.ComponentModel.DataAnnotations;

namespace AccountingERP.Infrastructure.Entities
{
    public class Transaction : BaseEntity
    {
        [Required]
        [StringLength(50)]
        //auto generated unique transaction number (e.g., INV-0001, BILL-0001) based on the type and a sequence
        public string TransactionNumber { get; set; } = string.Empty;

        [StringLength(50)]
        public string? InvoiceNumber { get; set; }
        public DateTime TransactionDate { get; set; }

        public string FormType { get; set; } = string.Empty;


        [Required]
        public TransactionType Type { get; set; }
        public JournalEntryType? JournalEntryType { get; set; }
        public NatureOfTransaction? NatureOfTransactionTypes { get; set; }

      

        public DateTime DueDate { get; set; }

        [StringLength(500)]
        public string? Notes { get; set; }

        public decimal SubTotal { get; set; }
        public decimal TaxRate { get; set; }
        public decimal TaxAmount { get; set; }
        public decimal Discount { get; set; }
        public decimal DiscountAmount { get; set; }
        public decimal Freight { get; set; }
        public bool IsFreightIncluded { get; set; }
        public decimal RoundOff { get; set; }
        public decimal Total { get; set; }

        public decimal? PaidAmount { get; set; }
        public decimal? BalanceDue => Total - (PaidAmount ?? 0);
        // public bool IsPaid => (PaidAmount ?? 0) >= Total;

        public bool IsPaid { get; set; }

        public TransactionStatus Status { get; set; } = TransactionStatus.Draft;
        public PaymentStatusType PaymentStatus { get; set; } = PaymentStatusType.Credit;      
        public string? ReferenceNumber { get; set; }
        public string? PaymentMethod { get; set; }

        /// <summary>
        /// Indicates if the payment was made along with the transaction (invoice/bill).
        /// True = Payment received/made at the time of sale/purchase (no separate payment transaction)
        /// False = Separate payment transaction was created later or no payment yet
        /// </summary>
        public bool IsPaidWithTransaction { get; set; }

        // Navigation properties
        public Guid? CompanyId { get; set; }
        public Company Company { get; set; } = null!;

        public Guid? FinancialYearId { get; set; }
        public FinancialYear FinancialYear { get; set; } = null!;

        // Collection of ledger entries (both debit and credit)
        public ICollection<TransactionLedger> LedgerEntries { get; set; } = new HashSet<TransactionLedger>();

        // Collection of items in the transaction
        public ICollection<TransactionItem> Items { get; set; } = new HashSet<TransactionItem>();

        // Collection of taxes applied to the transaction
        public ICollection<TransactionTax> Taxes { get; set; } = new HashSet<TransactionTax>();

        // Collection of payments received (for invoices/bills)
        public ICollection<TransactionPayment> ReceivedPayments { get; set; } = new HashSet<TransactionPayment>();

        // Collection of payments made (for payment transactions)
        public ICollection<TransactionPayment> PaymentsMade { get; set; } = new HashSet<TransactionPayment>();

        // Links where this transaction is the derived/child (e.g. this Bill links TO a PurchaseOrder)
        public ICollection<TransactionLink> TransactionLinksFrom { get; set; } = new HashSet<TransactionLink>();

        // Links where this transaction is the source/parent (e.g. this PurchaseOrder is linked FROM a Bill)
        public ICollection<TransactionLink> TransactionLinksTo { get; set; } = new HashSet<TransactionLink>();
    }
}