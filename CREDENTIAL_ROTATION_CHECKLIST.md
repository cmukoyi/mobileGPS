# 🔐 CREDENTIAL ROTATION CHECKLIST

**Date**: March 6, 2026  
**Status**: ⚠️ URGENT - Credentials were exposed in GitHub history

## ✅ Completed Actions
- [x] Removed secrets from git history
- [x] Force pushed to GitHub
- [x] Updated .gitignore

## 🚨 REQUIRED: Rotate These Credentials Immediately

### 1. Database Password (HIGH PRIORITY)
**Current Password (COMPROMISED)**: `hBY1d3jKNwN3iC7zAeNZKaIZjCBPUTkWDhlk2UK5Wq0=`

**Steps:**
```bash
# Generate new password
NEW_DB_PASSWORD=$(openssl rand -base64 48)
echo "New DB Password: $NEW_DB_PASSWORD"

# On production server, connect to database
docker exec -it ble_tracker_db psql -U postgres -d ble_tracker

# In PostgreSQL shell, change password:
ALTER USER ble_user WITH PASSWORD 'PASTE_NEW_PASSWORD_HERE';
\q

# Update production .env file on server
ssh root@161.35.38.209
cd /path/to/production
nano .env  # Update DATABASE_URL with new password

# Restart backend
docker-compose restart backend
```

**Status**: [ ] Not Started | [ ] In Progress | [ ] Completed

---

### 2. Application SECRET_KEY (HIGH PRIORITY)
**Current Key (COMPROMISED)**: `0382e405ce0ae7a631ac2c4eb666b5ce61a09519ce9a1e251992dabf7628eda4`

**Impact**: Can forge session tokens, JWT tokens, CSRF tokens

**Steps:**
```bash
# Generate new secret key
NEW_SECRET_KEY=$(openssl rand -hex 32)
echo "New SECRET_KEY: $NEW_SECRET_KEY"

# Update production .env file
ssh root@161.35.38.209
cd /path/to/production
nano .env  # Update SECRET_KEY

# Restart backend (this will invalidate all existing sessions)
docker-compose restart backend

# Update GitHub Secrets
# Go to: https://github.com/cmukoyi/mobileGPS/settings/secrets/actions
# Update SECRET_KEY with the new value
```

**Warning**: Changing this will log out all users!

**Status**: [ ] Not Started | [ ] In Progress | [ ] Completed

---

### 3. MZone API Credentials (CRITICAL)
**Compromised Credentials:**
- Client ID: `mz-scopeuk`
- Client Secret: `g_SkQ.B.z3TeBU$g%23hVeP%23c2`
- Username: `ScopeUKAPI`
- Password: `ScopeUKAPI01!`

**Impact**: Unauthorized access to GPS tracking API, potential data breach

**Steps:**
1. **Contact MZone Support IMMEDIATELY**
   - Email: [Add MZone support email]
   - Phone: [Add MZone support phone]
   - Request: Password reset for `ScopeUKAPI` account
   - Request: Rotate client secret if possible

2. **Review API Logs**
   - Check for unauthorized API calls
   - Look for unusual patterns between [date secrets were exposed] and now

3. **Update Credentials**
   ```bash
   # After receiving new credentials from MZone:
   ssh root@161.35.38.209
   cd /path/to/production
   nano .env
   # Update:
   # MZONE_CLIENT_SECRET=NEW_SECRET
   # MZONE_PASSWORD=NEW_PASSWORD
   
   docker-compose restart backend
   ```

4. **Update GitHub Secrets**
   - Go to repository settings → Secrets → Actions
   - Update `MZONE_CLIENT_SECRET`
   - Update `MZONE_PASSWORD`

**Status**: [ ] Not Started | [ ] In Progress | [ ] Completed

---

### 4. SendGrid API Key (MEDIUM PRIORITY)
**Current**: `SG.your_sendgrid_api_key_here` (appears to be placeholder?)

**Steps:**
1. **Verify if real key was exposed**
   ```bash
   # Check actual production .env file
   ssh root@161.35.38.209
   cat /path/to/production/.env | grep SENDGRID_API_KEY
   ```

2. **If real key exists, rotate it:**
   - Log into SendGrid: https://app.sendgrid.com/
   - Navigate to: Settings → API Keys
   - Find the old key and delete it
   - Create new API key with these permissions:
     - Mail Send → Full Access
     - Template Engine → Read Access (if using templates)
   - Copy the new key (you can only see it once!)

3. **Update Production**
   ```bash
   ssh root@161.35.38.209
   nano /path/to/production/.env
   # Update SENDGRID_API_KEY=NEW_KEY
   
   docker-compose restart backend
   ```

4. **Update GitHub Secrets**
   - Update `SENDGRID_API_KEY` in repository secrets

**Status**: [ ] Not Started | [ ] In Progress | [ ] Completed

