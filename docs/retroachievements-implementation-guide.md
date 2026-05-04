# RetroAchievements (rc_client) Implementation Guide

This guide captures the correct pattern for integrating rcheevos `rc_client` into an OpenEmu-Silicon core, along with the specific bugs we've hit in production. Read this before starting a new integration or reviewing an existing one.

The canonical reference implementations are:
- **Mednafen** — `Mednafen/MednafenGameCore.mm` (multi-system: PSX, PCE, Lynx, NGP)
- **Mupen64Plus** — `Mupen64Plus/MupenGameCore.m` (N64)

---

## Required call sequence during `loadFileAtPath:`

```objc
_rcClient = rc_client_create(my_rc_read_memory, oeRetroAchievementsServerCall);
rc_client_set_userdata(_rcClient, (__bridge void *)self);
rc_client_set_event_handler(_rcClient, my_rc_event_handler);
rc_client_set_hardcore_enabled(_rcClient, 0);
rc_client_set_allow_background_memory_reads(_rcClient, 0);  // ← REQUIRED. See pitfall #1.
rc_client_enable_logging(_rcClient, RC_CLIENT_LOG_LEVEL_WARN, my_rc_log);
```

Then set up the token observer and call `rc_client_begin_login_with_token()` when credentials arrive.

---

## Frame loop

Call `rc_client_do_frame()` once per emulated frame, inside whatever method drives emulation (typically `executeFrame` or `videoInterrupt`):

```objc
if (_rcClient) {
    rc_client_do_frame(_rcClient);
}
```

---

## Lifecycle hooks

| Event | Call |
|---|---|
| Game loading | `rc_client_begin_identify_and_load_game()` |
| Save state load | `rc_client_reset()` |
| Emulation reset | `rc_client_reset()` |
| Stop / dealloc | `rc_client_unload_game()` then `rc_client_destroy()` |

---

## Writing rc_read_memory correctly

The function signature rcheevos expects:

```c
static uint32_t my_rc_read_memory(uint32_t address, uint8_t *buffer,
                                  uint32_t num_bytes, rc_client_t *client)
{
    uint8_t *ram = /* pointer to emulated RAM */;
    size_t   sz  = /* size of that RAM region */;
    if (!ram || sz == 0) { return 0; }
    uint32_t end      = address + num_bytes;
    if (end > (uint32_t)sz) { end = (uint32_t)sz; }
    uint32_t readable = end - address;
    memcpy(buffer, ram + address, readable);
    return readable;
}
```

**Return value:** number of bytes actually read. Return 0 if the pointer is null or the region is empty. Return a partial count if the request extends past the end of RAM.

### Pitfall #2 — byte-swapping (N64-specific, do not copy to other systems)

The original Mupen64Plus implementation applied `buffer[i] = ram[addr ^ 3]` — an N64 big-endian byte-swap — to every byte. This was wrong.

Achievement conditions for N64 are authored against **raw little-endian host byte addresses**, matching the layout RetroArch/mupen64plus-next exposes via `retro_get_memory_data`. Mupen stores RDRAM as host-native 32-bit words, which is already in that layout. No swap is needed.

The fix is `memcpy` with no address manipulation, as shown above.

**Rule:** only apply a byte-swap if the achievement set for that system was authored against byte-swapped addresses, which is rare and will be documented explicitly by the rcheevos team. When in doubt, match what RetroArch's equivalent core does.

---

## Known pitfalls

### Pitfall #1 — Missing `rc_client_set_allow_background_memory_reads(_rcClient, 0)`

**Symptoms:** Achievements never fire. No errors in the log. The game loads and runs fine.

**Root cause:** By default, rcheevos validates achievement memrefs as soon as the game is identified — on the HTTP callback thread, before the emulator core has finished starting up. At that point, the emulated RAM pointer is null or zero-filled. Every address validates as invalid and rcheevos silently deactivates all achievements before the first frame.

**Fix:** Call `rc_client_set_allow_background_memory_reads(_rcClient, 0)` during `rc_client` initialization. This defers address validation to the `rc_client_do_frame()` call in the frame loop, where emulated RAM is guaranteed live.

**Affected cores fixed:** Mupen64Plus (PR #345), Mednafen (PR #346).

**Every new integration must include this call.** It is easy to omit because achievements appear to load (no error) and the game runs normally — the failure is silent.

### Pitfall #2 — See byte-swapping section above.

---

## Checklist for a new rc_client integration

- [ ] `rc_client_set_allow_background_memory_reads(_rcClient, 0)` called before logging setup
- [ ] `rc_client_do_frame()` called every emulated frame
- [ ] `rc_client_reset()` called on save state load and emulation reset
- [ ] `rc_client_unload_game()` + `rc_client_destroy()` called on stop/dealloc
- [ ] `rc_read_memory` returns 0 (not garbage) when RAM pointer is null
- [ ] `rc_read_memory` returns partial count when request exceeds RAM size
- [ ] No byte-swap unless the system's achievement set was explicitly authored against byte-swapped addresses
- [ ] `RC_CLIENT_EVENT_ACHIEVEMENT_TRIGGERED` posts `OEAchievementUnlockedNotification`
- [ ] Tested with a real game and achievement that fires in RetroArch — confirm it fires in OE too
