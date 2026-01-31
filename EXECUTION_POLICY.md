# PowerShell Execution Policy Setup for Lead Generator

## Understanding the Issue

When you download PowerShell scripts from the internet, Windows marks them as "blocked" for security. You'll see this error:

```
File cannot be loaded. The file is not digitally signed.
You cannot run this script on the current system.
```

## Solutions

### ✅ Recommended: Unblock Scripts Only

This is the **safest option** - it only affects Lead Generator scripts.

**Step 1:** Open PowerShell as Administrator
- Press `Win + X`
- Select "Windows PowerShell (Admin)" or "Terminal (Admin)"

**Step 2:** Navigate to the project directory

```powershell
cd D:\ProgramFiles\EmailSequence-main
```

**Step 3:** Unblock all PowerShell scripts

```powershell
Get-ChildItem -Recurse -Filter "*.ps1" | Unblock-File
```

**Step 4:** Verify scripts are unblocked

```powershell
# Should show no output if successful
Get-ChildItem -Recurse -Filter "*.ps1" | Get-Item | Select-Object FullName, @{Name="Blocked";Expression={(Get-Item $_.FullName).Attributes -band [System.IO.FileAttributes]::Offline}}
```

**Step 5:** Run your scripts normally

```powershell
.\build.ps1 -Target help
.\scripts\install\install-mailservice.ps1 -ApiServerUrl "http://server:5000" -WorkstationId "WS-01"
```

---

### 🔓 Alternative 1: Bypass for Current Session

This temporarily allows scripts **only in the current PowerShell window**.

```powershell
# Run this first
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Then run your script
.\build.ps1 -Target build
```

When you close PowerShell, the policy reverts to default.

---

### ⚙️ Alternative 2: Change Execution Policy (Permanent)

This changes the policy **permanently** on your system.

**For Current User Only:**

```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

**For All Users:**

```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy -Scope LocalMachine -ExecutionPolicy RemoteSigned
```

**Understanding Execution Policies:**

| Policy | Description |
|--------|-------------|
| `Restricted` | Default. No scripts allowed. |
| `RemoteSigned` | Local scripts run. Downloaded scripts must be signed. |
| `Unrestricted` | All scripts run (with warning for downloaded). |
| `Bypass` | No restrictions, no warnings. |

**⚠️ Security Note:** `RemoteSigned` is a good balance between security and usability.

---

### 🚀 Quick Unblock Script

Run this one-liner to unblock all scripts:

```powershell
# From project root directory
Get-ChildItem -Recurse -Filter "*.ps1" | Unblock-File; Write-Host "All scripts unblocked!" -ForegroundColor Green
```

---

## Verification

After applying any solution, verify it works:

```powershell
# Test with help command
.\build.ps1 -Target help

# Should display help information without errors
```

---

## Troubleshooting

### Still Getting Errors After Unblocking?

1. **Close and reopen PowerShell**
2. **Run as Administrator**
3. **Check file properties manually:**
   - Right-click the .ps1 file
   - Select "Properties"
   - Look for "Unblock" checkbox at the bottom
   - Check it and click "Apply"

### "Access Denied" Error?

You need to run PowerShell as **Administrator**:
- Press `Win + X`
- Select "Windows PowerShell (Admin)"

### Want to Check Current Policy?

```powershell
Get-ExecutionPolicy -List
```

This shows policies for all scopes.

---

## Best Practice for Teams

If deploying to multiple machines:

1. **Use Option 1 (Unblock)** on each machine
2. **Document this step** in your installation guide
3. **Create a batch file** to automate unblocking:

```batch
@echo off
echo Unblocking PowerShell scripts...
powershell -Command "Get-ChildItem -Recurse -Filter '*.ps1' | Unblock-File"
echo Done!
pause
```

---

## Security Considerations

**Why does Windows block scripts?**
- Protects against malicious scripts downloaded from the internet
- Prevents accidental execution of harmful code

**Is it safe to unblock Lead Generator scripts?**
- ✅ Yes, if you cloned from the official repository
- ✅ Yes, if you trust the source
- ⚠️ Always review scripts before unblocking from unknown sources

**What's the safest approach?**
1. Clone from official Git repository only
2. Use Option 1 (Unblock scripts manually)
3. Review scripts if you're security-conscious
4. Don't set `Unrestricted` policy unless necessary

---

## References

- Microsoft Docs: [about_Execution_Policies](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_execution_policies)
- Understanding `Unblock-File`: [Unblock-File Documentation](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/unblock-file)

---

**After fixing the execution policy, proceed with:**
- `QUICKSTART.md` for installation instructions
- `build.ps1 -Target help` to see available commands
