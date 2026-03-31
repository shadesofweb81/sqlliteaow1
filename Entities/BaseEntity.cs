using System;
using System.ComponentModel.DataAnnotations;

namespace AccountingERP.Infrastructure.Entities
{
    public abstract class BaseEntity
    {
        public Guid Id { get; set; }
        public DateTime CreatedOn { get; set; }
        public DateTime? ModifiedOn { get; set; }
        public string CreatedBy { get; set; } = string.Empty;
        public string ModifiedBy { get; set; } = string.Empty;
        public bool? Authorized { get; set; }
        public string? AuthorizedBy { get; set; } = string.Empty;
        public DateTime? AuthorizedOn { get; set; }
        public bool? IsDeleted { get; set; }
        public string? DeletedBy { get; set; } = string.Empty;
        public DateTime? DeletedOn { get; set; }

        [Timestamp]
        public byte[]? RowVersion { get; set; }

        protected BaseEntity()
        {
            Id = Guid.NewGuid();
            CreatedOn = DateTime.UtcNow;           
            IsDeleted = false;
            Authorized = false; // Default to not authorized
        }
    }
} 