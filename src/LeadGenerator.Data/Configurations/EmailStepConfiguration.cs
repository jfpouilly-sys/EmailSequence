using LeadGenerator.Core.Entities;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace LeadGenerator.Data.Configurations;

public class EmailStepConfiguration : IEntityTypeConfiguration<EmailStep>
{
    public void Configure(EntityTypeBuilder<EmailStep> builder)
    {
        builder.ToTable("email_steps");
        builder.HasKey(es => es.StepId);
        builder.Property(es => es.StepId).HasColumnName("step_id");
        builder.Property(es => es.CampaignId).HasColumnName("campaign_id");
        builder.Property(es => es.StepNumber).HasColumnName("step_number").IsRequired();
        builder.Property(es => es.SubjectTemplate).HasColumnName("subject_template").IsRequired();
        builder.Property(es => es.BodyTemplate).HasColumnName("body_template").IsRequired();
        builder.Property(es => es.DelayDays).HasColumnName("delay_days").IsRequired();
        builder.Property(es => es.IsActive).HasColumnName("is_active").IsRequired();
        builder.Property(es => es.CreatedAt).HasColumnName("created_at").IsRequired();
        builder.Property(es => es.UpdatedAt).HasColumnName("updated_at").IsRequired();

        builder.HasOne(es => es.Campaign)
            .WithMany(c => c.EmailSteps)
            .HasForeignKey(es => es.CampaignId)
            .OnDelete(DeleteBehavior.Cascade);

        builder.HasIndex(es => new { es.CampaignId, es.StepNumber }).IsUnique();
    }
}
