using LeadGenerator.Core.Entities;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace LeadGenerator.Data.Configurations;

public class EmailLogConfiguration : IEntityTypeConfiguration<EmailLog>
{
    public void Configure(EntityTypeBuilder<EmailLog> builder)
    {
        builder.ToTable("email_logs");
        builder.HasKey(el => el.LogId);
        builder.Property(el => el.LogId).HasColumnName("log_id");
        builder.Property(el => el.CampaignId).HasColumnName("campaign_id");
        builder.Property(el => el.ContactId).HasColumnName("contact_id");
        builder.Property(el => el.StepId).HasColumnName("step_id");
        builder.Property(el => el.MailAccountId).HasColumnName("mail_account_id");
        builder.Property(el => el.Subject).HasColumnName("subject").HasMaxLength(500);
        builder.Property(el => el.SentAt).HasColumnName("sent_at").IsRequired();
        builder.Property(el => el.Status).HasColumnName("status").HasMaxLength(50).IsRequired();
        builder.Property(el => el.ErrorMessage).HasColumnName("error_message");
        builder.Property(el => el.OutlookEntryId).HasColumnName("outlook_entry_id").HasMaxLength(500);

        builder.HasOne(el => el.Campaign)
            .WithMany()
            .HasForeignKey(el => el.CampaignId)
            .OnDelete(DeleteBehavior.SetNull);

        builder.HasOne(el => el.Contact)
            .WithMany(c => c.EmailLogs)
            .HasForeignKey(el => el.ContactId)
            .OnDelete(DeleteBehavior.SetNull);

        builder.HasOne(el => el.EmailStep)
            .WithMany(es => es.EmailLogs)
            .HasForeignKey(el => el.StepId)
            .OnDelete(DeleteBehavior.SetNull);

        builder.HasOne(el => el.MailAccount)
            .WithMany(m => m.EmailLogs)
            .HasForeignKey(el => el.MailAccountId)
            .OnDelete(DeleteBehavior.SetNull);

        builder.HasIndex(el => el.CampaignId);
        builder.HasIndex(el => el.ContactId);
        builder.HasIndex(el => el.SentAt);
    }
}
