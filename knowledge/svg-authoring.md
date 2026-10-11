# SVG authoring notes (budget 0 USD art)

- Author in a fixed viewBox per kind: for example illustrations 500×350, portraits 96×96, icons 24×24 or 32×32 (the style bible sets the real ones).
- **Colours:** use the palette tokens as literal hex in the files (CSS variables do not reach `<img>`-loaded SVG). Use `currentColor` only for icons that the UI tints.
- **Reuse:**
  - shared ornaments (corners, vines, borders) become inline SVG components, so they can take tokens and be reused without network requests;
  - illustrations are files imported by Vite (hashed, cached).
- **Small files:**
  - round coordinates to 1 decimal;
  - `<symbol>`/`<use>` for repeats;
  - no editor metadata;
  - no embedded rasters;
  - no filters except a single blur for glows (expensive on phones; test the FPS).
- **Procedural generators** (foliage, stars, particles, map fog, filigree):
  - a small TypeScript or Python script with a seed, committed in `scripts/assets/`;
  - the output is committed too, so the build does not depend on running it.
- **Rendering contact sheets:** an HTML page that lays the SVGs out on the target background (the style bible's backgrounds), screenshotted with Playwright at 1x and 2x.
- **The silhouette test:** fill the shape black at 48 px. If it is not recognisable, simplify.
