

namespace AccountingERP.Infrastructure.Entities
{
    public class AttributeOption : BaseEntity
    {
        public string Value { get; set; } = string.Empty;
        public string DisplayName { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public bool IsActive { get; set; } = true;
        public int SortOrder { get; set; }
        
        // Foreign keys
        public Guid AttributeId { get; set; }
        public Guid CompanyId { get; set; }
        
        // Navigation properties
        public Attribute Attribute { get; set; } = null!;
        public Company Company { get; set; } = null!;
        public ICollection<ProductAttribute> ProductAttributes { get; set; } = new HashSet<ProductAttribute>();
        public ICollection<ProductVariantAttribute> ProductVariantAttributes { get; set; } = new HashSet<ProductVariantAttribute>();
    }
} 