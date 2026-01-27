using LeadGenerator.Core.Entities;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace LeadGenerator.Data.Configurations;

public class CampaignContactConfiguration : IEntityTypeConfiguration<CampaignContact>
{
    public void Configure(EntityTypeBuilder<CampaignContact> builder)
    {
        builder.ToTable("campaign_contacts");
        builder.HasKey(cc => new { cc.CampaignId, cc.ContactId });
        builder.Property(cc => cc.CampaignId).HasColumnName("campaign_id");
        builder.Property(cc => cc.ContactId).HasColumnName("contact_id");
        builder.Property(cc => cc.Status).HasColumnName("status").IsRequired();
        builder.Property(cc => cc.AssignedMailAccountId).HasColumnName("assigned_mail_account_id");
        builder.Property(cc => cc.CurrentStep).HasColumnName("current_step").IsRequired();
        builder.Property(cc => cc.LastEmailSentAt).HasColumnName("last_email_sent_at");
        builder.Property(cc => cc.NextEmailScheduledAt).HasColumnName("next_email_scheduled_at");
        builder.Property(cc => cc.RespondedAt).HasColumnName("responded_at");
        builder.Property(cc => cc.ABTestVariant).HasColumnName("ab_test_variant").HasMaxLength(1);
        builder.Property(cc => cc.CreatedAt).HasColumnName("created_at").IsRequired();
        builder.Property(cc => cc.UpdatedAt).HasColumnName("updated_at").IsRequired();

        builder.HasOne(cc => cc.Campaign)
            .WithMany(c => c.CampaignContacts)
            .HasForeignKey(cc => cc.CampaignId)
            .OnDelete(DeleteBehavior.Cascade);

        builder.HasOne(cc => cc.Contact)
            .WithMany(c => c.CampaignContacts)
            .HasForeignKey(cc => cc.ContactId)
            .OnDelete(DeleteBehavior.Cascade);

        builder.HasOne(cc => cc.AssignedMailAccount)
            .WithMany()
            .HasForeignKey(cc => cc.AssignedMailAccountId)
            .OnDelete(DeleteBehavior.SetNull);

        builder.HasIndex(cc => cc.Status);
        builder.HasIndex(cc => cc.NextEmailScheduledAt);
    }
}
