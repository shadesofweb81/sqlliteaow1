using System.ComponentModel.DataAnnotations;

namespace AccountingERP.Infrastructure.Entities
{
    public class Ledger : BaseEntity
    {
        [Required]
        [StringLength(100)]
        public string Name { get; set; } = string.Empty;

        [Required]
        [StringLength(50)]
        public string Type { get; set; } = string.Empty;  // e.g., "Customer", "Supplier", "Bank", "Tax", etc.

        [Required]
        [StringLength(50)]
        public string RootCategory { get; set; } = string.Empty;

        [StringLength(50)]
        public string Code { get; set; } = string.Empty;

        [StringLength(200)]
        public string? Address { get; set; }

        [StringLength(100)]
        public string? City { get; set; }

        [StringLength(50)]
        public string? State { get; set; }

        [StringLength(20)]
        public string? ZipCode { get; set; }

        [StringLength(100)]
        public string? Country { get; set; }

        [StringLength(30)]
        public string? Phone { get; set; }

        [StringLength(100)]
        [EmailAddress]
        public string? Email { get; set; }

        [StringLength(100)]
        [Url]
        public string? Website { get; set; }

        [StringLength(50)]
        public string? TaxId { get; set; }

        public bool IsGroup { get; set; }
        public bool? IsRegistered { get; set; }

        // Tax-specific fields (used when Type = "Tax")
        [StringLength(50)]
        public string? TaxClass { get; set; } // e.g., "CGST", "SGST", "IGST", "TDS", "TCS", etc.

        public decimal? TaxRate { get; set; }

        public bool IsCreditAllowed { get; set; } // Whether input credit is allowed

        [StringLength(500)]
        public string? Description { get; set; }

        [StringLength(50)]
        public string? ReturnFormNumber { get; set; }

        public Guid? TaxEntityId { get; set; } // FK to Tax entity
        public Tax? TaxEntity { get; set; }

        public Guid? ReceivableLedgerId { get; set; }
        public Guid? PayableLedgerId { get; set; }



        // Bank Details
        [StringLength(50)]
        public string? AccountHolderName { get; set; }

        [StringLength(50)]
        public string? AccountNumber { get; set; }

        [StringLength(50)]
        public string? BankName { get; set; }
        [StringLength(50)]
        public string? Branch { get; set; }

        [StringLength(50)]
        public string? IFSCCode { get; set; } = null;

        // Parent-Child relationship
        public Guid? ParentId { get; set; }
        public Ledger? Parent { get; set; }
        public ICollection<Ledger> Children { get; set; } = new HashSet<Ledger>();

        // Navigation properties
        public Guid CompanyId { get; set; }
        public Company Company { get; set; } = null!;
        public ICollection<Transaction> Transactions { get; set; } = new HashSet<Transaction>();
        public ICollection<LedgerOpeningBalance> LedgerOpeningBalances { get; set; } = new HashSet<LedgerOpeningBalance>();
    }
}