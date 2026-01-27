using LeadGenerator.Core.Entities;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace LeadGenerator.Data.Configurations;

public class CampaignConfiguration : IEntityTypeConfiguration<Campaign>
{
    public void Configure(EntityTypeBuilder<Campaign> builder)
    {
        builder.ToTable("campaigns");
        builder.HasKey(c => c.CampaignId);
        builder.Property(c => c.CampaignId).HasColumnName("campaign_id");
        builder.Property(c => c.Name).HasColumnName("name").HasMaxLength(200).IsRequired();
        builder.Property(c => c.Description).HasColumnName("description");
        builder.Property(c => c.CampaignRef).HasColumnName("campaign_ref").HasMaxLength(20).IsRequired();
        builder.Property(c => c.OwnerUserId).HasColumnName("owner_user_id");
        builder.Property(c => c.ContactListId).HasColumnName("contact_list_id");
        builder.Property(c => c.Status).HasColumnName("status").IsRequired();
        builder.Property(c => c.InterEmailDelayMinutes).HasColumnName("inter_email_delay_minutes").IsRequired();
        builder.Property(c => c.SequenceStepDelayDays).HasColumnName("sequence_step_delay_days").IsRequired();
        builder.Property(c => c.SendingWindowStart).HasColumnName("sending_window_start").IsRequired();
        builder.Property(c => c.SendingWindowEnd).HasColumnName("sending_window_end").IsRequired();
        builder.Property(c => c.SendingDays).HasColumnName("sending_days").HasMaxLength(20).IsRequired();
        builder.Property(c => c.RandomizationMinutes).HasColumnName("randomization_minutes").IsRequired();
        builder.Property(c => c.DailySendLimit).HasColumnName("daily_send_limit").IsRequired();
        builder.Property(c => c.StartDate).HasColumnName("start_date");
        builder.Property(c => c.EndDate).HasColumnName("end_date");
        builder.Property(c => c.CreatedAt).HasColumnName("created_at").IsRequired();
        builder.Property(c => c.UpdatedAt).HasColumnName("updated_at").IsRequired();

        builder.HasOne(c => c.OwnerUser)
            .WithMany(u => u.Campaigns)
            .HasForeignKey(c => c.OwnerUserId)
            .OnDelete(DeleteBehavior.SetNull);

        builder.HasOne(c => c.ContactList)
            .WithMany(cl => cl.Campaigns)
            .HasForeignKey(c => c.ContactListId)
            .OnDelete(DeleteBehavior.SetNull);

        builder.HasIndex(c => c.CampaignRef).IsUnique();
        builder.HasIndex(c => c.Status);
        builder.HasIndex(c => c.OwnerUserId);
    }
}
