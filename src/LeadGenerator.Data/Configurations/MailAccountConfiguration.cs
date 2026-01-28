using LeadGenerator.Core.Entities;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace LeadGenerator.Data.Configurations;

public class MailAccountConfiguration : IEntityTypeConfiguration<MailAccount>
{
    public void Configure(EntityTypeBuilder<MailAccount> builder)
    {
        builder.ToTable("mail_accounts");
        builder.HasKey(m => m.AccountId);
        builder.Property(m => m.AccountId).HasColumnName("account_id");
        builder.Property(m => m.AccountName).HasColumnName("account_name").HasMaxLength(100).IsRequired();
        builder.Property(m => m.EmailAddress).HasColumnName("email_address").HasMaxLength(255).IsRequired();
        builder.Property(m => m.WorkstationId).HasColumnName("workstation_id").HasMaxLength(100);
        builder.Property(m => m.DailyLimit).HasColumnName("daily_limit").IsRequired();
        builder.Property(m => m.HourlyLimit).HasColumnName("hourly_limit").IsRequired();
        builder.Property(m => m.CurrentDailyCount).HasColumnName("current_daily_count").IsRequired();
        builder.Property(m => m.LastCountReset).HasColumnName("last_count_reset");
        builder.Property(m => m.IsActive).HasColumnName("is_active").IsRequired();
        builder.Property(m => m.WarmupMode).HasColumnName("warmup_mode").IsRequired();
        builder.Property(m => m.WarmupStartDate).HasColumnName("warmup_start_date");
        builder.Property(m => m.CreatedAt).HasColumnName("created_at").IsRequired();

        builder.HasIndex(m => m.EmailAddress).IsUnique();
    }
}
