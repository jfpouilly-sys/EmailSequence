# Lead Generator — Claude Code Implementation Guide

**Version:** 1.0  
**Target:** Claude Code AI Assistant  
**Document Purpose:** Step-by-step instructions to implement the Lead Generator application

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Technology Stack](#2-technology-stack)
3. [Project Structure](#3-project-structure)
4. [Phase 1: Database Setup](#4-phase-1-database-setup)
5. [Phase 2: API Server](#5-phase-2-api-server)
6. [Phase 3: WPF Client](#6-phase-3-wpf-client)
7. [Phase 4: Mail Service](#7-phase-4-mail-service)
8. [Phase 5: CRM Integration API](#8-phase-5-crm-integration-api)
9. [Installation Manual](#9-installation-manual)
10. [Configuration Guide](#10-configuration-guide)

---

## 1. Project Overview

### 1.1 What We're Building

A multi-user desktop application for managing digital marketing email campaigns:
- **API Server**: .NET 8 REST API with PostgreSQL database
- **WPF Client**: Windows desktop application for campaign management
- **Mail Service**: Windows Service for Outlook integration (send, reply detection, unsubscribe)
- **CRM Sync API**: Endpoints for home-made CRM to pull data

### 1.2 Key Constraints

- All components run on **internal network only** (no public endpoints)
- **Standalone authentication** (no AD/LDAP)
- **Email-based unsubscribe** (no web forms)
- **Hybrid attachments**: Direct attach (no tracking) or Link (internal tracking)
- **10 custom fields** from CSV import for personalization

---

## 2. Technology Stack

```
┌─────────────────────────────────────────────────────────┐
│ Component          │ Technology                         │
├────────────────────┼────────────────────────────────────┤
│ API Server         │ .NET 8 Web API                     │
│ Database           │ PostgreSQL 15+                     │
│ ORM                │ Entity Framework Core 8            │
│ Desktop Client     │ WPF (.NET 8)                       │
│ Mail Integration   │ Outlook COM Interop (Microsoft.Office.Interop.Outlook) │
│ Background Service │ Windows Service (.NET 8 Worker)    │
│ Authentication     │ JWT Bearer Tokens                  │
│ Password Hashing   │ BCrypt.Net-Next                    │
│ CSV Parsing        │ CsvHelper                          │
│ Reporting/Charts   │ LiveCharts2                        │
│ PDF Export         │ QuestPDF                           │
│ Logging            │ Serilog                            │
└─────────────────────────────────────────────────────────┘
```

---

## 3. Project Structure

```
LeadGenerator/
├── src/
│   ├── LeadGenerator.Api/              # .NET 8 Web API
│   │   ├── Controllers/
│   │   │   ├── AuthController.cs
│   │   │   ├── UsersController.cs
│   │   │   ├── CampaignsController.cs
│   │   │   ├── ContactListsController.cs
│   │   │   ├── ContactsController.cs
│   │   │   ├── TemplatesController.cs
│   │   │   ├── MailAccountsController.cs
│   │   │   ├── ReportsController.cs
│   │   │   ├── SuppressionController.cs
│   │   │   ├── DownloadController.cs       # File download with tracking
│   │   │   └── SyncController.cs           # CRM sync endpoints
│   │   ├── Services/
│   │   │   ├── AuthService.cs
│   │   │   ├── CampaignService.cs
│   │   │   ├── ContactService.cs
│   │   │   ├── EmailQueueService.cs
│   │   │   ├── TemplateService.cs
│   │   │   ├── ReportService.cs
│   │   │   ├── ABTestService.cs
│   │   │   └── SuppressionService.cs
│   │   ├── Models/
│   │   │   ├── DTOs/
│   │   │   └── Requests/
│   │   ├── Middleware/
│   │   │   └── JwtMiddleware.cs
│   │   ├── Program.cs
│   │   └── appsettings.json
│   │
│   ├── LeadGenerator.Core/             # Shared domain models
│   │   ├── Entities/
│   │   │   ├── User.cs
│   │   │   ├── Campaign.cs
│   │   │   ├── ContactList.cs
│   │   │   ├── Contact.cs
│   │   │   ├── EmailSequence.cs
│   │   │   ├── EmailStep.cs
│   │   │   ├── Attachment.cs
│   │   │   ├── CampaignContact.cs
│   │   │   ├── EmailLog.cs
│   │   │   ├── DownloadLog.cs
│   │   │   ├── MailAccount.cs
│   │   │   ├── SuppressionEntry.cs
│   │   │   ├── ABTest.cs
│   │   │   └── AuditLog.cs
│   │   ├── Enums/
│   │   │   ├── UserRole.cs
│   │   │   ├── CampaignStatus.cs
│   │   │   ├── ContactStatus.cs
│   │   │   ├── DeliveryMode.cs
│   │   │   └── UnsubscribeScope.cs
│   │   └── Interfaces/
│   │
│   ├── LeadGenerator.Data/             # EF Core DbContext
│   │   ├── LeadGenDbContext.cs
│   │   ├── Configurations/             # Entity configurations
│   │   ├── Migrations/
│   │   └── Repositories/
│   │
│   ├── LeadGenerator.Desktop/          # WPF Application
│   │   ├── Views/
│   │   │   ├── LoginWindow.xaml
│   │   │   ├── MainWindow.xaml
│   │   │   ├── DashboardView.xaml
│   │   │   ├── CampaignListView.xaml
│   │   │   ├── CampaignDetailView.xaml
│   │   │   ├── ContactListView.xaml
│   │   │   ├── CsvImportWizard.xaml
│   │   │   ├── TemplateEditorView.xaml
│   │   │   ├── AttachmentManagerView.xaml
│   │   │   ├── ABTestView.xaml
│   │   │   ├── ReportsView.xaml
│   │   │   ├── UserManagementView.xaml
│   │   │   ├── MailAccountsView.xaml
│   │   │   └── SettingsView.xaml
│   │   ├── ViewModels/
│   │   ├── Services/
│   │   │   └── ApiClient.cs
│   │   ├── Converters/
│   │   ├── Resources/
│   │   └── App.xaml
│   │
│   └── LeadGenerator.MailService/      # Windows Service
│       ├── Worker.cs
│       ├── Services/
│       │   ├── OutlookService.cs
│       │   ├── EmailSenderService.cs
│       │   ├── ReplyDetectionService.cs
│       │   └── UnsubscribeDetectionService.cs
│       ├── Program.cs
│       └── appsettings.json
│
├── scripts/
│   ├── database/
│   │   ├── 001_create_database.sql
│   │   ├── 002_create_tables.sql
│   │   ├── 003_seed_admin_user.sql
│   │   └── 004_create_indexes.sql
│   └── install/
│       ├── install-api.ps1
│       ├── install-mailservice.ps1
│       └── install-client.ps1
│
├── docs/
│   ├── FunctionalSpec.md
│   ├── InstallationManual.md
│   └── UserGuide.md
│
├── LeadGenerator.sln
└── README.md
```

---

## 4. Phase 1: Database Setup

### 4.1 Claude Code Prompt — Create Database Schema

```
Create PostgreSQL database schema for the Lead Generator application.

Requirements:
- Users table with standalone authentication (BCrypt password hash)
- Campaigns, ContactLists, Contacts with 10 custom fields
- EmailSequence with EmailSteps
- Attachments with DeliveryMode (Attachment/Link)
- CampaignContact junction table with status tracking
- EmailLog for sent emails
- DownloadLog for file download tracking
- MailAccounts with daily limits and warmup mode
- SuppressionList for global/campaign opt-outs
- ABTests for A/B testing
- AuditLog for security events

Generate:
1. CREATE TABLE statements with proper constraints
2. Foreign key relationships
3. Indexes for common queries
4. ENUM types for status fields
5. Seed script for default admin user (username: admin, password: Admin123!)
```

### 4.2 Database Schema SQL

```sql
-- File: scripts/database/001_create_database.sql

CREATE DATABASE leadgenerator
    WITH ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8';

-- File: scripts/database/002_create_tables.sql

-- ENUM Types
CREATE TYPE user_role AS ENUM ('Admin', 'Manager', 'User');
CREATE TYPE campaign_status AS ENUM ('Draft', 'Active', 'Paused', 'Completed', 'Archived');
CREATE TYPE contact_status AS ENUM ('Pending', 'InProgress', 'Responded', 'Completed', 'Bounced', 'Unsubscribed', 'OptedOut', 'Paused');
CREATE TYPE delivery_mode AS ENUM ('Attachment', 'Link');
CREATE TYPE unsubscribe_scope AS ENUM ('Global', 'Campaign');
CREATE TYPE unsubscribe_source AS ENUM ('EmailReply', 'Manual', 'Bounce', 'Complaint');
CREATE TYPE ab_test_element AS ENUM ('Subject', 'Body', 'SendTime');
CREATE TYPE ab_test_status AS ENUM ('Running', 'Completed', 'Cancelled');

-- Users
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role user_role NOT NULL DEFAULT 'User',
    is_active BOOLEAN NOT NULL DEFAULT true,
    failed_login_attempts INT NOT NULL DEFAULT 0,
    locked_until TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Mail Accounts
CREATE TABLE mail_accounts (
    account_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_name VARCHAR(100) NOT NULL,
    email_address VARCHAR(255) NOT NULL UNIQUE,
    workstation_id VARCHAR(100),
    daily_limit INT NOT NULL DEFAULT 50,
    hourly_limit INT NOT NULL DEFAULT 10,
    current_daily_count INT NOT NULL DEFAULT 0,
    last_count_reset DATE,
    is_active BOOLEAN NOT NULL DEFAULT true,
    warmup_mode BOOLEAN NOT NULL DEFAULT false,
    warmup_start_date DATE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- User Mail Account Assignments
CREATE TABLE user_mail_accounts (
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    account_id UUID REFERENCES mail_accounts(account_id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, account_id)
);

-- Contact Lists
CREATE TABLE contact_lists (
    list_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    owner_user_id UUID REFERENCES users(user_id),
    is_shared BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Contacts
CREATE TABLE contacts (
    contact_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    list_id UUID NOT NULL REFERENCES contact_lists(list_id) ON DELETE CASCADE,
    title VARCHAR(20),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    company VARCHAR(200) NOT NULL,
    position VARCHAR(100),
    phone VARCHAR(50),
    linkedin_url VARCHAR(500),
    source VARCHAR(100),
    custom1 VARCHAR(500),
    custom2 VARCHAR(500),
    custom3 VARCHAR(500),
    custom4 VARCHAR(500),
    custom5 VARCHAR(500),
    custom6 VARCHAR(500),
    custom7 VARCHAR(500),
    custom8 VARCHAR(500),
    custom9 VARCHAR(500),
    custom10 VARCHAR(500),
    custom1_label VARCHAR(50),
    custom2_label VARCHAR(50),
    custom3_label VARCHAR(50),
    custom4_label VARCHAR(50),
    custom5_label VARCHAR(50),
    custom6_label VARCHAR(50),
    custom7_label VARCHAR(50),
    custom8_label VARCHAR(50),
    custom9_label VARCHAR(50),
    custom10_label VARCHAR(50),
    crm_lead_id VARCHAR(100),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(list_id, email)
);

-- Campaigns
CREATE TABLE campaigns (
    campaign_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    campaign_ref VARCHAR(20) NOT NULL UNIQUE, -- ISIT-25xxxx
    owner_user_id UUID REFERENCES users(user_id),
    contact_list_id UUID REFERENCES contact_lists(list_id),
    status campaign_status NOT NULL DEFAULT 'Draft',
    -- Sending Configuration
    inter_email_delay_minutes INT NOT NULL DEFAULT 30,
    sequence_step_delay_days INT NOT NULL DEFAULT 3,
    sending_window_start TIME NOT NULL DEFAULT '09:00',
    sending_window_end TIME NOT NULL DEFAULT '17:00',
    sending_days VARCHAR(20) NOT NULL DEFAULT 'Mon,Tue,Wed,Thu,Fri',
    randomization_minutes INT NOT NULL DEFAULT 15,
    daily_send_limit INT NOT NULL DEFAULT 50,
    -- Dates
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Campaign Mail Accounts
CREATE TABLE campaign_mail_accounts (
    campaign_id UUID REFERENCES campaigns(campaign_id) ON DELETE CASCADE,
    account_id UUID REFERENCES mail_accounts(account_id) ON DELETE CASCADE,
    distribution_weight DECIMAL(3,2) DEFAULT 1.0,
    PRIMARY KEY (campaign_id, account_id)
);

-- Email Steps (Sequence)
CREATE TABLE email_steps (
    step_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID NOT NULL REFERENCES campaigns(campaign_id) ON DELETE CASCADE,
    step_number INT NOT NULL,
    subject_template TEXT NOT NULL,
    body_template TEXT NOT NULL,
    delay_days INT NOT NULL DEFAULT 0, -- Days after previous step
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(campaign_id, step_number)
);

-- Attachments
CREATE TABLE attachments (
    attachment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    step_id UUID NOT NULL REFERENCES email_steps(step_id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(1000) NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(100),
    delivery_mode delivery_mode NOT NULL DEFAULT 'Attachment',
    link_text VARCHAR(200),
    expiration_days INT,
    download_token VARCHAR(100) UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Campaign Contacts (Junction + Status)
CREATE TABLE campaign_contacts (
    campaign_id UUID REFERENCES campaigns(campaign_id) ON DELETE CASCADE,
    contact_id UUID REFERENCES contacts(contact_id) ON DELETE CASCADE,
    status contact_status NOT NULL DEFAULT 'Pending',
    assigned_mail_account_id UUID REFERENCES mail_accounts(account_id),
    current_step INT NOT NULL DEFAULT 0,
    last_email_sent_at TIMESTAMP,
    next_email_scheduled_at TIMESTAMP,
    responded_at TIMESTAMP,
    ab_test_variant CHAR(1), -- 'A' or 'B'
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (campaign_id, contact_id)
);

-- Email Log
CREATE TABLE email_logs (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES campaigns(campaign_id),
    contact_id UUID REFERENCES contacts(contact_id),
    step_id UUID REFERENCES email_steps(step_id),
    mail_account_id UUID REFERENCES mail_accounts(account_id),
    subject VARCHAR(500),
    sent_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) NOT NULL, -- 'Sent', 'Failed', 'Bounced'
    error_message TEXT,
    outlook_entry_id VARCHAR(500)
);

-- Download Log (for Link mode tracking)
CREATE TABLE download_logs (
    download_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    attachment_id UUID NOT NULL REFERENCES attachments(attachment_id),
    contact_id UUID REFERENCES contacts(contact_id),
    campaign_id UUID REFERENCES campaigns(campaign_id),
    downloaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(50),
    user_agent VARCHAR(500)
);

-- Suppression List
CREATE TABLE suppression_list (
    email VARCHAR(255) PRIMARY KEY,
    scope unsubscribe_scope NOT NULL DEFAULT 'Global',
    source unsubscribe_source NOT NULL,
    campaign_id UUID REFERENCES campaigns(campaign_id),
    reason TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- A/B Tests
CREATE TABLE ab_tests (
    test_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID NOT NULL REFERENCES campaigns(campaign_id) ON DELETE CASCADE,
    step_id UUID NOT NULL REFERENCES email_steps(step_id) ON DELETE CASCADE,
    test_element ab_test_element NOT NULL,
    variant_a_content TEXT NOT NULL,
    variant_b_content TEXT NOT NULL,
    split_ratio DECIMAL(3,2) NOT NULL DEFAULT 0.50,
    success_metric VARCHAR(50) NOT NULL DEFAULT 'ResponseRate',
    min_sample_size INT NOT NULL DEFAULT 100,
    max_duration_days INT NOT NULL DEFAULT 14,
    status ab_test_status NOT NULL DEFAULT 'Running',
    winner_variant CHAR(1), -- 'A', 'B', or NULL
    confidence_level DECIMAL(5,2),
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Audit Log
CREATE TABLE audit_logs (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id UUID,
    details JSONB,
    ip_address VARCHAR(50),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- File: scripts/database/003_seed_admin_user.sql
-- Password: Admin123! (BCrypt hash)
INSERT INTO users (username, email, password_hash, role, is_active)
VALUES ('admin', 'admin@company.com', 
        '$2a$11$rBNdGDmjXGPqXcH7JhHxPeZVzYw7aBhqF7YHQz.gE7gEz8QzEkMmK', 
        'Admin', true);

-- File: scripts/database/004_create_indexes.sql
CREATE INDEX idx_contacts_email ON contacts(email);
CREATE INDEX idx_contacts_list_id ON contacts(list_id);
CREATE INDEX idx_campaigns_status ON campaigns(status);
CREATE INDEX idx_campaigns_owner ON campaigns(owner_user_id);
CREATE INDEX idx_campaign_contacts_status ON campaign_contacts(status);
CREATE INDEX idx_campaign_contacts_next_scheduled ON campaign_contacts(next_email_scheduled_at);
CREATE INDEX idx_email_logs_campaign ON email_logs(campaign_id);
CREATE INDEX idx_email_logs_contact ON email_logs(contact_id);
CREATE INDEX idx_email_logs_sent_at ON email_logs(sent_at);
CREATE INDEX idx_download_logs_attachment ON download_logs(attachment_id);
CREATE INDEX idx_suppression_email ON suppression_list(email);
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at);
```

---

## 5. Phase 2: API Server

### 5.1 Claude Code Prompt — Create API Project

```
Create a .NET 8 Web API project for the Lead Generator application.

Project: LeadGenerator.Api

Requirements:
1. JWT authentication with BCrypt password hashing
2. Role-based authorization (Admin, Manager, User)
3. Entity Framework Core with PostgreSQL
4. RESTful endpoints for all entities
5. File upload/download with tracking
6. CRM sync endpoints (GET only, internal network)
7. Proper error handling and logging with Serilog
8. Swagger documentation

Key Endpoints:
- POST /api/auth/login
- POST /api/auth/refresh
- CRUD for /api/users, /api/campaigns, /api/contacts, etc.
- GET /api/download/{token} - File download with tracking
- GET /api/sync/* - CRM integration endpoints

Include:
- appsettings.json with configurable connection string
- JWT configuration
- CORS for internal network
- Request validation with FluentValidation
```

### 5.2 Key API Files

**Program.cs:**
```csharp
using LeadGenerator.Api.Services;
using LeadGenerator.Data;
using Microsoft.EntityFrameworkCore;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.IdentityModel.Tokens;
using System.Text;
using Serilog;

var builder = WebApplication.CreateBuilder(args);

// Serilog
Log.Logger = new LoggerConfiguration()
    .ReadFrom.Configuration(builder.Configuration)
    .Enrich.FromLogContext()
    .WriteTo.Console()
    .WriteTo.File("logs/api-.log", rollingInterval: RollingInterval.Day)
    .CreateLogger();

builder.Host.UseSerilog();

// Database
builder.Services.AddDbContext<LeadGenDbContext>(options =>
    options.UseNpgsql(builder.Configuration.GetConnectionString("DefaultConnection")));

// JWT Authentication
var jwtKey = builder.Configuration["Jwt:Key"];
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            ValidIssuer = builder.Configuration["Jwt:Issuer"],
            ValidAudience = builder.Configuration["Jwt:Audience"],
            IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(jwtKey))
        };
    });

builder.Services.AddAuthorization(options =>
{
    options.AddPolicy("AdminOnly", policy => policy.RequireRole("Admin"));
    options.AddPolicy("ManagerOrAdmin", policy => policy.RequireRole("Admin", "Manager"));
});

// Services
builder.Services.AddScoped<IAuthService, AuthService>();
builder.Services.AddScoped<ICampaignService, CampaignService>();
builder.Services.AddScoped<IContactService, ContactService>();
builder.Services.AddScoped<ITemplateService, TemplateService>();
builder.Services.AddScoped<IReportService, ReportService>();

builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// CORS (internal network only)
builder.Services.AddCors(options =>
{
    options.AddPolicy("InternalNetwork", policy =>
    {
        policy.WithOrigins(builder.Configuration.GetSection("AllowedOrigins").Get<string[]>())
              .AllowAnyMethod()
              .AllowAnyHeader();
    });
});

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseCors("InternalNetwork");
app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();

app.Run();
```

**appsettings.json:**
```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Host=localhost;Database=leadgenerator;Username=leadgen_user;Password=YourPassword"
  },
  "Jwt": {
    "Key": "YourSuperSecretKeyAtLeast32Characters!",
    "Issuer": "LeadGenerator",
    "Audience": "LeadGeneratorClients",
    "ExpirationMinutes": 480
  },
  "AllowedOrigins": [
    "http://localhost:*",
    "http://192.168.*.*"
  ],
  "FileStorage": {
    "BasePath": "C:\\LeadGenerator\\Files",
    "MaxFileSizeMB": 10,
    "AllowedExtensions": [".pdf", ".docx", ".xlsx", ".pptx", ".png", ".jpg"]
  },
  "Unsubscribe": {
    "KeywordsEN": ["UNSUBSCRIBE", "STOP", "REMOVE", "OPT OUT", "OPT-OUT"],
    "KeywordsFR": ["DÉSINSCRIRE", "DÉSINSCRIPTION", "STOP", "ARRÊTER", "SUPPRIMER"]
  },
  "Serilog": {
    "MinimumLevel": {
      "Default": "Information",
      "Override": {
        "Microsoft": "Warning"
      }
    }
  }
}
```

---

## 6. Phase 3: WPF Client

### 6.1 Claude Code Prompt — Create WPF Application

```
Create a WPF application (.NET 8) for the Lead Generator desktop client.

Project: LeadGenerator.Desktop

Requirements:
1. MVVM architecture with CommunityToolkit.Mvvm
2. Modern UI with Material Design or similar
3. Login window with session management
4. Main window with navigation sidebar
5. Views for: Dashboard, Campaigns, Contacts, Templates, Reports, Settings
6. CSV Import Wizard with field mapping
7. Template Editor with merge tag insertion
8. HTTP client for API communication

Key Features:
- Secure token storage
- Auto-refresh token before expiration
- Offline detection with retry
- Progress indicators for long operations
- DataGrid with sorting, filtering, pagination
- Form validation

Include XAML for:
- LoginWindow
- MainWindow with navigation
- CampaignListView with status indicators
- CsvImportWizard (3-step process)
- TemplateEditorView with merge tag picker
```

### 6.2 Key Desktop Files

**App.xaml.cs:**
```csharp
public partial class App : Application
{
    public static IServiceProvider ServiceProvider { get; private set; }
    
    protected override void OnStartup(StartupEventArgs e)
    {
        var services = new ServiceCollection();
        
        // Configuration
        var configuration = new ConfigurationBuilder()
            .SetBasePath(AppDomain.CurrentDomain.BaseDirectory)
            .AddJsonFile("appsettings.json", optional: false)
            .Build();
        
        services.AddSingleton<IConfiguration>(configuration);
        
        // HTTP Client
        services.AddHttpClient<IApiClient, ApiClient>(client =>
        {
            client.BaseAddress = new Uri(configuration["ApiBaseUrl"]);
        });
        
        // ViewModels
        services.AddTransient<LoginViewModel>();
        services.AddTransient<MainViewModel>();
        services.AddTransient<DashboardViewModel>();
        services.AddTransient<CampaignListViewModel>();
        services.AddTransient<CampaignDetailViewModel>();
        services.AddTransient<ContactListViewModel>();
        services.AddTransient<CsvImportViewModel>();
        services.AddTransient<TemplateEditorViewModel>();
        services.AddTransient<ReportsViewModel>();
        
        // Views
        services.AddTransient<LoginWindow>();
        services.AddTransient<MainWindow>();
        
        ServiceProvider = services.BuildServiceProvider();
        
        var loginWindow = ServiceProvider.GetRequiredService<LoginWindow>();
        loginWindow.Show();
    }
}
```

**ApiClient.cs:**
```csharp
public class ApiClient : IApiClient
{
    private readonly HttpClient _httpClient;
    private string _accessToken;
    
    public ApiClient(HttpClient httpClient)
    {
        _httpClient = httpClient;
    }
    
    public void SetToken(string token)
    {
        _accessToken = token;
        _httpClient.DefaultRequestHeaders.Authorization = 
            new AuthenticationHeaderValue("Bearer", token);
    }
    
    public async Task<T> GetAsync<T>(string endpoint)
    {
        var response = await _httpClient.GetAsync(endpoint);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<T>();
    }
    
    public async Task<T> PostAsync<T>(string endpoint, object data)
    {
        var response = await _httpClient.PostAsJsonAsync(endpoint, data);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<T>();
    }
    
    // ... other methods
}
```

---

## 7. Phase 4: Mail Service

### 7.1 Claude Code Prompt — Create Windows Service

```
Create a .NET 8 Worker Service for Outlook integration.

Project: LeadGenerator.MailService

Requirements:
1. Windows Service that runs in background
2. Outlook COM Interop for sending emails
3. Periodic inbox scanning for:
   - Reply detection (stop sequence)
   - Unsubscribe detection (EN + FR keywords)
4. Queue processing from API
5. Anti-spam measures (delays, randomization, daily limits)
6. Warmup mode support
7. Configurable scan intervals

Features:
- Process email queue from database
- Apply merge tags to templates
- Handle attachments (direct or link mode)
- Detect replies and update contact status
- Detect unsubscribe keywords and add to suppression list
- Log all activities

Unsubscribe Keywords:
- EN: UNSUBSCRIBE, STOP, REMOVE, OPT OUT, OPT-OUT
- FR: DÉSINSCRIRE, DÉSINSCRIPTION, STOP, ARRÊTER, SUPPRIMER
```

### 7.2 Key Mail Service Files

**Worker.cs:**
```csharp
public class Worker : BackgroundService
{
    private readonly ILogger<Worker> _logger;
    private readonly IServiceProvider _serviceProvider;
    private readonly IConfiguration _configuration;
    
    public Worker(ILogger<Worker> logger, IServiceProvider serviceProvider, 
                  IConfiguration configuration)
    {
        _logger = logger;
        _serviceProvider = serviceProvider;
        _configuration = configuration;
    }
    
    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                using var scope = _serviceProvider.CreateScope();
                
                // Process email queue
                var emailSender = scope.ServiceProvider.GetRequiredService<IEmailSenderService>();
                await emailSender.ProcessQueueAsync(stoppingToken);
                
                // Check for replies
                var replyDetector = scope.ServiceProvider.GetRequiredService<IReplyDetectionService>();
                await replyDetector.ScanForRepliesAsync(stoppingToken);
                
                // Check for unsubscribes
                var unsubDetector = scope.ServiceProvider.GetRequiredService<IUnsubscribeDetectionService>();
                await unsubDetector.ScanForUnsubscribesAsync(stoppingToken);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error in mail service worker");
            }
            
            var interval = _configuration.GetValue<int>("ScanIntervalSeconds", 60);
            await Task.Delay(TimeSpan.FromSeconds(interval), stoppingToken);
        }
    }
}
```

**UnsubscribeDetectionService.cs:**
```csharp
public class UnsubscribeDetectionService : IUnsubscribeDetectionService
{
    private readonly LeadGenDbContext _dbContext;
    private readonly IOutlookService _outlookService;
    private readonly IConfiguration _configuration;
    private readonly ILogger<UnsubscribeDetectionService> _logger;
    
    private readonly List<string> _keywordsEN;
    private readonly List<string> _keywordsFR;
    
    public UnsubscribeDetectionService(...)
    {
        _keywordsEN = _configuration.GetSection("Unsubscribe:KeywordsEN").Get<List<string>>();
        _keywordsFR = _configuration.GetSection("Unsubscribe:KeywordsFR").Get<List<string>>();
    }
    
    public async Task ScanForUnsubscribesAsync(CancellationToken ct)
    {
        var folders = _configuration.GetSection("Unsubscribe:ScanFolders").Get<List<string>>();
        
        foreach (var folderName in folders)
        {
            var emails = await _outlookService.GetUnreadEmailsAsync(folderName);
            
            foreach (var email in emails)
            {
                if (ContainsUnsubscribeKeyword(email.Subject) || 
                    ContainsUnsubscribeKeyword(email.Body))
                {
                    await ProcessUnsubscribeAsync(email);
                }
            }
        }
    }
    
    private bool ContainsUnsubscribeKeyword(string text)
    {
        if (string.IsNullOrEmpty(text)) return false;
        
        var upperText = text.ToUpperInvariant();
        var allKeywords = _keywordsEN.Concat(_keywordsFR);
        
        return allKeywords.Any(keyword => upperText.Contains(keyword.ToUpperInvariant()));
    }
    
    private async Task ProcessUnsubscribeAsync(EmailMessage email)
    {
        // Find contact by sender email
        var contact = await _dbContext.Contacts
            .FirstOrDefaultAsync(c => c.Email.ToLower() == email.SenderEmail.ToLower());
        
        if (contact == null) return;
        
        // Extract campaign ID from subject if present (ISIT-25xxxx)
        var campaignRef = ExtractCampaignRef(email.Subject);
        
        // Add to suppression list
        var suppression = new SuppressionEntry
        {
            Email = contact.Email.ToLower(),
            Scope = campaignRef != null ? UnsubscribeScope.Campaign : UnsubscribeScope.Global,
            Source = UnsubscribeSource.EmailReply,
            CampaignId = campaignRef != null ? await GetCampaignIdByRef(campaignRef) : null,
            CreatedAt = DateTime.UtcNow
        };
        
        _dbContext.SuppressionList.Add(suppression);
        
        // Update campaign contact status
        var campaignContacts = await _dbContext.CampaignContacts
            .Where(cc => cc.ContactId == contact.ContactId)
            .ToListAsync();
        
        foreach (var cc in campaignContacts)
        {
            cc.Status = ContactStatus.Unsubscribed;
            cc.UpdatedAt = DateTime.UtcNow;
        }
        
        await _dbContext.SaveChangesAsync();
        
        _logger.LogInformation("Processed unsubscribe for {Email}", contact.Email);
    }
}
```

---

## 8. Phase 5: CRM Integration API

### 8.1 Claude Code Prompt — Create Sync Endpoints

```
Add CRM sync endpoints to the API for the home-made CRM to pull data.

Requirements:
- All endpoints are GET only (CRM pulls, doesn't push)
- Internal network access only
- Delta sync support (only changes since last sync)
- Acknowledgment endpoint to mark sync complete

Endpoints:
GET  /api/sync/contacts?since={datetime}
GET  /api/sync/contacts/{id}
GET  /api/sync/campaigns
GET  /api/sync/activities?since={datetime}
GET  /api/sync/status-changes?since={datetime}
POST /api/sync/crm-updates  (CRM sends back conversion info)
POST /api/sync/acknowledge

Response format should be simple JSON suitable for the CRM to parse.
```

### 8.2 SyncController.cs

```csharp
[ApiController]
[Route("api/sync")]
[Authorize(Policy = "CrmAccess")]
public class SyncController : ControllerBase
{
    private readonly LeadGenDbContext _dbContext;
    
    [HttpGet("contacts")]
    public async Task<IActionResult> GetContacts([FromQuery] DateTime? since)
    {
        var query = _dbContext.Contacts.AsQueryable();
        
        if (since.HasValue)
        {
            query = query.Where(c => c.UpdatedAt > since.Value);
        }
        
        var contacts = await query
            .Select(c => new ContactSyncDto
            {
                ContactId = c.ContactId,
                Email = c.Email,
                FirstName = c.FirstName,
                LastName = c.LastName,
                Company = c.Company,
                Position = c.Position,
                Phone = c.Phone,
                Custom1 = c.Custom1,
                Custom2 = c.Custom2,
                // ... etc
                UpdatedAt = c.UpdatedAt
            })
            .ToListAsync();
        
        return Ok(new { contacts, timestamp = DateTime.UtcNow });
    }
    
    [HttpGet("status-changes")]
    public async Task<IActionResult> GetStatusChanges([FromQuery] DateTime? since)
    {
        var query = _dbContext.CampaignContacts
            .Include(cc => cc.Contact)
            .Include(cc => cc.Campaign)
            .AsQueryable();
        
        if (since.HasValue)
        {
            query = query.Where(cc => cc.UpdatedAt > since.Value);
        }
        
        var changes = await query
            .Select(cc => new StatusChangeSyncDto
            {
                ContactId = cc.ContactId,
                ContactEmail = cc.Contact.Email,
                CampaignId = cc.CampaignId,
                CampaignRef = cc.Campaign.CampaignRef,
                Status = cc.Status.ToString(),
                RespondedAt = cc.RespondedAt,
                UpdatedAt = cc.UpdatedAt
            })
            .ToListAsync();
        
        return Ok(new { changes, timestamp = DateTime.UtcNow });
    }
    
    [HttpPost("crm-updates")]
    public async Task<IActionResult> ReceiveCrmUpdates([FromBody] CrmUpdateRequest request)
    {
        foreach (var update in request.Updates)
        {
            var contact = await _dbContext.Contacts
                .FirstOrDefaultAsync(c => c.ContactId == update.ContactId);
            
            if (contact != null)
            {
                contact.CrmLeadId = update.CrmLeadId;
                contact.UpdatedAt = DateTime.UtcNow;
            }
        }
        
        await _dbContext.SaveChangesAsync();
        return Ok(new { processed = request.Updates.Count });
    }
    
    [HttpPost("acknowledge")]
    public async Task<IActionResult> Acknowledge([FromBody] AcknowledgeRequest request)
    {
        // Log sync completion for audit
        _dbContext.AuditLogs.Add(new AuditLog
        {
            Action = "CrmSyncCompleted",
            Details = JsonSerializer.Serialize(new { request.LastSyncTimestamp }),
            CreatedAt = DateTime.UtcNow
        });
        
        await _dbContext.SaveChangesAsync();
        return Ok();
    }
}
```

---

## 9. Installation Manual

### 9.1 Prerequisites

```
┌─────────────────────────────────────────────────────────────────┐
│                    SYSTEM REQUIREMENTS                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  SERVER (API + Database):                                       │
│  • Windows Server 2019+ or Windows 10/11 Pro                    │
│  • 4 GB RAM minimum (8 GB recommended)                          │
│  • 50 GB disk space                                             │
│  • .NET 8 Runtime                                               │
│  • PostgreSQL 15+                                               │
│                                                                 │
│  WORKSTATIONS (Desktop Client + Mail Service):                  │
│  • Windows 10/11                                                │
│  • 4 GB RAM minimum                                             │
│  • .NET 8 Desktop Runtime                                       │
│  • Microsoft Outlook 2016+ (installed and configured)           │
│  • Network access to API server                                 │
│                                                                 │
│  NETWORK:                                                       │
│  • All components on internal network or VPN                    │
│  • Port 5000 (or configured) open for API                       │
│  • Port 5432 open for PostgreSQL (server only)                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 9.2 Step-by-Step Installation

#### Step 1: Install PostgreSQL (Server)

```powershell
# Download PostgreSQL 15 from https://www.postgresql.org/download/windows/
# Run installer with default settings

# After installation, open pgAdmin or psql and run:
psql -U postgres

# Create database and user
CREATE USER leadgen_user WITH PASSWORD 'YourSecurePassword123!';
CREATE DATABASE leadgenerator OWNER leadgen_user;
GRANT ALL PRIVILEGES ON DATABASE leadgenerator TO leadgen_user;

# Exit psql
\q
```

#### Step 2: Initialize Database Schema

```powershell
# Navigate to scripts folder
cd C:\LeadGenerator\scripts\database

# Run schema scripts in order
psql -U leadgen_user -d leadgenerator -f 002_create_tables.sql
psql -U leadgen_user -d leadgenerator -f 003_seed_admin_user.sql
psql -U leadgen_user -d leadgenerator -f 004_create_indexes.sql
```

#### Step 3: Install API Server

```powershell
# Create installation directory
New-Item -ItemType Directory -Path "C:\LeadGenerator\Api" -Force
New-Item -ItemType Directory -Path "C:\LeadGenerator\Files" -Force
New-Item -ItemType Directory -Path "C:\LeadGenerator\Logs" -Force

# Copy API files
Copy-Item -Path ".\publish\Api\*" -Destination "C:\LeadGenerator\Api" -Recurse

# Edit configuration
notepad C:\LeadGenerator\Api\appsettings.json
# Update: ConnectionStrings:DefaultConnection
# Update: Jwt:Key (generate a secure 32+ character key)
# Update: FileStorage:BasePath

# Install as Windows Service
sc create "LeadGeneratorApi" binPath="C:\LeadGenerator\Api\LeadGenerator.Api.exe" start=auto
sc description "LeadGeneratorApi" "Lead Generator API Server"

# Start service
sc start LeadGeneratorApi

# Verify service is running
Invoke-RestMethod -Uri "http://localhost:5000/health" -Method Get
```

#### Step 4: Install Mail Service (Each Workstation)

```powershell
# Create installation directory
New-Item -ItemType Directory -Path "C:\LeadGenerator\MailService" -Force

# Copy Mail Service files
Copy-Item -Path ".\publish\MailService\*" -Destination "C:\LeadGenerator\MailService" -Recurse

# Edit configuration
notepad C:\LeadGenerator\MailService\appsettings.json
# Update: ApiBaseUrl (point to API server)
# Update: WorkstationId (unique identifier for this machine)

# Install as Windows Service
sc create "LeadGeneratorMailService" binPath="C:\LeadGenerator\MailService\LeadGenerator.MailService.exe" start=auto
sc description "LeadGeneratorMailService" "Lead Generator Mail Service"

# Configure service to run as user with Outlook access
# (Required for Outlook COM Interop)
sc config "LeadGeneratorMailService" obj="DOMAIN\Username" password="UserPassword"

# Start service
sc start LeadGeneratorMailService
```

#### Step 5: Install Desktop Client (Each Workstation)

```powershell
# Create installation directory
New-Item -ItemType Directory -Path "C:\Program Files\LeadGenerator" -Force

# Copy Desktop files
Copy-Item -Path ".\publish\Desktop\*" -Destination "C:\Program Files\LeadGenerator" -Recurse

# Edit configuration
notepad "C:\Program Files\LeadGenerator\appsettings.json"
# Update: ApiBaseUrl (point to API server)

# Create desktop shortcut
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:PUBLIC\Desktop\Lead Generator.lnk")
$Shortcut.TargetPath = "C:\Program Files\LeadGenerator\LeadGenerator.Desktop.exe"
$Shortcut.Save()
```

### 9.3 Post-Installation Verification

```powershell
# 1. Verify API is running
Invoke-RestMethod -Uri "http://YOUR_SERVER:5000/health"

# 2. Test login with default admin account
$body = @{ username = "admin"; password = "Admin123!" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://YOUR_SERVER:5000/api/auth/login" -Method Post -Body $body -ContentType "application/json"

# 3. Verify Mail Service is running
Get-Service "LeadGeneratorMailService"

# 4. Check logs for errors
Get-Content "C:\LeadGenerator\Logs\api-*.log" -Tail 50
Get-Content "C:\LeadGenerator\MailService\logs\mailservice-*.log" -Tail 50
```

---

## 10. Configuration Guide

### 10.1 appsettings.json (API Server)

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Host=localhost;Port=5432;Database=leadgenerator;Username=leadgen_user;Password=YOUR_PASSWORD"
  },
  "Jwt": {
    "Key": "YOUR_SUPER_SECRET_KEY_AT_LEAST_32_CHARACTERS_LONG!",
    "Issuer": "LeadGenerator",
    "Audience": "LeadGeneratorClients",
    "ExpirationMinutes": 480
  },
  "AllowedOrigins": [
    "http://localhost:*",
    "http://192.168.1.*"
  ],
  "FileStorage": {
    "BasePath": "C:\\LeadGenerator\\Files",
    "MaxFileSizeMB": 10,
    "AllowedExtensions": [".pdf", ".docx", ".xlsx", ".pptx", ".png", ".jpg"]
  },
  "CampaignDefaults": {
    "InterEmailDelayMinutes": 30,
    "SequenceStepDelayDays": 3,
    "SendingWindowStart": "09:00",
    "SendingWindowEnd": "17:00",
    "SendingDays": "Mon,Tue,Wed,Thu,Fri",
    "RandomizationMinutes": 15,
    "DailySendLimit": 50
  },
  "Unsubscribe": {
    "KeywordsEN": ["UNSUBSCRIBE", "STOP", "REMOVE", "OPT OUT", "OPT-OUT"],
    "KeywordsFR": ["DÉSINSCRIRE", "DÉSINSCRIPTION", "STOP", "ARRÊTER", "SUPPRIMER"]
  },
  "Security": {
    "MaxFailedLoginAttempts": 5,
    "LockoutMinutes": 15,
    "PasswordMinLength": 8,
    "RequireUppercase": true,
    "RequireNumber": true
  }
}
```

### 10.2 appsettings.json (Mail Service)

```json
{
  "ApiBaseUrl": "http://YOUR_SERVER:5000",
  "WorkstationId": "WORKSTATION-01",
  "ScanIntervalSeconds": 60,
  "Outlook": {
    "ScanFolders": ["Inbox", "Unsubscribe"],
    "ProcessedFolder": "Processed",
    "UseDefaultSignature": true
  },
  "Sending": {
    "MaxRetries": 3,
    "RetryDelayMinutes": 5,
    "RespectSendingWindow": true
  },
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft": "Warning"
    }
  }
}
```

### 10.3 appsettings.json (Desktop Client)

```json
{
  "ApiBaseUrl": "http://YOUR_SERVER:5000",
  "SessionTimeoutMinutes": 480,
  "AutoRefreshTokenMinutes": 60,
  "Logging": {
    "LogLevel": {
      "Default": "Warning"
    }
  }
}
```

### 10.4 First Login & Setup

```
┌─────────────────────────────────────────────────────────────────┐
│                    FIRST LOGIN CHECKLIST                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Login with default admin account:                           │
│     Username: admin                                             │
│     Password: Admin123!                                         │
│                                                                 │
│  2. IMMEDIATELY change admin password:                          │
│     Settings → My Account → Change Password                     │
│                                                                 │
│  3. Create additional users:                                    │
│     Settings → User Management → Add User                       │
│                                                                 │
│  4. Configure mail accounts:                                    │
│     Settings → Mail Accounts → Add Account                      │
│     • Enter Outlook email address                               │
│     • Set daily/hourly limits                                   │
│     • Assign to users                                           │
│                                                                 │
│  5. Create your first campaign:                                 │
│     Campaigns → New Campaign                                    │
│     • Import contact list (CSV)                                 │
│     • Create email sequence                                     │
│     • Configure sending schedule                                │
│     • Activate campaign                                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Quick Reference Commands

### Build & Publish

```powershell
# Build solution
dotnet build LeadGenerator.sln -c Release

# Publish API
dotnet publish src/LeadGenerator.Api -c Release -o ./publish/Api

# Publish Mail Service
dotnet publish src/LeadGenerator.MailService -c Release -o ./publish/MailService

# Publish Desktop
dotnet publish src/LeadGenerator.Desktop -c Release -o ./publish/Desktop
```

### Service Management

```powershell
# Start/Stop/Restart API
sc stop LeadGeneratorApi
sc start LeadGeneratorApi

# Start/Stop/Restart Mail Service
sc stop LeadGeneratorMailService
sc start LeadGeneratorMailService

# View service status
Get-Service LeadGenerator*
```

### Database Management

```powershell
# Backup database
pg_dump -U leadgen_user leadgenerator > backup_$(Get-Date -Format "yyyyMMdd").sql

# Restore database
psql -U leadgen_user -d leadgenerator < backup_20250127.sql

# Run EF migrations
dotnet ef database update --project src/LeadGenerator.Data
```

---

**End of Implementation Guide**
