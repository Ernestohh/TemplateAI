# Third-party assets

**Allowed licences:**
- CC0;
- CC-BY 3.0/4.0, with credit in LICENSES.md and the in-game Credits;
- SIL OFL 1.1 (fonts);
- MIT and Apache-2.0 (code).

**Not allowed:**
- anything ripped or extracted from commercial games, films or books;
- unclear or missing licences;
- "personal use only" or "non-commercial" without a real licence text;
- anything from the reference games;
- AI-generated packs with unclear provenance.

**For every file, record:** source URL, author, licence, local path, and whether it was modified. Record it in `Docs/LICENSES.md` and in the asset's `asset.json` (route `external`). Store the file under `assets/external/<source>/`.

**Places to look:**
- **Music:** CC0/CC-BY libraries that show the licence on each track page. Check the page itself, not a mirror. Prefer the instrumentation in TASK.md section 14.
- **Fonts:** `@fontsource/*` packages (the npm metadata states the licence). Keep the OFL text in the credits.

If nothing fits, build it procedurally (SVG or Web Audio) and log the decision.
