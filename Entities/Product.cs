

namespace AccountingERP.Infrastructure.Entities
{
    public class Product : BaseEntity
    {
        public string ProductCode { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public decimal PurchasePrice { get; set; }
        public decimal SellingPrice { get; set; }
        public int StockQuantity { get; set; }
        public bool IsActive { get; set; }
        public string SKU { get; set; } = string.Empty;
        public string Barcode { get; set; } = string.Empty;        
        public string Unit { get; set; } = string.Empty;
        // Hierarchical structure
        public Guid? ParentId { get; set; }
        
        // Foreign keys
        public Guid CompanyId { get; set; }
        
        // Navigation properties
        public Product? Parent { get; set; }
        public ICollection<Product> Children { get; set; } = new HashSet<Product>();
        public Company Company { get; set; } = null!;
        public ICollection<ProductAttribute> ProductAttributes { get; set; } = new HashSet<ProductAttribute>();
        public ICollection<ProductVariant> ProductVariants { get; set; } = new HashSet<ProductVariant>();
        public ICollection<ProductOpeningStock> ProductOpeningStocks { get; set; } = new HashSet<ProductOpeningStock>();
       
    }
} 