---

### 5. Server SSH Access (HIGH PRIORITY)
**Server IP (EXPOSED)**: `161.35.38.209`

**Steps:**
1. **Check for unauthorized access**
   ```bash
   ssh root@161.35.38.209
   
   # Check authentication logs
   sudo tail -200 /var/log/auth.log | grep "Accepted"
   
   # Check active sessions
   who
   w
   
   # Check for suspicious processes
   ps aux | grep -v "^root" | grep -v "^www-data" | head -20
   ```

2. **Rotate SSH keys**
   ```bash
   # On server
   cd ~/.ssh
   
   # Backup old keys
   mv authorized_keys authorized_keys.backup
   
   # Generate new key pair locally
   ssh-keygen -t ed25519 -C "production-deployment" -f ~/.ssh/pinplot_production
   
   # Add new public key to server
   ssh-copy-id -i ~/.ssh/pinplot_production.pub root@161.35.38.209
   
   # Test new key works
   ssh -i ~/.ssh/pinplot_production root@161.35.38.209
   
   # If working, update GitHub secret
   # Go to repository settings → Secrets
   # Update DO_SSH_PRIVATE_KEY with contents of ~/.ssh/pinplot_production
   ```

**Status**: [ ] Not Started | [ ] In Progress | [ ] Completed

---

## 📊 Security Monitoring

### Immediate Monitoring (Next 7 Days)
- [ ] Check database logs daily for suspicious queries
- [ ] Monitor MZone API usage for anomalies
- [ ] Review server auth.log for unauthorized access attempts
- [ ] Monitor SendGrid for unusual email sending patterns
- [ ] Check application logs for failed authentication attempts

### Set Up Alerts
```bash
# On production server, add monitoring script:
cat > /root/security-check.sh << 'EOF'
#!/bin/bash
echo "=== Security Check $(date) ==="
echo "Failed SSH attempts:"
grep "Failed password" /var/log/auth.log | tail -10
echo ""
echo "Active database connections:"
docker exec ble_tracker_db psql -U ble_user -d ble_tracker -c "SELECT * FROM pg_stat_activity WHERE datname='ble_tracker';"
EOF

chmod +x /root/security-check.sh

# Add to cron (run daily)
(crontab -l 2>/dev/null; echo "0 9 * * * /root/security-check.sh >> /var/log/security-check.log 2>&1") | crontab -
```

---

## 🛡️ Prevention Measures Implemented

- [x] Updated `.gitignore` to block:
  - `backend.env.*` (except .example)
  - `PRODUCTION_CONFIG.md`
  - `SECURITY_INCIDENT_REMEDIATION.md`
  
- [ ] **TODO: Enable GitHub Secret Scanning**
  - Go to: https://github.com/cmukoyi/mobileGPS/settings/security_analysis
  - Enable "Secret scanning"
  - Enable "Push protection"

- [ ] **TODO: Add pre-commit hook**
  ```bash
  cat > .git/hooks/pre-commit << 'EOF'
  #!/bin/bash
  # Prevent committing sensitive files
  
  if git diff --cached --name-only | grep -E '\.env$|\.env\.|SECRET|PASSWORD|backend\.env\.'; then
      echo "❌ ERROR: Attempting to commit sensitive files!"
      echo "Files blocked:"
      git diff --cached --name-only | grep -E '\.env$|\.env\.|SECRET|PASSWORD'
      exit 1
  fi
  
  # Check for common secret patterns
  if git diff --cached -U0 | grep -iE 'password.*=|api.*key.*=|secret.*=|token.*=' | grep -v '+.*# Example'; then
      echo "⚠️  WARNING: Potential secret detected in commit!"
      git diff --cached | grep -iE 'password.*=|api.*key.*=|secret.*=|token.*='
      read -p "Continue anyway? (yes/no) " confirm
      if [ "$confirm" != "yes" ]; then
          exit 1
      fi
  fi
  EOF
  
  chmod +x .git/hooks/pre-commit
  ```

---

## 📝 Completion Checklist

- [ ] All passwords rotated
- [ ] All API keys rotated  
- [ ] SSH keys updated
- [ ] GitHub secrets updated
- [ ] Production services restarted
- [ ] Monitoring alerts configured
- [ ] Github secret scanning enabled
- [ ] Pre-commit hooks installed
- [ ] Team notified (if applicable)
- [ ] No unauthorized access detected
- [ ] All services tested and working

---

## 📞 Support Contacts

- **MZone API Support**: [Add contact]
- **SendGrid Support**: https://support.sendgrid.com/
- **Digital Ocean Support**: https://www.digitalocean.com/support/
- **Repository Owner**: Carlos Mukoyi (carlmukoyi@gmail.com)

---

**Last Updated**: March 6, 2026  
**Next Review**: After all credentials rotated
