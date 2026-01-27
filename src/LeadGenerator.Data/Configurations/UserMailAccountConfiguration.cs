using LeadGenerator.Core.Entities;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace LeadGenerator.Data.Configurations;

public class UserMailAccountConfiguration : IEntityTypeConfiguration<UserMailAccount>
{
    public void Configure(EntityTypeBuilder<UserMailAccount> builder)
    {
        builder.ToTable("user_mail_accounts");
        builder.HasKey(uma => new { uma.UserId, uma.AccountId });
        builder.Property(uma => uma.UserId).HasColumnName("user_id");
        builder.Property(uma => uma.AccountId).HasColumnName("account_id");

        builder.HasOne(uma => uma.User)
            .WithMany(u => u.UserMailAccounts)
            .HasForeignKey(uma => uma.UserId)
            .OnDelete(DeleteBehavior.Cascade);

        builder.HasOne(uma => uma.MailAccount)
            .WithMany(m => m.UserMailAccounts)
            .HasForeignKey(uma => uma.AccountId)
            .OnDelete(DeleteBehavior.Cascade);
    }
}
