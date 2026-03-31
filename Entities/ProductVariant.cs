

namespace AccountingERP.Infrastructure.Entities
{
    public class ProductVariant : BaseEntity
    {
        public string VariantCode { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public decimal PurchasePrice { get; set; }
        public decimal SellingPrice { get; set; }
        public int StockQuantity { get; set; }
        public int MinStockLevel { get; set; }
        public int MaxStockLevel { get; set; }
        public bool IsActive { get; set; } = true;
        public string SKU { get; set; } = string.Empty;
        public string Barcode { get; set; } = string.Empty;
        public decimal Weight { get; set; }
        public string Unit { get; set; } = string.Empty;
        public string ImageUrl { get; set; } = string.Empty;
        public int SortOrder { get; set; }
        
        // Foreign keys
        public Guid ProductId { get; set; }
        public Guid CompanyId { get; set; }
        
        // Navigation properties
        public Product Product { get; set; } = null!;
        public Company Company { get; set; } = null!;
        public ICollection<ProductVariantAttribute> ProductVariantAttributes { get; set; } = new HashSet<ProductVariantAttribute>();
    }
} 