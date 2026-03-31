using System.ComponentModel.DataAnnotations;

namespace AccountingERP.Infrastructure.Entities
{
    public class LedgerOpeningBalance : BaseEntity
    {
        [Required]
        public Guid LedgerId { get; set; }
        
        [Required]
        public Guid FinancialYearId { get; set; }
        
        [Required]
        public DateTime OpeningDate { get; set; }
        
        [Required]
        public decimal OpeningBalance { get; set; }
        
        
        [StringLength(6)]
        public string BalanceType { get; set; } = string.Empty; // 'D' for Debit, 'C' for Credit
        
        // Navigation properties
        public Ledger Ledger { get; set; } = null!;
        public FinancialYear FinancialYear { get; set; } = null!;
    }
}