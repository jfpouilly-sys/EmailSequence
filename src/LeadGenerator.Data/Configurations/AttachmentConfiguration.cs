using LeadGenerator.Core.Entities;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace LeadGenerator.Data.Configurations;

public class AttachmentConfiguration : IEntityTypeConfiguration<Attachment>
{
    public void Configure(EntityTypeBuilder<Attachment> builder)
    {
        builder.ToTable("attachments");
        builder.HasKey(a => a.AttachmentId);
        builder.Property(a => a.AttachmentId).HasColumnName("attachment_id");
        builder.Property(a => a.StepId).HasColumnName("step_id");
        builder.Property(a => a.FileName).HasColumnName("file_name").HasMaxLength(255).IsRequired();
        builder.Property(a => a.FilePath).HasColumnName("file_path").HasMaxLength(1000).IsRequired();
        builder.Property(a => a.FileSize).HasColumnName("file_size").IsRequired();
        builder.Property(a => a.MimeType).HasColumnName("mime_type").HasMaxLength(100);
        builder.Property(a => a.DeliveryMode).HasColumnName("delivery_mode").IsRequired();
        builder.Property(a => a.LinkText).HasColumnName("link_text").HasMaxLength(200);
        builder.Property(a => a.ExpirationDays).HasColumnName("expiration_days");
        builder.Property(a => a.DownloadToken).HasColumnName("download_token").HasMaxLength(100);
        builder.Property(a => a.CreatedAt).HasColumnName("created_at").IsRequired();

        builder.HasOne(a => a.EmailStep)
            .WithMany(es => es.Attachments)
            .HasForeignKey(a => a.StepId)
            .OnDelete(DeleteBehavior.Cascade);

        builder.HasIndex(a => a.DownloadToken).IsUnique();
    }
}
