

namespace AccountingERP.Infrastructure.Entities
{
    public class ProductAttribute : BaseEntity
    {
        // Foreign keys
        public Guid ProductId { get; set; }
        public Guid AttributeId { get; set; }
        public Guid CompanyId { get; set; }
        
        // Additional properties
        public bool IsActive { get; set; } = true;
        
        // Navigation properties
        public Product Product { get; set; } = null!;
        public Attribute Attribute { get; set; } = null!;
        public Company Company { get; set; } = null!;
    }
} 