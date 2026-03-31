using System.ComponentModel.DataAnnotations;

namespace AccountingERP.Infrastructure.Entities
{
    public class ProductOpeningStock : BaseEntity
    {
        [Required]
        public Guid ProductId { get; set; }
        
        [Required]
        public Guid FinancialYearId { get; set; }
        
        [Required]
        public DateTime OpeningDate { get; set; }
        
        [Required]
        public decimal Quantity { get; set; }
        
        [Required]
        public decimal Rate { get; set; }
        
        // Calculated property - will be configured as computed column in the database
        public decimal ValueAmount { get; set; }

        // Navigation properties
        public Product Product { get; set; } = null!;
        public FinancialYear FinancialYear { get; set; } = null!;
    }
}