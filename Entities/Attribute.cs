

namespace AccountingERP.Infrastructure.Entities
{
    public class Attribute : BaseEntity
    {
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty; 
        public bool IsRequired { get; set; }
        public bool IsActive { get; set; } = true;
        public int SortOrder { get; set; }
        
        // Foreign keys
        public Guid CompanyId { get; set; }
        
        // Navigation properties
        public Company Company { get; set; } = null!;
        public ICollection<AttributeOption> AttributeOptions { get; set; } = new HashSet<AttributeOption>();
        public ICollection<ProductAttribute> ProductAttributes { get; set; } = new HashSet<ProductAttribute>();
    }
} 