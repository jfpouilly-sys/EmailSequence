using LeadGenerator.Core.Entities;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace LeadGenerator.Data.Configurations;

public class CampaignMailAccountConfiguration : IEntityTypeConfiguration<CampaignMailAccount>
{
    public void Configure(EntityTypeBuilder<CampaignMailAccount> builder)
    {
        builder.ToTable("campaign_mail_accounts");
        builder.HasKey(cma => new { cma.CampaignId, cma.AccountId });
        builder.Property(cma => cma.CampaignId).HasColumnName("campaign_id");
        builder.Property(cma => cma.AccountId).HasColumnName("account_id");
        builder.Property(cma => cma.DistributionWeight).HasColumnName("distribution_weight").HasPrecision(3, 2);

        builder.HasOne(cma => cma.Campaign)
            .WithMany(c => c.CampaignMailAccounts)
            .HasForeignKey(cma => cma.CampaignId)
            .OnDelete(DeleteBehavior.Cascade);

        builder.HasOne(cma => cma.MailAccount)
            .WithMany(m => m.CampaignMailAccounts)
            .HasForeignKey(cma => cma.AccountId)
            .OnDelete(DeleteBehavior.Cascade);
    }
}
