

namespace AccountingERP.Infrastructure.Entities
{
    public class ProductVariantAttribute : BaseEntity
    {
        // Foreign keys
        public Guid ProductVariantId { get; set; }
        public Guid AttributeId { get; set; }
        public Guid AttributeOptionId { get; set; }
        public Guid CompanyId { get; set; }
        
        // Additional properties
        public string CustomValue { get; set; } = string.Empty; // For custom values not in predefined options
        public bool IsActive { get; set; } = true;
        
        // Navigation properties
        public ProductVariant ProductVariant { get; set; } = null!;
        public Attribute Attribute { get; set; } = null!;
        public AttributeOption AttributeOption { get; set; } = null!;
        public Company Company { get; set; } = null!;
    }
} 