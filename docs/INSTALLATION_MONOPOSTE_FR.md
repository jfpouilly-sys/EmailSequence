# Lead Generator - Guide d'Installation Monoposte

**Version**: 260128-2
**Langue**: Francais

---

## Table des Matieres

1. [Presentation](#presentation)
2. [Configuration Requise](#configuration-requise)
3. [Installation des Prerequis](#installation-des-prerequis)
4. [Configuration de la Base de Donnees](#configuration-de-la-base-de-donnees)
5. [Installation du Serveur API](#installation-du-serveur-api)
6. [Installation du Client Bureau](#installation-du-client-bureau)
7. [Installation du Service Mail](#installation-du-service-mail)
8. [Configuration Post-Installation](#configuration-post-installation)
9. [Verification et Tests](#verification-et-tests)
10. [Depannage](#depannage)

---

## Presentation

Ce guide couvre l'installation de tous les composants Lead Generator sur une seule machine Windows. Cette configuration est ideale pour :

- Petites equipes (1-5 utilisateurs)
- Environnements de test et d'evaluation
- Configurations de developpement

### Composants Installes

| Composant | Description | Port |
|-----------|-------------|------|
| Base de donnees PostgreSQL | Stockage des donnees | 5432 |
| LeadGenerator.Api | Serveur API REST | 5000 |
| LeadGenerator.Desktop | Client Windows | - |
| LeadGenerator.MailService | Service de traitement des emails | - |

### Schema d'Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MACHINE UNIQUE                            │
│                                                              │
│  ┌─────────────────┐    ┌─────────────────┐                 │
│  │  Client Bureau  │───▶│  Serveur API    │                 │
│  │     (WPF)       │    │   (Port 5000)   │                 │
│  └─────────────────┘    └────────┬────────┘                 │
│                                  │                           │
│  ┌─────────────────┐             │                          │
│  │ Service Mail    │─────────────┼──────────┐               │
│  │(Service Windows)│             │          │               │
│  └────────┬────────┘             │          │               │
│           │                      ▼          │               │
│           │              ┌───────────────┐  │               │
│           │              │  PostgreSQL   │◀─┘               │
│           │              │  (Port 5432)  │                  │
│           │              └───────────────┘                  │
│           ▼                                                  │
│  ┌─────────────────┐                                        │
│  │ Microsoft       │                                        │
│  │ Outlook         │                                        │
│  └─────────────────┘                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## Configuration Requise

### Materiel

| Ressource | Minimum | Recommande |
|-----------|---------|------------|
| Processeur | 4 coeurs | 8 coeurs |
| Memoire RAM | 8 Go | 16 Go |
| Espace Disque | 50 Go SSD | 100 Go SSD |
| Reseau | 100 Mbps | 1 Gbps |

### Logiciels

| Logiciel | Version | Requis |
|----------|---------|--------|
| Windows | 10/11 Pro ou Server 2019+ | Oui |
| Runtime .NET | 8.0 | Oui |
| Runtime .NET Desktop | 8.0 | Oui |
| PostgreSQL | 15+ | Oui |
| Microsoft Outlook | 2016+ | Oui |

---

## Installation des Prerequis

### Etape 1 : Installer le Runtime .NET 8

1. Telecharger .NET 8 depuis : https://dotnet.microsoft.com/download/dotnet/8.0
2. Telecharger les deux composants :
   - **Runtime .NET 8.0** (pour l'API et le Service Mail)
   - **Runtime .NET Desktop 8.0** (pour le Client Bureau)
3. Executer les deux installateurs avec les privileges Administrateur
4. Verifier l'installation :

```powershell
dotnet --list-runtimes
```

Resultat attendu :
```
Microsoft.AspNetCore.App 8.0.x
Microsoft.NETCore.App 8.0.x
Microsoft.WindowsDesktop.App 8.0.x
```

### Etape 2 : Installer PostgreSQL

1. Telecharger PostgreSQL 15+ depuis : https://www.postgresql.org/download/windows/
2. Executer l'installateur en tant qu'Administrateur
3. Pendant l'installation :
   - **Repertoire d'installation** : `C:\Program Files\PostgreSQL\15`
   - **Repertoire des donnees** : `C:\Program Files\PostgreSQL\15\data`
   - **Mot de passe** : Definir un mot de passe fort pour l'utilisateur `postgres` (a retenir !)
   - **Port** : 5432 (par defaut)
   - **Locale** : Locale par defaut
4. Terminer l'installation
5. Verifier que PostgreSQL fonctionne :

```powershell
# Ouvrir PowerShell en tant qu'Administrateur
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -c "SELECT version();"
```

### Etape 3 : Installer Microsoft Outlook

1. Installer Microsoft Office 2016 ou ulterieur (Outlook requis)
2. Configurer au moins un compte de messagerie dans Outlook
3. S'assurer qu'Outlook demarre correctement et peut envoyer/recevoir des emails
4. Fermer Outlook apres verification

---

## Configuration de la Base de Donnees

### Etape 1 : Creer la Base de Donnees et l'Utilisateur

Ouvrir PowerShell en tant qu'Administrateur et naviguer vers le repertoire du projet :

```powershell
cd C:\LeadGenerator\Source
```

Se connecter a PostgreSQL et executer les scripts de configuration :

```powershell
# Se connecter a PostgreSQL
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres
```

Executer les commandes SQL suivantes (ou executer les fichiers de script) :

```sql
-- Creer la base de donnees
CREATE DATABASE leadgenerator
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'French_France.1252'
    LC_CTYPE = 'French_France.1252'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

-- Creer l'utilisateur applicatif
CREATE USER leadgen_user WITH PASSWORD 'ChangerCeMotDePasse123!';

-- Accorder les privileges
GRANT ALL PRIVILEGES ON DATABASE leadgenerator TO leadgen_user;

-- Se connecter a la nouvelle base de donnees
\c leadgenerator

-- Accorder les privileges sur le schema
GRANT ALL ON SCHEMA public TO leadgen_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO leadgen_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO leadgen_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO leadgen_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO leadgen_user;
```

### Etape 2 : Creer les Tables

Executer le script de creation des tables :

```powershell
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U leadgen_user -d leadgenerator -f "scripts\database\002_create_tables.sql"
```

### Etape 3 : Initialiser les Donnees

Executer le script d'initialisation pour creer l'utilisateur admin par defaut :

```powershell
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U leadgen_user -d leadgenerator -f "scripts\database\003_seed_admin_user.sql"
```

### Etape 4 : Creer les Index

Executer le script de creation des index :

```powershell
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U leadgen_user -d leadgenerator -f "scripts\database\004_create_indexes.sql"
```

---

## Installation du Serveur API

### Etape 1 : Creer la Structure de Repertoires

```powershell
# Executer en tant qu'Administrateur
New-Item -ItemType Directory -Force -Path "C:\LeadGenerator\Api"
New-Item -ItemType Directory -Force -Path "C:\LeadGenerator\Files"
New-Item -ItemType Directory -Force -Path "C:\LeadGenerator\Logs"
```

### Etape 2 : Compiler et Publier l'API

Naviguer vers le repertoire source et publier :

```powershell
cd C:\LeadGenerator\Source
dotnet publish src\LeadGenerator.Api -c Release -o C:\LeadGenerator\Api
```

### Etape 3 : Configurer l'API

Modifier `C:\LeadGenerator\Api\appsettings.json` :

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Host=localhost;Port=5432;Database=leadgenerator;Username=leadgen_user;Password=ChangerCeMotDePasse123!"
  },
  "Jwt": {
    "Key": "VotreCleSecreteSuperSecuriseeAvecAuMoins32Caracteres!",
    "Issuer": "LeadGenerator",
    "Audience": "LeadGeneratorClients",
    "ExpirationMinutes": 480
  },
  "FileStorage": {
    "BasePath": "C:\\LeadGenerator\\Files",
    "MaxFileSizeMB": 10,
    "AllowedExtensions": [".pdf", ".docx", ".xlsx", ".pptx", ".png", ".jpg", ".jpeg"]
  },
  "Logging": {
    "LogLevel": {
      "Default": "Information"
    }
  },
  "AllowedHosts": "*",
  "Urls": "http://localhost:5000"
}
```

**Important** : Modifier les valeurs suivantes :
- `Password` dans ConnectionStrings (doit correspondre au mot de passe de l'utilisateur de la base de donnees)
- `Key` dans la section Jwt (utiliser une cle forte et unique de 32+ caracteres)

### Etape 4 : Installer en tant que Service Windows

```powershell
# Executer en tant qu'Administrateur
sc.exe create "LeadGeneratorApi" binPath="C:\LeadGenerator\Api\LeadGenerator.Api.exe" start=auto displayname="Lead Generator API"
sc.exe description "LeadGeneratorApi" "Serveur API REST Lead Generator"

# Demarrer le service
sc.exe start LeadGeneratorApi
```

### Etape 5 : Configurer le Pare-feu Windows

```powershell
# Executer en tant qu'Administrateur
New-NetFirewallRule -DisplayName "Lead Generator API" -Direction Inbound -Port 5000 -Protocol TCP -Action Allow
```

### Etape 6 : Verifier l'Installation de l'API

Ouvrir un navigateur et acceder a :
- Verification de sante : http://localhost:5000/health
- Interface Swagger : http://localhost:5000/swagger

---

## Installation du Client Bureau

### Etape 1 : Creer le Repertoire

```powershell
New-Item -ItemType Directory -Force -Path "C:\Program Files\LeadGenerator\Desktop"
```

### Etape 2 : Compiler et Publier

```powershell
cd C:\LeadGenerator\Source
dotnet publish src\LeadGenerator.Desktop -c Release -o "C:\Program Files\LeadGenerator\Desktop"
```

### Etape 3 : Configurer le Client

Modifier `C:\Program Files\LeadGenerator\Desktop\appsettings.json` :

```json
{
  "ApiSettings": {
    "BaseUrl": "http://localhost:5000",
    "Timeout": 30
  },
  "AppSettings": {
    "SessionTimeoutMinutes": 480,
    "AutoRefreshIntervalSeconds": 60
  }
}
```

### Etape 4 : Creer un Raccourci Bureau

```powershell
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:PUBLIC\Desktop\Lead Generator.lnk")
$Shortcut.TargetPath = "C:\Program Files\LeadGenerator\Desktop\LeadGenerator.Desktop.exe"
$Shortcut.WorkingDirectory = "C:\Program Files\LeadGenerator\Desktop"
$Shortcut.Description = "Client Bureau Lead Generator"
$Shortcut.Save()
```

---

## Installation du Service Mail

### Etape 1 : Creer le Repertoire

```powershell
New-Item -ItemType Directory -Force -Path "C:\LeadGenerator\MailService"
New-Item -ItemType Directory -Force -Path "C:\LeadGenerator\MailService\Logs"
```

### Etape 2 : Compiler et Publier

```powershell
cd C:\LeadGenerator\Source
dotnet publish src\LeadGenerator.MailService -c Release -o C:\LeadGenerator\MailService
```

### Etape 3 : Configurer le Service Mail

Modifier `C:\LeadGenerator\MailService\appsettings.json` :

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Host=localhost;Port=5432;Database=leadgenerator;Username=leadgen_user;Password=ChangerCeMotDePasse123!"
  },
  "ApiSettings": {
    "BaseUrl": "http://localhost:5000",
    "Timeout": 30
  },
  "MailService": {
    "WorkstationId": "POSTE-01",
    "ScanIntervalSeconds": 60,
    "OutlookProfileName": "",
    "EnableReplyDetection": true,
    "EnableUnsubscribeDetection": true,
    "UnsubscribeKeywords": ["unsubscribe", "desabonner", "remove", "stop", "optout", "opt-out", "desinscription"]
  },
  "Logging": {
    "LogLevel": {
      "Default": "Information"
    }
  }
}
```

**Configuration Importante** :
- `WorkstationId` : Identifiant unique pour cette machine
- `OutlookProfileName` : Laisser vide pour utiliser le profil par defaut, ou specifier le nom du profil
- `UnsubscribeKeywords` : Ajouter les mots-cles pertinents pour vos campagnes

### Etape 4 : Installer en tant que Service Windows

Le Service Mail doit s'executer sous un compte utilisateur ayant Outlook configure :

```powershell
# Executer en tant qu'Administrateur

# Creer le service
sc.exe create "LeadGeneratorMailService" binPath="C:\LeadGenerator\MailService\LeadGenerator.MailService.exe" start=auto displayname="Lead Generator Service Mail"
sc.exe description "LeadGeneratorMailService" "Service de traitement des emails Lead Generator"

# Configurer pour s'executer sous un compte utilisateur (requis pour l'acces a Outlook)
# Remplacer DOMAINE\NomUtilisateur et mot de passe par les valeurs reelles
sc.exe config "LeadGeneratorMailService" obj=".\VotreNomUtilisateur" password="VotreMotDePasse"

# Demarrer le service
sc.exe start LeadGeneratorMailService
```

**Note** : Le compte utilisateur doit :
- Avoir Outlook installe et configure
- Avoir l'autorisation "Ouvrir une session en tant que service"
- Etre administrateur ou avoir les permissions appropriees

### Etape 5 : Accorder l'Autorisation "Ouvrir une session en tant que service"

1. Appuyer sur `Win + R`, taper `secpol.msc`, appuyer sur Entree
2. Naviguer vers : Strategies locales > Attribution des droits utilisateur
3. Double-cliquer sur "Ouvrir une session en tant que service"
4. Cliquer sur "Ajouter un utilisateur ou un groupe"
5. Ajouter le compte utilisateur qui executera le Service Mail
6. Cliquer sur OK et fermer

---

## Configuration Post-Installation

### Etape 1 : Changer le Mot de Passe Admin par Defaut

1. Ouvrir le Client Bureau
2. Se connecter avec les identifiants par defaut :
   - Nom d'utilisateur : `admin`
   - Mot de passe : `Admin123!`
3. Aller dans Parametres > Changer le mot de passe
4. Definir un mot de passe fort et unique

### Etape 2 : Configurer les Comptes Mail

1. Dans le Client Bureau, aller dans Parametres > Comptes Mail
2. Ajouter les comptes Outlook configures sur cette machine
3. Assigner les comptes aux utilisateurs selon les besoins

### Etape 3 : Creer des Utilisateurs Supplementaires

1. Aller dans Parametres > Utilisateurs
2. Creer des comptes pour les membres de votre equipe
3. Attribuer les roles appropries :
   - **Admin** : Acces complet au systeme
   - **Manager** : Gestion des campagnes, pas d'acces aux parametres systeme
   - **User** : Limite aux campagnes assignees

---

## Verification et Tests

### Liste de Verification

| Test | Commande/Action | Resultat Attendu |
|------|-----------------|------------------|
| Connexion base de donnees | `psql -U leadgen_user -d leadgenerator -c "SELECT 1"` | Retourne 1 |
| Sante API | Navigateur : `http://localhost:5000/health` | "Healthy" |
| Swagger API | Navigateur : `http://localhost:5000/swagger` | Interface Swagger chargee |
| Connexion Client Bureau | Ouvrir le Client Bureau, se connecter | Connexion reussie |
| Service Mail | `sc.exe query LeadGeneratorMailService` | RUNNING |

### Test d'Envoi d'Email

1. Creer une liste de contacts test avec votre propre email
2. Creer une campagne de test simple
3. Demarrer la campagne
4. Verifier que l'email est recu

---

## Depannage

### L'API ne Demarre Pas

**Symptomes** : Le service ne demarre pas, le port 5000 n'est pas accessible

**Solutions** :
1. Verifier les logs dans `C:\LeadGenerator\Logs`
2. Verifier que PostgreSQL fonctionne :
   ```powershell
   Get-Service postgresql*
   ```
3. Tester la connexion a la base de donnees :
   ```powershell
   & "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U leadgen_user -d leadgenerator -c "SELECT 1"
   ```
4. Verifier si le port 5000 est utilise :
   ```powershell
   netstat -ano | findstr :5000
   ```

### Le Service Mail ne Demarre Pas

**Symptomes** : Le service demarre mais s'arrete immediatement

**Solutions** :
1. Verifier les logs dans `C:\LeadGenerator\MailService\Logs`
2. Verifier que le compte de service a Outlook configure
3. Tester qu'Outlook s'ouvre correctement pour le compte de service
4. S'assurer que l'autorisation "Ouvrir une session en tant que service" est accordee

### Le Client Bureau ne Peut Pas se Connecter

**Symptomes** : Erreurs "Connexion refusee" ou timeout

**Solutions** :
1. Verifier que l'API fonctionne : `http://localhost:5000/health`
2. Verifier que `appsettings.json` contient l'URL correcte de l'API
3. Verifier que le pare-feu autorise le port 5000

### Problemes de Connexion a la Base de Donnees

**Symptomes** : "Connexion refusee" a PostgreSQL

**Solutions** :
1. Verifier que le service PostgreSQL fonctionne :
   ```powershell
   Get-Service postgresql*
   ```
2. Verifier que `pg_hba.conf` autorise les connexions locales
3. Verifier que le mot de passe dans la chaine de connexion correspond a l'utilisateur de la base de donnees

---

## Reference Rapide

### Commandes de Gestion des Services

```powershell
# Service API
sc.exe start LeadGeneratorApi
sc.exe stop LeadGeneratorApi
sc.exe query LeadGeneratorApi

# Service Mail
sc.exe start LeadGeneratorMailService
sc.exe stop LeadGeneratorMailService
sc.exe query LeadGeneratorMailService

# PostgreSQL
net start postgresql-x64-15
net stop postgresql-x64-15
```

### Emplacements des Fichiers Importants

| Element | Emplacement |
|---------|-------------|
| Application API | `C:\LeadGenerator\Api` |
| Configuration API | `C:\LeadGenerator\Api\appsettings.json` |
| Logs API | `C:\LeadGenerator\Logs` |
| Client Bureau | `C:\Program Files\LeadGenerator\Desktop` |
| Service Mail | `C:\LeadGenerator\MailService` |
| Logs Service Mail | `C:\LeadGenerator\MailService\Logs` |
| Stockage Fichiers | `C:\LeadGenerator\Files` |
| Donnees PostgreSQL | `C:\Program Files\PostgreSQL\15\data` |

### Identifiants par Defaut

| Compte | Nom d'utilisateur | Mot de passe | Notes |
|--------|-------------------|--------------|-------|
| Admin Application | admin | Admin123! | A CHANGER IMMEDIATEMENT |
| Utilisateur BDD | leadgen_user | ChangerCeMotDePasse123! | Mettre a jour dans les fichiers de config |

---

**Version du Document** : 1.0
**Derniere Mise a Jour** : Janvier 2026
**S'applique a** : Lead Generator v260128-2
