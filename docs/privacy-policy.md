# Privacy Policy

**App:** OpenEmu-Silicon  
**Last updated:** May 3, 2026  
**Contact:** [Open an issue](https://github.com/nickybmon/OpenEmu-Silicon/issues)

---

## What this app does

OpenEmu-Silicon is a macOS game emulator. It runs locally on your computer. It does not create accounts, collect usage data, or connect to any server except when you explicitly enable the optional Google Drive Save Sync feature described below.

---

## Google Drive Save Sync (optional)

This feature lets you back up and sync your save states and battery saves to your own Google Drive. It is off by default and only activates after you sign in.

### What access is requested

OpenEmu-Silicon requests the `drive.appdata` scope. This gives the app access to a private, hidden App Data folder inside your Google Drive. This folder:

- Is not visible in the Google Drive web interface
- Cannot be read by other apps
- Can only be accessed by OpenEmu-Silicon

The app does **not** request access to your files, documents, photos, or any other part of your Google Drive.

### What is stored in your Drive

Only your game save data:

- Save state files (snapshots of game progress)
- Battery save files (in-game save data)

No personal information, no device identifiers, no usage metrics.

### How authentication works

Sign-in uses Google's standard OAuth 2.0 flow. Your Google account password is never seen or stored by the app. After you authorize access, Google issues an OAuth token. That token is stored locally in your macOS Keychain and is used only to read and write your save data to the App Data folder.

### Revoking access

You can disconnect Google Drive at any time from **Preferences → Cloud Sync → Sign Out**. This clears the stored token from your Keychain. You can also revoke access from your Google Account at [myaccount.google.com/permissions](https://myaccount.google.com/permissions).

---

## What this app does not do

- Does not collect analytics or usage data
- Does not transmit data to any server operated by this project
- Does not share any data with third parties
- Does not access your Google Drive files outside the hidden App Data folder
- Does not identify you by name, email, or device

---

## Open source

The full source code is available at [github.com/nickybmon/OpenEmu-Silicon](https://github.com/nickybmon/OpenEmu-Silicon). You can inspect exactly what data is read, written, and transmitted.

---

## Changes to this policy

If the app adds new network features that affect privacy, this document will be updated and the "Last updated" date above will change. Significant changes will be noted in the release notes.

---

## Contact

Questions or concerns? [Open an issue](https://github.com/nickybmon/OpenEmu-Silicon/issues) on GitHub.
