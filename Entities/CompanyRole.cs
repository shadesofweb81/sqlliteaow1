namespace AccountingERP.Infrastructure.Entities
{
    public class CompanyRole
    {
        public Guid Id { get; set; }
        public Guid CompanyId { get; set; }
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public bool IsSystemRole { get; set; }
        public DateTime CreatedOn { get; set; }
        public DateTime? ModifiedOn { get; set; }

        // Navigation properties
        public Company Company { get; set; } = null!;
        public ICollection<CompanyRoleFeature> RoleFeatures { get; set; } = new List<CompanyRoleFeature>();
        public ICollection<UserCompany> UserCompanies { get; set; } = new List<UserCompany>();

        public CompanyRole()
        {
            CreatedOn = DateTime.UtcNow;
        }
    }
}
