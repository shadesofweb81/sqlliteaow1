using System;

namespace AccountingERP.Infrastructure.Entities
{
    /// <summary>
    /// Tracks every local INSERT / UPDATE / SOFT_DELETE / HARD_DELETE so that
    /// offline changes can be replayed against the cloud PostgreSQL database.
    /// Maps to the PostgreSQL table "SyncLogs".
    /// SQLite counterpart: sync_log  (see Database/orm_models.py  –  SyncLog)
    /// </summary>
    public class SyncLog
    {
        public Guid Id { get; set; }

        /// <summary>Name of the affected table (e.g. "company", "ledger").</summary>
        public string TableName { get; set; } = string.Empty;

        /// <summary>Primary key of the affected row.</summary>
        public Guid RecordId { get; set; }

        /// <summary>INSERT | UPDATE | SOFT_DELETE | HARD_DELETE</summary>
        public string Action { get; set; } = string.Empty;

        /// <summary>JSON snapshot of changed fields (null for INSERT/DELETE).</summary>
        public string? ChangedData { get; set; }

        /// <summary>UTC timestamp when the local change was made.</summary>
        public DateTime CreatedOn { get; set; }

        /// <summary>True once the entry has been successfully pushed to the cloud.</summary>
        public bool IsSynced { get; set; } = false;

        /// <summary>UTC timestamp when the entry was synced.</summary>
        public DateTime? SyncedOn { get; set; }

        /// <summary>Last error message from a failed sync attempt.</summary>
        public string? SyncError { get; set; }

        /// <summary>Number of failed push attempts.</summary>
        public int RetryCount { get; set; } = 0;

        public SyncLog()
        {
            Id = Guid.NewGuid();
            CreatedOn = DateTime.UtcNow;
        }
    }
}
