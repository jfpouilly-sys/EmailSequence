using LeadGenerator.Core.Entities;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace LeadGenerator.Data.Configurations;

public class ContactListConfiguration : IEntityTypeConfiguration<ContactList>
{
    public void Configure(EntityTypeBuilder<ContactList> builder)
    {
        builder.ToTable("contact_lists");
        builder.HasKey(cl => cl.ListId);
        builder.Property(cl => cl.ListId).HasColumnName("list_id");
        builder.Property(cl => cl.Name).HasColumnName("name").HasMaxLength(200).IsRequired();
        builder.Property(cl => cl.Description).HasColumnName("description");
        builder.Property(cl => cl.OwnerUserId).HasColumnName("owner_user_id");
        builder.Property(cl => cl.IsShared).HasColumnName("is_shared").IsRequired();
        builder.Property(cl => cl.CreatedAt).HasColumnName("created_at").IsRequired();
        builder.Property(cl => cl.UpdatedAt).HasColumnName("updated_at").IsRequired();

        builder.HasOne(cl => cl.OwnerUser)
            .WithMany(u => u.ContactLists)
            .HasForeignKey(cl => cl.OwnerUserId)
            .OnDelete(DeleteBehavior.SetNull);
    }
}
