using LeadGenerator.Core.Entities;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace LeadGenerator.Data.Configurations;

public class AuditLogConfiguration : IEntityTypeConfiguration<AuditLog>
{
    public void Configure(EntityTypeBuilder<AuditLog> builder)
    {
        builder.ToTable("audit_logs");
        builder.HasKey(al => al.LogId);
        builder.Property(al => al.LogId).HasColumnName("log_id");
        builder.Property(al => al.UserId).HasColumnName("user_id");
        builder.Property(al => al.Action).HasColumnName("action").HasMaxLength(100).IsRequired();
        builder.Property(al => al.EntityType).HasColumnName("entity_type").HasMaxLength(50);
        builder.Property(al => al.EntityId).HasColumnName("entity_id");
        builder.Property(al => al.Details).HasColumnName("details").HasColumnType("jsonb");
        builder.Property(al => al.IpAddress).HasColumnName("ip_address").HasMaxLength(50);
        builder.Property(al => al.CreatedAt).HasColumnName("created_at").IsRequired();

        builder.HasOne(al => al.User)
            .WithMany()
            .HasForeignKey(al => al.UserId)
            .OnDelete(DeleteBehavior.SetNull);

        builder.HasIndex(al => al.UserId);
        builder.HasIndex(al => al.CreatedAt);
    }
}
