# Lead Generator - Guide d'Installation Client-Serveur

**Version**: 260128-2
**Langue**: Francais

---

## Table des Matieres

1. [Presentation](#presentation)
2. [Architecture](#architecture)
3. [Configuration Requise](#configuration-requise)
4. [Partie 1 : Installation du Serveur](#partie-1--installation-du-serveur)
5. [Partie 2 : Installation des Postes de Travail](#partie-2--installation-des-postes-de-travail)
6. [Configuration Reseau](#configuration-reseau)
7. [Considerations de Securite](#considerations-de-securite)
8. [Configuration Post-Installation](#configuration-post-installation)
9. [Verification et Tests](#verification-et-tests)
10. [Depannage](#depannage)

---

## Presentation

Ce guide couvre l'installation distribuee de Lead Generator dans une architecture client-serveur. Cette configuration est recommandee pour :

- Equipes moyennes a grandes (5+ utilisateurs)
- Environnements de production
- Deployments multi-sites
- Exigences de haute disponibilite

### Scenarios de Deploiement

| Scenario | Serveur | Postes de travail | Ideal pour |
|----------|---------|-------------------|------------|
| Petit bureau | 1 serveur | 2-5 postes | Petites equipes |
| Bureau moyen | 1 serveur | 5-20 postes | Equipes en croissance |
| Entreprise | 1+ serveurs (avec basculement) | 20+ postes | Grandes organisations |

---

## Architecture

### Schema Reseau

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           RESEAU                                          │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                         SERVEUR                                      │ │
│  │                   (ex: 192.168.1.10)                                 │ │
│  │                                                                      │ │
│  │    ┌─────────────────┐         ┌─────────────────┐                  │ │
│  │    │ LeadGenerator   │         │   PostgreSQL    │                  │ │
│  │    │     API         │────────▶│   Base de       │                  │ │
│  │    │  (Port 5000)    │         │   donnees       │                  │ │
│  │    └────────┬────────┘         │  (Port 5432)    │                  │ │
│  │             │                   └─────────────────┘                  │ │
│  └─────────────┼────────────────────────────────────────────────────────┘ │
│                │                                                           │
│                │ HTTP/REST (Port 5000)                                    │
│                │                                                           │
│    ┌───────────┴───────────┬───────────────────┬───────────────────┐     │
│    │                       │                   │                   │     │
│    ▼                       ▼                   ▼                   ▼     │
│ ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────┐│
│ │   POSTE 1    │    │   POSTE 2    │    │   POSTE 3    │    │   ...    ││
│ │192.168.1.101 │    │192.168.1.102 │    │192.168.1.103 │    │          ││
│ │              │    │              │    │              │    │          ││
│ │┌────────────┐│    │┌────────────┐│    │┌────────────┐│    │          ││
│ ││  Client    ││    ││  Client    ││    ││  Client    ││    │          ││
│ ││  Bureau    ││    ││  Bureau    ││    ││  Bureau    ││    │          ││
│ │└────────────┘│    │└────────────┘│    │└────────────┘│    │          ││
│ │              │    │              │    │              │    │          ││
│ │┌────────────┐│    │┌────────────┐│    │              │    │          ││
│ ││Service Mail││    ││Service Mail││    │ (Pas de     │    │          ││
│ ││ + Outlook  ││    ││ + Outlook  ││    │  Service    │    │          ││
│ │└────────────┘│    │└────────────┘│    │  Mail)      │    │          ││
│ └──────────────┘    └──────────────┘    └──────────────┘    └──────────┘│
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

### Repartition des Composants

| Composant | Emplacement d'installation | Quantite |
|-----------|---------------------------|----------|
| Base de donnees PostgreSQL | Serveur | 1 |
| LeadGenerator.Api | Serveur | 1 |
| LeadGenerator.Desktop | Tous les postes de travail | N |
| LeadGenerator.MailService | Postes avec Outlook | 1-N |

---

## Configuration Requise

### Configuration Serveur

| Ressource | Minimum | Recommande |
|-----------|---------|------------|
| Processeur | 4 coeurs | 8+ coeurs |
| Memoire RAM | 8 Go | 16+ Go |
| Espace Disque | 100 Go SSD | 500 Go SSD |
| Reseau | 1 Gbps | 1 Gbps |
| Systeme | Windows Server 2019 | Windows Server 2022 |

**Logiciels Requis (Serveur)** :
- Runtime .NET 8 (ASP.NET Core)
- PostgreSQL 15+

### Configuration Poste de Travail

| Ressource | Minimum | Recommande |
|-----------|---------|------------|
| Processeur | 2 coeurs | 4 coeurs |
| Memoire RAM | 4 Go | 8 Go |
| Espace Disque | 10 Go | 20 Go |
| Reseau | 100 Mbps | 1 Gbps |
| Systeme | Windows 10 Pro | Windows 11 Pro |

**Logiciels Requis (Poste de travail)** :
- Runtime .NET 8 Desktop
- Microsoft Outlook 2016+ (uniquement pour les postes avec Service Mail)

### Configuration Reseau

| Port | Protocole | Direction | Utilisation |
|------|-----------|-----------|-------------|
| 5000 | TCP | Serveur ← Postes | Acces API |
| 5432 | TCP | Serveur uniquement | PostgreSQL (non expose) |
| 443 | TCP | Sortant | Envoi d'emails Outlook |

---

## Partie 1 : Installation du Serveur

### Etape 1.1 : Preparer le Serveur

1. Installer Windows Server 2019/2022
2. Configurer une adresse IP statique (ex : 192.168.1.10)
3. Definir le nom d'hote du serveur
4. Appliquer les mises a jour Windows

### Etape 1.2 : Installer le Runtime .NET 8

```powershell
# Telecharger et installer le Runtime ASP.NET Core .NET 8
# Depuis : https://dotnet.microsoft.com/download/dotnet/8.0

# Verifier l'installation
dotnet --list-runtimes
```

### Etape 1.3 : Installer PostgreSQL

1. Telecharger PostgreSQL 15+ depuis https://www.postgresql.org/download/windows/
2. Executer l'installateur en tant qu'Administrateur
3. Configuration pendant l'installation :
   - **Port** : 5432
   - **Mot de passe** : Definir un mot de passe fort pour l'utilisateur `postgres`
   - **Locale** : Par defaut
4. Terminer l'installation

### Etape 1.4 : Configurer PostgreSQL pour l'Acces Reseau

Modifier `C:\Program Files\PostgreSQL\15\data\postgresql.conf` :

```ini
# Ecouter uniquement sur localhost (securite)
listen_addresses = 'localhost'
```

Modifier `C:\Program Files\PostgreSQL\15\data\pg_hba.conf` :

```ini
# Autoriser uniquement les connexions locales (API sur le meme serveur)
# Connexions locales IPv4 :
host    all             all             127.0.0.1/32            scram-sha-256
```

Redemarrer PostgreSQL :

```powershell
net stop postgresql-x64-15
net start postgresql-x64-15
```

### Etape 1.5 : Creer la Base de Donnees

Se connecter a PostgreSQL :

```powershell
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres
```

Executer les commandes SQL :

```sql
-- Creer la base de donnees
CREATE DATABASE leadgenerator
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

-- Creer l'utilisateur applicatif
CREATE USER leadgen_user WITH PASSWORD 'VotreMotDePasseSecurise123!';

-- Accorder les privileges
GRANT ALL PRIVILEGES ON DATABASE leadgenerator TO leadgen_user;

\c leadgenerator

GRANT ALL ON SCHEMA public TO leadgen_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO leadgen_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO leadgen_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO leadgen_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO leadgen_user;
```

### Etape 1.6 : Executer les Scripts de Base de Donnees

```powershell
cd C:\LeadGenerator\Source

# Creer les tables
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U leadgen_user -d leadgenerator -f "scripts\database\002_create_tables.sql"

# Initialiser l'utilisateur admin
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U leadgen_user -d leadgenerator -f "scripts\database\003_seed_admin_user.sql"

# Creer les index
& "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U leadgen_user -d leadgenerator -f "scripts\database\004_create_indexes.sql"
```

### Etape 1.7 : Installer le Serveur API

Creer les repertoires :

```powershell
New-Item -ItemType Directory -Force -Path "C:\LeadGenerator\Api"
New-Item -ItemType Directory -Force -Path "C:\LeadGenerator\Files"
New-Item -ItemType Directory -Force -Path "C:\LeadGenerator\Logs"
```

Compiler et publier :

```powershell
cd C:\LeadGenerator\Source
dotnet publish src\LeadGenerator.Api -c Release -o C:\LeadGenerator\Api
```

### Etape 1.8 : Configurer l'API

Modifier `C:\LeadGenerator\Api\appsettings.json` :

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Host=localhost;Port=5432;Database=leadgenerator;Username=leadgen_user;Password=VotreMotDePasseSecurise123!"
  },
  "Jwt": {
    "Key": "VotreCleJWTTresSecuriseeAvecAuMoins32Caracteres!",
    "Issuer": "LeadGenerator",
    "Audience": "LeadGeneratorClients",
    "ExpirationMinutes": 480
  },
  "FileStorage": {
    "BasePath": "C:\\LeadGenerator\\Files",
    "MaxFileSizeMB": 10,
    "AllowedExtensions": [".pdf", ".docx", ".xlsx", ".pptx", ".png", ".jpg", ".jpeg"]
  },
  "CampaignDefaults": {
    "InterEmailDelayMinutes": 30,
    "SequenceStepDelayDays": 3,
    "SendingWindowStart": "09:00",
    "SendingWindowEnd": "17:00",
    "SendingDays": "Lun,Mar,Mer,Jeu,Ven",
    "DailySendLimit": 50
  },
  "Security": {
    "MaxFailedLoginAttempts": 5,
    "LockoutMinutes": 15,
    "PasswordMinLength": 8,
    "RequireUppercase": true,
    "RequireNumber": true
  },
  "Logging": {
    "LogLevel": {
      "Default": "Information"
    }
  },
  "AllowedHosts": "*",
  "Urls": "http://0.0.0.0:5000"
}
```

**Important** : Definir `Urls` sur `http://0.0.0.0:5000` pour ecouter sur toutes les interfaces.

### Etape 1.9 : Installer l'API en tant que Service Windows

```powershell
# Executer en tant qu'Administrateur
sc.exe create "LeadGeneratorApi" binPath="C:\LeadGenerator\Api\LeadGenerator.Api.exe" start=auto displayname="Lead Generator API"
sc.exe description "LeadGeneratorApi" "Serveur API REST Lead Generator"

# Demarrer le service
sc.exe start LeadGeneratorApi
```

### Etape 1.10 : Configurer le Pare-feu Windows

```powershell
# Autoriser le port API uniquement depuis le reseau interne
New-NetFirewallRule -DisplayName "Lead Generator API" `
    -Direction Inbound `
    -Port 5000 `
    -Protocol TCP `
    -Action Allow `
    -RemoteAddress 192.168.1.0/24  # Ajuster selon votre reseau
```

### Etape 1.11 : Verifier l'Installation du Serveur

Tester depuis le serveur :

```powershell
# Verification de sante
Invoke-RestMethod -Uri "http://localhost:5000/health"

# Doit retourner : Healthy
```

Acceder a l'interface Swagger : http://[IP-SERVEUR]:5000/swagger

---

## Partie 2 : Installation des Postes de Travail

Repeter ces etapes sur chaque poste de travail.

### Etape 2.1 : Installer les Prerequis

1. Installer le Runtime .NET 8 Desktop
   - Telecharger depuis : https://dotnet.microsoft.com/download/dotnet/8.0
   - Executer l'installateur en tant qu'Administrateur

2. (Si Service Mail necessaire) Installer et configurer Microsoft Outlook
   - S'assurer qu'au moins un compte de messagerie est configure
   - Tester l'envoi et la reception d'emails

### Etape 2.2 : Installer le Client Bureau

Creer le repertoire et copier les fichiers :

```powershell
# Creer le repertoire
New-Item -ItemType Directory -Force -Path "C:\Program Files\LeadGenerator\Desktop"

# Copier les fichiers publies depuis un partage reseau ou un package de deploiement
# OU compiler localement :
# dotnet publish src\LeadGenerator.Desktop -c Release -o "C:\Program Files\LeadGenerator\Desktop"
```

Configurer `C:\Program Files\LeadGenerator\Desktop\appsettings.json` :

```json
{
  "ApiSettings": {
    "BaseUrl": "http://192.168.1.10:5000",
    "Timeout": 30
  },
  "AppSettings": {
    "SessionTimeoutMinutes": 480,
    "AutoRefreshIntervalSeconds": 60
  }
}
```

**Important** : Remplacer `192.168.1.10` par l'adresse IP de votre serveur.

Creer un raccourci bureau :

```powershell
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:PUBLIC\Desktop\Lead Generator.lnk")
$Shortcut.TargetPath = "C:\Program Files\LeadGenerator\Desktop\LeadGenerator.Desktop.exe"
$Shortcut.WorkingDirectory = "C:\Program Files\LeadGenerator\Desktop"
$Shortcut.Description = "Client Bureau Lead Generator"
$Shortcut.Save()
```

### Etape 2.3 : Installer le Service Mail (Optionnel)

Installer uniquement sur les postes qui enverront des emails.

Creer les repertoires :

```powershell
New-Item -ItemType Directory -Force -Path "C:\LeadGenerator\MailService"
New-Item -ItemType Directory -Force -Path "C:\LeadGenerator\MailService\Logs"
```

Copier les fichiers :

```powershell
# Copier depuis un partage reseau ou un package de deploiement
# OU compiler localement :
# dotnet publish src\LeadGenerator.MailService -c Release -o C:\LeadGenerator\MailService
```

Configurer `C:\LeadGenerator\MailService\appsettings.json` :

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Host=192.168.1.10;Port=5432;Database=leadgenerator;Username=leadgen_user;Password=VotreMotDePasseSecurise123!"
  },
  "ApiSettings": {
    "BaseUrl": "http://192.168.1.10:5000",
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
- Remplacer `192.168.1.10` par l'adresse IP de votre serveur
- Definir un `WorkstationId` unique pour chaque poste (ex : POSTE-01, POSTE-02)

### Etape 2.4 : Configurer le Compte du Service Mail

Le Service Mail doit s'executer sous un compte utilisateur ayant acces a Outlook.

**Accorder l'autorisation "Ouvrir une session en tant que service"** :
1. Appuyer sur `Win + R`, taper `secpol.msc`, appuyer sur Entree
2. Naviguer vers : Strategies locales > Attribution des droits utilisateur
3. Double-cliquer sur "Ouvrir une session en tant que service"
4. Ajouter le compte utilisateur
5. Cliquer sur OK

**Installer le service** :

```powershell
# Executer en tant qu'Administrateur
sc.exe create "LeadGeneratorMailService" binPath="C:\LeadGenerator\MailService\LeadGenerator.MailService.exe" start=auto displayname="Lead Generator Service Mail"
sc.exe description "LeadGeneratorMailService" "Service de traitement des emails Lead Generator"

# Configurer pour s'executer sous un compte utilisateur
sc.exe config "LeadGeneratorMailService" obj=".\VotreNomUtilisateur" password="VotreMotDePasse"

# Demarrer le service
sc.exe start LeadGeneratorMailService
```

### Etape 2.5 : Configurer l'Acces PostgreSQL (Si le Service Mail se Connecte Directement)

Sur le **serveur**, ajouter les IPs des postes a `pg_hba.conf` :

```ini
# Autoriser les connexions du Service Mail depuis les postes
host    leadgenerator   leadgen_user    192.168.1.101/32        scram-sha-256
host    leadgenerator   leadgen_user    192.168.1.102/32        scram-sha-256
# Ajouter d'autres postes selon les besoins
```

Mettre a jour `postgresql.conf` pour ecouter sur le reseau :

```ini
listen_addresses = '192.168.1.10'  # IP du serveur uniquement
```

Ajouter une regle de pare-feu sur le serveur :

```powershell
New-NetFirewallRule -DisplayName "PostgreSQL - Services Mail" `
    -Direction Inbound `
    -Port 5432 `
    -Protocol TCP `
    -Action Allow `
    -RemoteAddress 192.168.1.101,192.168.1.102  # IPs specifiques des postes
```

Redemarrer PostgreSQL :

```powershell
net stop postgresql-x64-15
net start postgresql-x64-15
```

---

## Configuration Reseau

### Configuration DNS (Recommandee)

Configurer le DNS interne pour une gestion plus facile :

| Nom d'hote | Adresse IP | Utilisation |
|------------|------------|-------------|
| leadgen-serveur.interne | 192.168.1.10 | Serveur API |
| leadgen-bdd.interne | 192.168.1.10 | Base de donnees |

Mettre a jour les fichiers de configuration pour utiliser les noms d'hote au lieu des IPs.

### Configuration HTTPS (Recommandee pour la Production)

Pour les environnements de production, activer HTTPS :

1. **Obtenir un Certificat SSL**
   - Acheter aupres d'une Autorite de Certification, ou
   - Utiliser une PKI interne, ou
   - Utiliser Let's Encrypt

2. **Configurer l'API pour HTTPS**

Modifier `appsettings.json` :

```json
{
  "Kestrel": {
    "Endpoints": {
      "Http": {
        "Url": "http://0.0.0.0:5000"
      },
      "Https": {
        "Url": "https://0.0.0.0:5001",
        "Certificate": {
          "Path": "C:\\LeadGenerator\\Certs\\serveur.pfx",
          "Password": "MotDePasseCertificat"
        }
      }
    }
  }
}
```

3. **Mettre a Jour le Pare-feu**

```powershell
New-NetFirewallRule -DisplayName "Lead Generator API HTTPS" `
    -Direction Inbound `
    -Port 5001 `
    -Protocol TCP `
    -Action Allow `
    -RemoteAddress 192.168.1.0/24
```

4. **Mettre a Jour les Configurations Client**

Changer `BaseUrl` dans les configs des postes pour utiliser `https://`.

---

## Considerations de Securite

### Securite Reseau

1. **Regles de Pare-feu**
   - Autoriser l'acces API uniquement depuis le reseau interne
   - Restreindre PostgreSQL au serveur et aux postes autorises uniquement
   - Bloquer tous les ports inutiles

2. **Segmentation Reseau**
   - Envisager de placer le serveur dans un VLAN separe
   - Utiliser le DNS interne pour la decouverte des services

### Securite Applicative

1. **Changer les Identifiants par Defaut**
   - Changer le mot de passe admin immediatement apres l'installation
   - Utiliser des mots de passe forts pour tous les comptes

2. **Configuration JWT**
   - Utiliser une cle JWT forte et unique (32+ caracteres)
   - Envisager une expiration de jeton plus courte pour les environnements haute securite

3. **Securite Base de Donnees**
   - Utiliser des mots de passe de base de donnees forts
   - Limiter les permissions de l'utilisateur de base de donnees au minimum requis
   - Sauvegarde reguliere de la base de donnees

### Audit et Surveillance

1. **Activer les Logs**
   - Logs API : `C:\LeadGenerator\Logs`
   - Logs Service Mail : `C:\LeadGenerator\MailService\Logs`
   - Logs PostgreSQL : `C:\Program Files\PostgreSQL\15\data\log`

2. **Surveiller les Services**
   - Configurer des alertes pour les pannes de service
   - Surveiller l'espace disque et la taille de la base de donnees

---

## Configuration Post-Installation

### Etape 1 : Premiere Connexion Admin

1. Ouvrir le Client Bureau sur n'importe quel poste
2. Se connecter avec les identifiants par defaut :
   - Nom d'utilisateur : `admin`
   - Mot de passe : `Admin123!`
3. **Changer immediatement le mot de passe admin**

### Etape 2 : Enregistrer les Postes de Travail

1. Aller dans Parametres > Postes de travail
2. Ajouter chaque poste avec Service Mail :
   - ID du poste (doit correspondre a `appsettings.json`)
   - Description
   - Comptes mail assignes

### Etape 3 : Configurer les Comptes Mail

1. Aller dans Parametres > Comptes Mail
2. Ajouter les comptes Outlook de chaque poste
3. Associer les comptes aux postes

### Etape 4 : Creer les Utilisateurs

1. Aller dans Parametres > Utilisateurs
2. Creer des comptes pour les membres de l'equipe
3. Attribuer les roles appropries :
   - **Admin** : Acces complet
   - **Manager** : Gestion des campagnes
   - **User** : Acces limite

### Etape 5 : Tester l'Envoi d'Emails

1. Creer une liste de contacts test
2. Creer une campagne de test simple
3. Assigner a un poste avec Service Mail
4. Demarrer la campagne et verifier que les emails sont envoyes

---

## Verification et Tests

### Verification du Serveur

| Test | Commande | Resultat Attendu |
|------|----------|------------------|
| PostgreSQL en marche | `Get-Service postgresql*` | Running |
| API en marche | `Get-Service LeadGeneratorApi` | Running |
| Sante API | `curl http://localhost:5000/health` | Healthy |
| Connexion BDD | `psql -U leadgen_user -d leadgenerator -c "SELECT 1"` | Retourne 1 |

### Verification des Postes

| Test | Action | Resultat Attendu |
|------|--------|------------------|
| Reseau vers serveur | `ping 192.168.1.10` | Succes |
| Acces API | Navigateur : `http://192.168.1.10:5000/health` | Healthy |
| Client Bureau | Lancer et se connecter | Connexion reussie |
| Service Mail | `Get-Service LeadGeneratorMailService` | Running |

### Test de Bout en Bout

1. Se connecter au Client Bureau depuis un poste
2. Creer une liste de contacts avec un email de test
3. Creer et demarrer une campagne de test
4. Verifier :
   - La campagne apparait dans l'interface
   - Le Service Mail traite les emails
   - L'email de test est recu

---

## Depannage

### Le Poste ne Peut Pas se Connecter a l'API

**Symptomes** : Timeout ou connexion refusee

**Solutions** :
1. Verifier la connectivite reseau :
   ```powershell
   Test-NetConnection -ComputerName 192.168.1.10 -Port 5000
   ```
2. Verifier le pare-feu sur le serveur
3. Verifier que le service API fonctionne sur le serveur
4. Verifier que `appsettings.json` contient l'IP correcte du serveur

### Le Service Mail ne Peut Pas se Connecter a la Base de Donnees

**Symptomes** : Erreurs de connexion a la base de donnees dans les logs

**Solutions** :
1. Verifier que PostgreSQL autorise les connexions depuis l'IP du poste
2. Verifier que `pg_hba.conf` inclut l'IP du poste
3. Verifier que `postgresql.conf` ecoute sur l'IP du serveur
4. Verifier que le pare-feu autorise le port 5432 depuis le poste
5. Tester la connexion :
   ```powershell
   & "C:\Program Files\PostgreSQL\15\bin\psql.exe" -h 192.168.1.10 -U leadgen_user -d leadgenerator -c "SELECT 1"
   ```

### Le Service Mail n'Envoie Pas les Emails

**Symptomes** : Les emails restent en attente

**Solutions** :
1. Verifier les logs du Service Mail
2. Verifier qu'Outlook est configure pour le compte de service
3. Tester qu'Outlook peut envoyer manuellement
4. Verifier que WorkstationId correspond a la configuration dans la base de donnees
5. Verifier que le Service Mail est assigne aux bons comptes mail

### Problemes de Performance

**Symptomes** : Temps de reponse lents, timeouts

**Solutions** :
1. Verifier les ressources du serveur (CPU, RAM, disque)
2. Examiner les performances de PostgreSQL
3. Envisager d'ajouter des index pour les grandes tables
4. Examiner la bande passante reseau
5. Verifier les interferences antivirus

---

## Annexe : Liste de Controle de Deploiement

### Liste de Controle Serveur

- [ ] Windows Server installe et mis a jour
- [ ] IP statique configuree
- [ ] Runtime .NET 8 installe
- [ ] PostgreSQL installe et configure
- [ ] Base de donnees creee et initialisee
- [ ] API publiee et configuree
- [ ] API installee en tant que Service Windows
- [ ] Regles de pare-feu configurees
- [ ] Verification de sante API passante
- [ ] Mot de passe admin par defaut change

### Liste de Controle par Poste

- [ ] Runtime .NET 8 Desktop installe
- [ ] (Si necessaire) Outlook installe et configure
- [ ] Client Bureau installe et configure
- [ ] Le Client Bureau peut se connecter a l'API
- [ ] (Si necessaire) Service Mail installe
- [ ] (Si necessaire) Compte du Service Mail configure
- [ ] (Si necessaire) Service Mail en cours d'execution et connecte
- [ ] L'utilisateur peut se connecter avec succes

---

**Version du Document** : 1.0
**Derniere Mise a Jour** : Janvier 2026
**S'applique a** : Lead Generator v260128-2
