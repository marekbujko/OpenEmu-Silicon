## What's New in 1.0.8

### RetroAchievements — Phase 2 🏆

Two more systems now earn achievements automatically while you play:

**Nintendo 64 (Mupen64Plus)** — N64 achievements are fully live. Log in once in Preferences → Achievements and your existing token carries over.

**PlayStation, PC Engine, Lynx, Neo Geo Pocket (Mednafen)** — PSX (including multi-disc games), PC Engine / TurboGrafx-16, Atari Lynx, and Neo Geo Pocket Color are all supported.

The full list of RA-supported systems now includes: GBA, GB/GBC, SNES, NES, Genesis / Mega Drive / CD / SG-1000, Master System / Game Gear, N64, PSX, PC Engine, Lynx, and NGP.

---

### Google Drive saves now visible in Finder

Save files synced to Google Drive are stored in a top-level **OpenEmu Saves** folder in your Drive, instead of a hidden app-data location. This makes it easy to see, download, or back up your saves directly from drive.google.com or the macOS Drive app.

---

## Bug Fixes

- **ROM files can now be re-imported after deletion.** If you deleted a game from your library and tried to add the same ROM again, OpenEmu silently skipped it because the stale database entry was still present. The entry is now cleaned up on delete so re-import works.
- **Game Scanner now has a Cancel button.** The "Resolve Issues" sheet that appears when imports need attention previously had no way to dismiss it without resolving every item.
- **Window resizing no longer leaves ghost content layers.** Maximizing or resizing the main window could leave semi-transparent artifacts from the previous layout overlaid on the new one. The content view is now correctly redrawn on resize.
- **Dreamcast games no longer play at half speed (27fps).** The Flycast JIT compiler was disabled, halving performance. JIT is re-enabled and the dynamic frame timeout is restored.
- **Dreamcast games no longer show a black screen on second launch.** A Flycast option override applied during `loadGame` was being reset before it took effect. The override now sticks.
- **PSX multi-disc games no longer require a manual .m3u file.** Mednafen now auto-generates the playlist for multi-disc sets so they load without any setup.
- **Input Monitoring permission is now correctly detected at launch.** If Input Monitoring was already granted before the app launched, OpenEmu would show the permission prompt again and controllers would not respond. This is fixed.
- **ScreenScraper now recognises 16 additional systems.** Covers, screenshots, and metadata were not fetching for systems whose IDs were missing from the mapping table.
- **Keychain reads no longer block the main thread.** Loading the RetroAchievements token at launch could cause a brief freeze, especially on first run. Tokens are now cached in memory after the first read.
- **Cheats are now saved and re-applied on game start.** User-added cheat codes were lost between sessions. Enabled cheats are now persisted to disk and automatically re-applied when the game loads.
- **Preferences no longer shows duplicate ColecoVision rows.** The Cores tab was resolving system names incorrectly, producing ghost rows for ColecoVision and a few other systems.
- **FCEU games now render correctly when running from a Release build.** Pixels were not being written to the framebuffer on the execute frame path used by Release and notarised builds, causing a black screen.
- **Google Drive OAuth now completes correctly.** The redirect URI handler was being called on the wrong thread, causing the sign-in flow to silently stall after the browser handoff.

## Core Updates

*(Core release notes will be added here before publishing.)*
