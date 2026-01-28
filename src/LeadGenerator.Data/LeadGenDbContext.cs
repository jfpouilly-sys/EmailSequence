using LeadGenerator.Core.Entities;
using LeadGenerator.Core.Enums;
using Microsoft.EntityFrameworkCore;
using LeadGenerator.Data.Configurations;

namespace LeadGenerator.Data;

public class LeadGenDbContext : DbContext
{
    public LeadGenDbContext(DbContextOptions<LeadGenDbContext> options) : base(options)
    {
    }

    // DbSets
    public DbSet<User> Users { get; set; }
    public DbSet<MailAccount> MailAccounts { get; set; }
    public DbSet<UserMailAccount> UserMailAccounts { get; set; }
    public DbSet<ContactList> ContactLists { get; set; }
    public DbSet<Contact> Contacts { get; set; }
    public DbSet<Campaign> Campaigns { get; set; }
    public DbSet<CampaignMailAccount> CampaignMailAccounts { get; set; }
    public DbSet<EmailStep> EmailSteps { get; set; }
    public DbSet<Attachment> Attachments { get; set; }
    public DbSet<CampaignContact> CampaignContacts { get; set; }
    public DbSet<EmailLog> EmailLogs { get; set; }
    public DbSet<DownloadLog> DownloadLogs { get; set; }
    public DbSet<SuppressionEntry> SuppressionList { get; set; }
    public DbSet<ABTest> ABTests { get; set; }
    public DbSet<AuditLog> AuditLogs { get; set; }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        // Apply all configurations
        modelBuilder.ApplyConfiguration(new UserConfiguration());
        modelBuilder.ApplyConfiguration(new MailAccountConfiguration());
        modelBuilder.ApplyConfiguration(new UserMailAccountConfiguration());
        modelBuilder.ApplyConfiguration(new ContactListConfiguration());
        modelBuilder.ApplyConfiguration(new ContactConfiguration());
        modelBuilder.ApplyConfiguration(new CampaignConfiguration());
        modelBuilder.ApplyConfiguration(new CampaignMailAccountConfiguration());
        modelBuilder.ApplyConfiguration(new EmailStepConfiguration());
        modelBuilder.ApplyConfiguration(new AttachmentConfiguration());
        modelBuilder.ApplyConfiguration(new CampaignContactConfiguration());
        modelBuilder.ApplyConfiguration(new EmailLogConfiguration());
        modelBuilder.ApplyConfiguration(new DownloadLogConfiguration());
        modelBuilder.ApplyConfiguration(new SuppressionEntryConfiguration());
        modelBuilder.ApplyConfiguration(new ABTestConfiguration());
        modelBuilder.ApplyConfiguration(new AuditLogConfiguration());

        // PostgreSQL enum type mapping
        modelBuilder.HasPostgresEnum<UserRole>("user_role");
        modelBuilder.HasPostgresEnum<CampaignStatus>("campaign_status");
        modelBuilder.HasPostgresEnum<ContactStatus>("contact_status");
        modelBuilder.HasPostgresEnum<DeliveryMode>("delivery_mode");
        modelBuilder.HasPostgresEnum<UnsubscribeScope>("unsubscribe_scope");
        modelBuilder.HasPostgresEnum<UnsubscribeSource>("unsubscribe_source");
        modelBuilder.HasPostgresEnum<ABTestElement>("ab_test_element");
        modelBuilder.HasPostgresEnum<ABTestStatus>("ab_test_status");
    }
}
