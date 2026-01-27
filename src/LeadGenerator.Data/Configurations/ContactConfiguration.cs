using LeadGenerator.Core.Entities;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace LeadGenerator.Data.Configurations;

public class ContactConfiguration : IEntityTypeConfiguration<Contact>
{
    public void Configure(EntityTypeBuilder<Contact> builder)
    {
        builder.ToTable("contacts");
        builder.HasKey(c => c.ContactId);
        builder.Property(c => c.ContactId).HasColumnName("contact_id");
        builder.Property(c => c.ListId).HasColumnName("list_id");
        builder.Property(c => c.Title).HasColumnName("title").HasMaxLength(20);
        builder.Property(c => c.FirstName).HasColumnName("first_name").HasMaxLength(100).IsRequired();
        builder.Property(c => c.LastName).HasColumnName("last_name").HasMaxLength(100).IsRequired();
        builder.Property(c => c.Email).HasColumnName("email").HasMaxLength(255).IsRequired();
        builder.Property(c => c.Company).HasColumnName("company").HasMaxLength(200).IsRequired();
        builder.Property(c => c.Position).HasColumnName("position").HasMaxLength(100);
        builder.Property(c => c.Phone).HasColumnName("phone").HasMaxLength(50);
        builder.Property(c => c.LinkedInUrl).HasColumnName("linkedin_url").HasMaxLength(500);
        builder.Property(c => c.Source).HasColumnName("source").HasMaxLength(100);

        // Custom fields
        builder.Property(c => c.Custom1).HasColumnName("custom1").HasMaxLength(500);
        builder.Property(c => c.Custom2).HasColumnName("custom2").HasMaxLength(500);
        builder.Property(c => c.Custom3).HasColumnName("custom3").HasMaxLength(500);
        builder.Property(c => c.Custom4).HasColumnName("custom4").HasMaxLength(500);
        builder.Property(c => c.Custom5).HasColumnName("custom5").HasMaxLength(500);
        builder.Property(c => c.Custom6).HasColumnName("custom6").HasMaxLength(500);
        builder.Property(c => c.Custom7).HasColumnName("custom7").HasMaxLength(500);
        builder.Property(c => c.Custom8).HasColumnName("custom8").HasMaxLength(500);
        builder.Property(c => c.Custom9).HasColumnName("custom9").HasMaxLength(500);
        builder.Property(c => c.Custom10).HasColumnName("custom10").HasMaxLength(500);

        builder.Property(c => c.Custom1Label).HasColumnName("custom1_label").HasMaxLength(50);
        builder.Property(c => c.Custom2Label).HasColumnName("custom2_label").HasMaxLength(50);
        builder.Property(c => c.Custom3Label).HasColumnName("custom3_label").HasMaxLength(50);
        builder.Property(c => c.Custom4Label).HasColumnName("custom4_label").HasMaxLength(50);
        builder.Property(c => c.Custom5Label).HasColumnName("custom5_label").HasMaxLength(50);
        builder.Property(c => c.Custom6Label).HasColumnName("custom6_label").HasMaxLength(50);
        builder.Property(c => c.Custom7Label).HasColumnName("custom7_label").HasMaxLength(50);
        builder.Property(c => c.Custom8Label).HasColumnName("custom8_label").HasMaxLength(50);
        builder.Property(c => c.Custom9Label).HasColumnName("custom9_label").HasMaxLength(50);
        builder.Property(c => c.Custom10Label).HasColumnName("custom10_label").HasMaxLength(50);

        builder.Property(c => c.CrmLeadId).HasColumnName("crm_lead_id").HasMaxLength(100);
        builder.Property(c => c.CreatedAt).HasColumnName("created_at").IsRequired();
        builder.Property(c => c.UpdatedAt).HasColumnName("updated_at").IsRequired();

        builder.HasOne(c => c.ContactList)
            .WithMany(cl => cl.Contacts)
            .HasForeignKey(c => c.ListId)
            .OnDelete(DeleteBehavior.Cascade);

        builder.HasIndex(c => c.Email);
        builder.HasIndex(c => new { c.ListId, c.Email }).IsUnique();
    }
}
