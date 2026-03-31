



namespace AccountingERP.Infrastructure.Entities
{
    public class UserCompany
    {
        public Guid Id { get; set; }
        public string UserId { get; set; }
        public Guid CompanyId { get; set; }
        public Guid? RoleId { get; set; }
        
        // Deprecated: Keep for backward compatibility during migration
        public string? Role { get; set; }
     
        
        // Navigation properties     
        public Company Company { get; set; }
        public CompanyRole? CompanyRole { get; set; }
    }
}
