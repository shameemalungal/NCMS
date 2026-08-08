# NCMS v1.0 Public Release Checklist

## Release baseline

- [x] NCMS v1.0 RC1 tagged as `ncms-v1.0-rc1`
- [x] Stable code pushed to `main`
- [x] Public submission separated from administrator-only modules
- [x] Administrator authentication and CSRF protection enabled
- [x] Backup route restricted to authenticated administrators
- [x] Production configuration uses environment variables for secrets
- [x] Production debug mode disabled
- [x] Production WSGI start command added
- [x] Health endpoint added at `/health`
- [x] Automated smoke tests added

## Local verification before deployment

Run:

```powershell
python -m pytest -q
flask routes
flask db upgrade
flask run
```

Then verify:

- `/health` returns HTTP 200.
- `/submit/` is accessible without administrator login.
- `/campaign/`, `/masterdata/`, `/monitoring/`, `/reports/`, `/settings/`, `/audit/`, and `/backup/download` require administrator authentication.
- Administrator login works with the production credentials stored in environment variables.
- Logout works and protected pages redirect to login afterwards.

## Public submission workflow

1. Select the active campaign's Panchayath.
2. Select the squad.
3. Confirm squad members and Pashudhan IDs.
4. Open the submission form.
5. Submit a valid completion report.
6. Confirm the success/reference page.
7. Attempt a second submission for the same squad and confirm it is blocked.
8. Close public submissions from Settings.
9. Confirm `/submit/` and direct form access are blocked while submissions are closed.
10. Re-open submissions and confirm the workflow works again.

## Data validation

- [ ] Import the actual squad/master-data Excel file.
- [ ] Confirm all expected Panchayaths are present.
- [ ] Confirm squad count matches the source file.
- [ ] Confirm squad members and Pashudhan IDs match the source file.
- [ ] Confirm duplicate Panchayath/squad detection works.
- [ ] Confirm failed rows are visible in the import result.
- [ ] Confirm imported data is restricted to the selected campaign.

## Reports and exports

- [ ] Dashboard totals match the underlying submissions.
- [ ] District Monitoring matches campaign totals.
- [ ] Panchayath Monitoring matches campaign totals.
- [ ] Squad Monitoring matches campaign totals.
- [ ] Panchayath Achievement export opens successfully in Excel.
- [ ] Pending Submissions export opens successfully in Excel.
- [ ] Squad-wise export opens successfully in Excel.
- [ ] NCMS Backup export opens successfully and contains all required sheets.

## Backup and recovery

- [ ] Download an NCMS backup before pilot data collection.
- [ ] Keep a copy outside the application server.
- [ ] Verify the workbook opens without corruption.
- [ ] Verify Campaigns, Panchayaths, Squads, Squad Members, Submissions, Import History, Audit Logs and Backup History are present.
- [ ] Perform one restore/recovery rehearsal before production data collection.

## Mobile and browser verification

Test the public submission workflow on:

- [ ] Android Chrome
- [ ] iPhone Safari
- [ ] Desktop Chrome/Edge/Firefox

Pay particular attention to:

- Panchayath selection
- Squad selection
- Member display
- Numeric inputs
- Validation messages
- Submit button
- Success/reference page

## Production deployment

Required environment variables:

```text
NCMS_ENVIRONMENT=production
NCMS_SECRET_KEY=<long-random-secret>
NCMS_ADMIN_USERNAME=<administrator-username>
NCMS_ADMIN_PASSWORD=<strong-unique-password>
NCMS_SESSION_COOKIE_SECURE=true
NCMS_TRUSTED_HOSTS=<production-hostname>
```

For Render, the repository includes `render.yaml` and a production WSGI command. If SQLite is used, the database directory must be on persistent storage. For a multi-instance deployment, use a production database such as PostgreSQL instead of SQLite.

## Pilot release

- [ ] Load the real campaign master data.
- [ ] Select the intended active campaign.
- [ ] Verify public submission is open only when intended.
- [ ] Send the public submission URL to a small pilot group.
- [ ] Collect several real submissions.
- [ ] Compare dashboard, monitoring and reports against the source records.
- [ ] Download a backup after the pilot.
- [ ] Fix only release-blocking defects.

## Final release

After the pilot passes:

```bash
git checkout main
git pull origin main
git tag -a ncms-v1.0 -m "NCMS Version 1.0"
git push origin ncms-v1.0
```

Do not begin multi-campaign, major UI redesign, or other v1.1 feature work until the v1.0 production baseline is accepted.
