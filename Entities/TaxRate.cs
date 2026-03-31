using System.ComponentModel.DataAnnotations;

namespace AccountingERP.Infrastructure.Entities
{
    public class TaxRate : BaseEntity
    {
        public Guid TaxId { get; set; }
        public Tax Tax { get; set; } = null!;

        public decimal Rate { get; set; }

        [StringLength(100)]
        public string Name { get; set; } = string.Empty; // e.g., "Standard Rate", "Lower Rate", etc.

        public string? HSNCode { get; set; }  // For GST rates based on HSN

        public decimal? MinAmount { get; set; } // Minimum amount for rate applicability

        public decimal? MaxAmount { get; set; } // Maximum amount for rate applicability

        public DateTime EffectiveFrom { get; set; }

        public DateTime? EffectiveTo { get; set; }

        public bool IsActive { get; set; } = true;
    }
} 