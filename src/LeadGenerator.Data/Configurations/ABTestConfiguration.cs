using LeadGenerator.Core.Entities;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace LeadGenerator.Data.Configurations;

public class ABTestConfiguration : IEntityTypeConfiguration<ABTest>
{
    public void Configure(EntityTypeBuilder<ABTest> builder)
    {
        builder.ToTable("ab_tests");
        builder.HasKey(ab => ab.TestId);
        builder.Property(ab => ab.TestId).HasColumnName("test_id");
        builder.Property(ab => ab.CampaignId).HasColumnName("campaign_id");
        builder.Property(ab => ab.StepId).HasColumnName("step_id");
        builder.Property(ab => ab.TestElement).HasColumnName("test_element").IsRequired();
        builder.Property(ab => ab.VariantAContent).HasColumnName("variant_a_content").IsRequired();
        builder.Property(ab => ab.VariantBContent).HasColumnName("variant_b_content").IsRequired();
        builder.Property(ab => ab.SplitRatio).HasColumnName("split_ratio").HasPrecision(3, 2).IsRequired();
        builder.Property(ab => ab.SuccessMetric).HasColumnName("success_metric").HasMaxLength(50).IsRequired();
        builder.Property(ab => ab.MinSampleSize).HasColumnName("min_sample_size").IsRequired();
        builder.Property(ab => ab.MaxDurationDays).HasColumnName("max_duration_days").IsRequired();
        builder.Property(ab => ab.Status).HasColumnName("status").IsRequired();
        builder.Property(ab => ab.WinnerVariant).HasColumnName("winner_variant").HasMaxLength(1);
        builder.Property(ab => ab.ConfidenceLevel).HasColumnName("confidence_level").HasPrecision(5, 2);
        builder.Property(ab => ab.StartedAt).HasColumnName("started_at").IsRequired();
        builder.Property(ab => ab.CompletedAt).HasColumnName("completed_at");

        builder.HasOne(ab => ab.Campaign)
            .WithMany(c => c.ABTests)
            .HasForeignKey(ab => ab.CampaignId)
            .OnDelete(DeleteBehavior.Cascade);

        builder.HasOne(ab => ab.EmailStep)
            .WithMany(es => es.ABTests)
            .HasForeignKey(ab => ab.StepId)
            .OnDelete(DeleteBehavior.Cascade);
    }
}
