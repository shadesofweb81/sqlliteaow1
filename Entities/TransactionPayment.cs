
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace AccountingERP.Infrastructure.Entities
{
    /// <summary>
    /// Represents a payment allocation from a payment transaction to an invoice/bill
    /// </summary>
    public class TransactionPayment : BaseEntity
    {
        [Key]
        public Guid Id { get; set; }

        /// <summary>
        /// The payment transaction ID
        /// </summary>
        public Guid PaymentTransactionId { get; set; }

        [ForeignKey("PaymentTransactionId")]
        public Transaction PaymentTransaction { get; set; }

        /// <summary>
        /// The invoice/bill transaction being paid
        /// </summary>
        public Guid InvoiceTransactionId { get; set; }

        [ForeignKey("InvoiceTransactionId")]
        public Transaction InvoiceTransaction { get; set; }

        /// <summary>
        /// Payment ledger ID (Cash or Bank ledger)
        /// </summary>
        public Guid? PaymentLedgerId { get; set; }

        [ForeignKey("PaymentLedgerId")]
        public Ledger? PaymentLedger { get; set; }

        /// <summary>
        /// Amount of payment allocated to this invoice/bill
        /// </summary>
        [Column(TypeName = "decimal(18,2)")]
        public decimal Amount { get; set; }

        /// <summary>
        /// Date of payment
        /// </summary>
        public DateTime PaymentDate { get; set; }

        /// <summary>
        /// Payment method: Cash, Bank, Cheque
        /// </summary>
        [StringLength(50)]
        public string? PaymentMethod { get; set; }

        /// <summary>
        /// Payment gateway for bank payments: Google Pay, Phone Pe, Paytm, NEFT, RTGS, IMPS, UPI
        /// </summary>
        [StringLength(50)]
        public string? PaymentGateway { get; set; }

        /// <summary>
        /// Transaction/UTR number for bank payments
        /// </summary>
        [StringLength(100)]
        public string? TransactionUtrNumber { get; set; }

        /// <summary>
        /// Cheque number for cheque payments
        /// </summary>
        [StringLength(50)]
        public string? ChequeNumber { get; set; }

        /// <summary>
        /// Cheque date for cheque payments
        /// </summary>
        public DateTime? ChequeDate { get; set; }

        /// <summary>
        /// Notes for this payment
        /// </summary>
        [StringLength(500)]
        public string? Notes { get; set; }

        /// <summary>
        /// When this payment was created
        /// </summary>
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    }
} 