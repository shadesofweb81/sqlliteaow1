using System.ComponentModel.DataAnnotations;

namespace AccountingERP.Infrastructure.Entities
{
    public class FinancialYear : BaseEntity
    {
        [Required]
        public Guid CompanyId { get; set; }
        
        [Required]
        [StringLength(20)]
        public string YearLabel { get; set; } = string.Empty; // e.g. "2025-2026"
        
        [Required]
        public DateTime StartDate { get; set; }
        
        [Required]
        public DateTime EndDate { get; set; }
        
        public bool IsActive { get; set; } = true;
        
        // Navigation properties
        public Company Company { get; set; } = null!;
        public ICollection<LedgerOpeningBalance> LedgerOpeningBalances { get; set; } = new HashSet<LedgerOpeningBalance>();
        public ICollection<ProductOpeningStock> ProductOpeningStocks { get; set; } = new HashSet<ProductOpeningStock>();
    }
}