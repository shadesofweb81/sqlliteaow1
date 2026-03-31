using System.ComponentModel.DataAnnotations;

namespace AccountingERP.Infrastructure.Entities
{
    public class Tax : BaseEntity
    {
        [Required]
        [StringLength(100)]
        public string Name { get; set; } = string.Empty;

        [StringLength(500)]
        public string Description { get; set; } = string.Empty;

        public TaxCategory Category { get; set; }

        public bool IsActive { get; set; } = true;

        public bool IsComposite { get; set; }

        public decimal DefaultRate { get; set; }

        public string? HSNCode { get; set; }  // For GST

        public string? SectionCode { get; set; } // For Income Tax

        public bool IsReverseChargeApplicable { get; set; }

        public bool IsDeductibleAtSource { get; set; }

        public bool IsCollectedAtSource { get; set; }

        [StringLength(50)]
        public string? ReturnFormNumber { get; set; } // e.g., GSTR-1, GSTR-2, ITR-1, etc.

        public Guid CompanyId { get; set; }
        public Company Company { get; set; } = null!;

        public ICollection<TaxComponent> Components { get; set; } = new HashSet<TaxComponent>();
        public ICollection<TaxRate> Rates { get; set; } = new HashSet<TaxRate>();
    }
} 