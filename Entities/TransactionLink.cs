namespace AccountingERP.Infrastructure.Entities
{
    /// <summary>
    /// Generic self-referencing link between any two transactions.
    /// Examples:
    ///   PurchaseBill (From) → PurchaseOrder (To)
    ///   PurchaseBill (From) → MaterialReceiveVoucher (To)
    ///   SaleInvoice  (From) → SaleOrder (To)
    ///   SaleInvoice  (From) → SaleQuotation (To)
    /// </summary>
    public class TransactionLink
    {
        public Guid Id { get; set; } = Guid.NewGuid();

        // The derived / child transaction (e.g. PurchaseBill, SaleInvoice, GRN)
        public Guid FromTransactionId { get; set; }
        public Transaction FromTransaction { get; set; } = null!;

        // The source / parent transaction (e.g. PurchaseOrder, SaleOrder, SaleQuotation)
        public Guid ToTransactionId { get; set; }
        public Transaction ToTransaction { get; set; } = null!;

        public DateTime LinkedOn { get; set; } = DateTime.UtcNow;

        [System.ComponentModel.DataAnnotations.StringLength(500)]
        public string? Notes { get; set; }
    }
}
