# Session 3 | File Integrity Monitoring (FIM) Lab

**Purpose:** Monitor only the three self-created demonstration files under `samples/` using SHA-256, keep a readable baseline and an AES-256 password-encrypted copy, and show ADDED / MODIFIED / DELETED changes against the **same original baseline**.

## Requirements

- Ubuntu or WSL Ubuntu shell, Python 3, GnuPG (`gpg`), and a screenshot tool.
- To install any missing packages in Ubuntu: `sudo apt update && sudo apt install -y python3 gnupg pinentry-curses unzip zip`.
- This lab does **not** scan or alter other people’s files or any Windows / Linux system files.

## Setup

1. Extract the starter ZIP and move the extracted `FIM_Integrity_Lab_Starter` folder into your Ubuntu home directory (open it from Ubuntu using `explorer.exe .`).
2. In Ubuntu: `cd ~/FIM_Integrity_Lab_Starter`
3. Confirm: `python3 --version && gpg --version && ls -l samples/`
4. Take screenshot 01 showing `ls -l samples/` and `date`.
5. Run **once only**: `python3 fim.py baseline`
6. Inspect the readable report: `cat baseline.txt`. Take screenshot 02 of command and hash/path entries.
7. Make the encrypted copy (interactive password prompt):

   ```bash
   export GPG_TTY=$(tty)
   gpg --symmetric --cipher-algo AES256 --output baseline.txt.gpg baseline.txt
   ls -l baseline.txt baseline.txt.gpg
   date
   ```

   Never type your passphrase as a command-line argument; never show it in screenshots or the final submission. Take screenshot 03 **after the password dialog is closed**.
8. Verify that decryption gives exactly the trusted baseline (optional extra-credit evidence):

   ```bash
   gpg --output verify_decrypted.txt --decrypt baseline.txt.gpg
   cmp -s baseline.txt verify_decrypted.txt && echo '[PASS] Decrypted baseline matches the original.'
   rm -- verify_decrypted.txt
   date
   ```

   The password prompt happens privately. Decryption evidence is already included alongside the clean check in screenshot 04; ensure no password or key is visible.
9. Initial clean check: `python3 fim.py check`. Take screenshot 04; the evidence here includes the decryption comparison and clean initial check.

## Do the three tests in this exact order (DO NOT RECREATE BASELINE)

**Test ADDED** (screenshot 05):

```bash
printf 'New demo file created after baseline.\n' > samples/new_file.txt
python3 fim.py check
date
```

Expected: `[ADDED] samples/new_file.txt`.

**Test MODIFIED** (screenshot 06):

```bash
printf 'This line changes the trusted file hash.\n' >> samples/notes.txt
python3 fim.py check
date
```

Expected: `[MODIFIED] samples/notes.txt` **plus** the earlier `[ADDED]` result because changes accumulate.

**Test DELETED** (screenshot 07):

```bash
rm -- samples/config.txt
python3 fim.py check
date
```

Expected: `[DELETED] samples/config.txt`, **plus** the earlier ADDED and MODIFIED alerts.

**Final summary** (screenshot 08):

```bash
python3 fim.py check
date
```

Expected: `Summary: ADDED=1, MODIFIED=1, DELETED=1, UNCHANGED=1`.

**Each screenshot must visibly include the action command, FIM checker result, and date/time** (terminal timestamps count). Screenshot filenames below are recommended. In Windows you can use `Win + Shift + S`, then save each image as `.png` under `screenshots/`. The completed report includes all eight real screenshots captured during the experiment.

## Important integrity / encryption explanation

- A SHA-256 hash acts as a content fingerprint: if file bytes change, the digest will almost certainly change. FIM compares known-good baseline digests with current ones.
- Encrypting `baseline.txt` to `baseline.txt.gpg` protects **confidentiality of the encrypted copy** if the password stays secret, but it does not make the readable copy confidential.
- Encryption **alone** does not prove the baseline is authentic or protected against replacement. An attacker who can alter the trusted baseline may hide changes. For real protection use restricted permissions and an independently authenticated baseline (e.g. verified digital signature / keyed MAC with properly separated key).
- The checker is **on demand**, not a continuous background service. It only inspects regular files under `samples/`, not file metadata, access permissions, file contents outside that directory, or changes made and reverted between checks. File names containing newlines are unsupported. The plain-text baseline remains a possible tampering target.
- `fim.py check` exit code 0 means clean; 1 means changes detected; 2 means an operational error.

## Tools used & AI disclosure

- Ubuntu terminal/WSL: create files and execute commands.
- Python 3 built-in `hashlib`: generate and compare SHA-256 digests.
- GnuPG (`gpg`): symmetric AES-256 encryption and verification via decryption.
- `cmp`, `ls`, `printf`, `rm`, `date`: inspection, controlled test actions, comparison, timestamp.
- Screenshot tool: image evidence.
- ChatGPT: assisted with planning the exercise, preparing the example code, explanations, and documentation. The student must run the lab and understand the script.

## What to submit

- `fim.py`
- `samples/` test folder (the modified state is fine)
- `baseline.txt` (original readable SHA-256 hash baseline)
- `baseline.txt.gpg` (encrypted copy)
- `FIM_Report.docx` with screenshots already inserted; fill your roll number and actual submission date
- `screenshots/01...08.png` 
- `README.md` (this file)

**Do not submit:** password/passphrase/key, `verify_decrypted.txt`, unrelated personal data or real system files.

### Original baseline must never be regenerated during the tests

Creating a new baseline after you add/modify/delete a sample would cause the checker to consider the changed state "normal" and invalidate the requested results. If you want to repeat the lab from scratch, start with a fresh extracted starter folder and new passphrase.

## Create the final submission ZIP (after pasting your screenshots in the report)

From your Ubuntu home directory: `cd ~ && zip -r FIM_Final_Submission.zip FIM_Integrity_Lab_Starter`. Use `explorer.exe .` to find the ZIP and upload it to your class portal. Do not include your GPG password/key.

## Verified run (30 October 2026, PKT)

The student performed the experiment in Ubuntu/WSL. GPG successfully decrypted and compared the stored baseline (`[PASS]`); the initial file check was clean with three unchanged files. After the three controlled tests, the checker reported `ADDED=1, MODIFIED=1, DELETED=1, UNCHANGED=1`. These observed outputs are documented in `FIM_Report.docx` with timestamped screenshots.
