namespace AccountingERP.Infrastructure.Entities
{
    public class CompanyFeature
    {
        public Guid Id { get; set; }
        public string Name { get; set; } = string.Empty;
        public string Code { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public string Category { get; set; } = string.Empty;
        public bool IsSystemFeature { get; set; }
        public bool IsEnabled { get; set; }
        public DateTime CreatedOn { get; set; }

        // Navigation properties
        public ICollection<CompanyRoleFeature> RoleFeatures { get; set; } = new List<CompanyRoleFeature>();

        public CompanyFeature()
        {
            CreatedOn = DateTime.UtcNow;
            IsEnabled = true;
        }
    }
}


