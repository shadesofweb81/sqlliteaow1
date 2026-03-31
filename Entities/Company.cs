namespace AccountingERP.Infrastructure.Entities
{
    public class Company : BaseEntity
    {
        public string Name { get; set; } = string.Empty;
        public string? Address { get; set; } = string.Empty;
        public string? City { get; set; } = string.Empty;
        public string State { get; set; } = string.Empty;
        public string StateCode { get; set; } = string.Empty;
        public string GSTIN { get; set; } = string.Empty;
        public string? ZipCode { get; set; } = string.Empty;
        public string Country { get; set; } = string.Empty;
        public string? Phone { get; set; } = string.Empty;
        public string Email { get; set; } = string.Empty;
        public string? Website { get; set; } = string.Empty;
        public string? TaxId { get; set; } = string.Empty;
        public string LogoUrl { get; set; } = string.Empty;
        public string Currency { get; set; } = "INR";
        public DateTime? StartingFinancialYearDate { get; set; }

        // Bank Details
        public string? BankName { get; set; }
        public string? AccountNumber { get; set; }
        public string? IFSCCode { get; set; }
        public string? AccountHolderName { get; set; }
        public string? BranchName { get; set; }
        public string? SwiftCode { get; set; }

        // Terms and Conditions
        public string? TermsAndConditions { get; set; }

        // Billing Address
        public string? BillingAddress { get; set; }
        public string? BillingCity { get; set; }
        public string? BillingState { get; set; }
        public string? BillingStateCode { get; set; }
        public string? BillingZipCode { get; set; }
        public string? BillingCountry { get; set; }

        // Navigation properties
        public ICollection<UserCompany> UserCompanies { get; set; } = new List<UserCompany>();
        public ICollection<Product> Products { get; set; } = new HashSet<Product>();
        public ICollection<Ledger> Ledgers { get; set; } = new List<Ledger>();
        public ICollection<Transaction> Transactions { get; set; } = new HashSet<Transaction>();
        public ICollection<Tax> Taxes { get; set; } = new List<Tax>();
        public ICollection<TransactionTypeSettings> TransactionTypeSettings { get; set; } = new List<TransactionTypeSettings>();
        public ICollection<CompanyRecharge> CompanyRecharges { get; set; } = new List<CompanyRecharge>();
        public ICollection<FinancialYear> FinancialYears { get; set; } = new HashSet<FinancialYear>();
    }
} 
