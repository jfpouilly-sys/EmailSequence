using LeadGenerator.Core.Entities;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace LeadGenerator.Data.Configurations;

public class SuppressionEntryConfiguration : IEntityTypeConfiguration<SuppressionEntry>
{
    public void Configure(EntityTypeBuilder<SuppressionEntry> builder)
    {
        builder.ToTable("suppression_list");
        builder.HasKey(se => se.Email);
        builder.Property(se => se.Email).HasColumnName("email").HasMaxLength(255);
        builder.Property(se => se.Scope).HasColumnName("scope").IsRequired();
        builder.Property(se => se.Source).HasColumnName("source").IsRequired();
        builder.Property(se => se.CampaignId).HasColumnName("campaign_id");
        builder.Property(se => se.Reason).HasColumnName("reason");
        builder.Property(se => se.CreatedAt).HasColumnName("created_at").IsRequired();

        builder.HasOne(se => se.Campaign)
            .WithMany(c => c.SuppressionEntries)
            .HasForeignKey(se => se.CampaignId)
            .OnDelete(DeleteBehavior.SetNull);

        builder.HasIndex(se => se.Email);
    }
}
