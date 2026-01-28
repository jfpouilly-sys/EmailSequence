using LeadGenerator.Core.Entities;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace LeadGenerator.Data.Configurations;

public class DownloadLogConfiguration : IEntityTypeConfiguration<DownloadLog>
{
    public void Configure(EntityTypeBuilder<DownloadLog> builder)
    {
        builder.ToTable("download_logs");
        builder.HasKey(dl => dl.DownloadId);
        builder.Property(dl => dl.DownloadId).HasColumnName("download_id");
        builder.Property(dl => dl.AttachmentId).HasColumnName("attachment_id");
        builder.Property(dl => dl.ContactId).HasColumnName("contact_id");
        builder.Property(dl => dl.CampaignId).HasColumnName("campaign_id");
        builder.Property(dl => dl.DownloadedAt).HasColumnName("downloaded_at").IsRequired();
        builder.Property(dl => dl.IpAddress).HasColumnName("ip_address").HasMaxLength(50);
        builder.Property(dl => dl.UserAgent).HasColumnName("user_agent").HasMaxLength(500);

        builder.HasOne(dl => dl.Attachment)
            .WithMany(a => a.DownloadLogs)
            .HasForeignKey(dl => dl.AttachmentId)
            .OnDelete(DeleteBehavior.Cascade);

        builder.HasOne(dl => dl.Contact)
            .WithMany()
            .HasForeignKey(dl => dl.ContactId)
            .OnDelete(DeleteBehavior.SetNull);

        builder.HasOne(dl => dl.Campaign)
            .WithMany()
            .HasForeignKey(dl => dl.CampaignId)
            .OnDelete(DeleteBehavior.SetNull);

        builder.HasIndex(dl => dl.AttachmentId);
    }
}
