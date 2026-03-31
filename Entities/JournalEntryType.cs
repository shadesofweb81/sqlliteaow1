using System.Text.Json.Serialization;

namespace AccountingERP.Infrastructure.Entities
{
    public enum JournalEntryType
    {
        JournalEntry,
        OpeningBalance,
        SaleQuotation,
        SaleOrder,
        SaleInvoice,
        SaleReturn,
        PurchaseQuotation,
        PurchaseOrder,
        PurchaseBill,
        PurchaseReturn,
        BankPayment,
        BankReceipt,
        CashPayment,
        CashReceipt
    }

    public enum NatureOfTransaction
    {
        NotApplicable,
        RegisteredExpense,
        UnregisteredExpense,
        RCMExpense,
        ExemptExpense,
        NonGSTExpense,
        TaxAdjustment,
        AdvancePayment,
        TDSPayment,
        TCSPayment,
        RCMPayment,
        PaymentToGovernment
    }

    public enum TransactionType
    {
        SaleQuotation,
        SaleOrder,
        SaleInvoice,
        SaleReturn,
        PurchaseQuotation,
        PurchaseOrder,
        PurchaseBill,
        PurchaseReturn,
        BankPayment,
        BankReceipt,
        CashPayment,
        CashReceipt,
        JournalEntry,
        PhysicalStock
    }

    public enum TransactionStatus
    {
        Draft,
        Posted,
        Approved,
        Completed,
        Cancelled
    }

    public enum PaymentStatusType
    {
        Pending,
        Paid,
        Partial,
        Credit
    }
}
