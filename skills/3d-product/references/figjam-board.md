# Posting a study to FigJam (the board style)

Review happens on FigJam boards: stills at full resolution, notes typed next to them, stamps as votes. Every board
follows the style below.

## Style
Grey sections `#E8E8E8`; white rounded boxes with a thin `#757575` stroke and 16 px charcoal (`#1E1E1E`) Inter Medium
text; elbowed `#757575` connectors with short lowercase labels; diamonds for decisions; images as cards with a
`#BDBDBD` 1 px stroke and 10 px radius; section titles Inter Bold 64; intro 22; captions 16. A process flow is a column
of white boxes ≈ 640 wide with a dashed "next" box at its end; image cards run 3-up in a grid, wide sheets full width.

## Routine
1. Collect the images (downscaled JPEG, ≤ 1600 px, unless the section is a full-resolution review, below) and their
   captions into a manifest. GIFs stay GIF (≤ 10 MB).
2. `upload_assets(fileKey, count ≤ 60)` → POST each file (multipart, filename = layer name, content type per
   extension). Replace an image in place with `upload_assets(nodeIds=[...])`.
3. One `use_figma` call per section (or 2–3 sections per call): create the section, title, intro, grid the images by
   name (`<idx>_<section>__<file>`), captions under each, verdict boxes in two columns, resize the section to fit.
4. Screenshot each section once; fix; stop.

Content rules: charts and figures are made from our own data and renders; never republish third-party frames or
product photos found by research. Public-domain patent drawings may go on a board.

## Section builder (reusable)
`scripts/figjam_section_builder.js` — paste into `use_figma` with `DATA` (sections: title, intro, flow of
[label, text], images [{n, c, w, h}], next, cols) and `START_Y` (it handles an empty board). Generate `DATA` from the
manifest after the upload. Build sections anywhere, then re-stack in reading order (one call). Boxes: measure text at
width FW−150 and add 96 px (FigJam shape padding) or text clips. Text-only sections read better narrowed to ≈ 2640
wide.
Traps: the canvas-wide `byName` lookup only sees *top-level* nodes (images already moved into a section are skipped);
clearing connector labels by text also clears flow-column labels — filter by endpoint.

## Board shape (user rule)
Keep each board near a screen aspect, about 1:1 to 1.6:1 landscape, never one long vertical strip (the author: "keep the
aspect ratio less extreme"). Lay sections out in columns (reading order column by column) or in row bands, with wide
grids such as a combination matrix in a top band. Add new sections as a new column or under the shortest column.
Estimate the total section area before building, and check the bounding box afterwards.

## Review boards: what the user reviews on
- **Full-resolution tiles:** every still at native 1920×1080, rows = shots, columns = variants, a caption above each
  tile, and an editable white "Notes · <shot>" box at the end of each row. Read the notes back with `get_figjam` and
  turn them into requirements (quoted verbatim in the shot list, `shots-and-script.md` §1).
- **One section per act or review round**, placed as a new column or under the shortest column. Typical builders: a
  stills grid (shots × variants), per-act FIRST | KEY | LAST sheets, a composition grid with title, subject,
  justification and a notes box per tile.
- **An editable film strip:** the edit's KEY strip in order (one tile per shot, open slots dashed) with the candidate
  frames floating beside it, so the user can drag candidates into slots and see the narrative. Read the arrangement
  back by position, then build exactly that (no parallel variants unless asked).
- **Stamps are votes:** the user thumbs-up-stamps tiles instead of typing. Read them with `use_figma`
  (`findAll(n => n.type === 'STAMP')`) and map each to the nearest tile; save the picks to a dated JSON.
- **Motion:** GIF fills render blank in the MCP screenshot API (the bytes are stored), so layer the KEY frame as a
  poster fill under each GIF; put MP4s in the review folder, not on the board.
- Every review section also goes to the review folder (`SKILL.md` stage 13), so the user can review on a phone.
