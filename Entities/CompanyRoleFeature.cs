namespace AccountingERP.Infrastructure.Entities
{
    public class CompanyRoleFeature
    {
        public Guid Id { get; set; }
        public Guid RoleId { get; set; }
        public Guid FeatureId { get; set; }
        public Guid CompanyId { get; set; }
       
        public bool CanCreate { get; set; }
        public bool CanRead { get; set; }
        public bool CanUpdate { get; set; }
        public bool CanDelete { get; set; }
        public bool CanAuthorize { get; set; }
        public DateTime CreatedOn { get; set; }

        // Navigation properties
        public CompanyRole Role { get; set; } = null!;
        public CompanyFeature Feature { get; set; } = null!;

        public CompanyRoleFeature()
        {
            CreatedOn = DateTime.UtcNow;
        }
    }


    public class UserCompanyRoleFeature
    {
        public Guid Id { get; set; }
        public Guid CompanyRoleFeatureId { get; set; }
        public Guid UserCompanyId { get; set; }
        public DateTime CreatedOn { get; set; }

        // Navigation properties
        public CompanyRoleFeature CompanyRoleFeature { get; set; } = null!;
        public UserCompany UserCompany { get; set; } = null!;

        public UserCompanyRoleFeature()
        {
            CreatedOn = DateTime.UtcNow;
        }
    }
}
