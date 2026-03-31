using System.ComponentModel.DataAnnotations;

namespace AccountingERP.Infrastructure.Entities
{
    public class CompanyRecharge : BaseEntity
    {
        public Guid CompanyId { get; set; }
        public Company Company { get; set; } = null!;

        [Required]
        public decimal Amount { get; set; }

        [Required]
        public RechargePeriod Period { get; set; }

        [Required]
        public DateTime StartDate { get; set; }

        [Required]
        public DateTime EndDate { get; set; }

        [Required]
        public RechargeStatus RechargeStatus { get; set; }

        [StringLength(500)]
        public string? Description { get; set; }

        [StringLength(100)]
        public string? TransactionId { get; set; }

        [StringLength(50)]
        public string? PaymentMethod { get; set; }

        public DateTime? PaidOn { get; set; }

        [StringLength(100)]
        public string? PaidBy { get; set; }

        public bool IsActive { get; set; } = true;

        // Fixed pricing constants
        public const decimal MonthlyRate = 300m; // ₹300 per month
        public const decimal DailyRate = 10m; // ₹10 per day
    }

    public enum RechargePeriod
    {
        Daily = 0,
        Monthly = 1,
        Quarterly = 3,
        HalfYearly = 6,
        Yearly = 12
    }

    public enum RechargeStatus
    {
        Pending = 0,
        Paid = 1,
        Expired = 2,
        Cancelled = 3
    }
} 