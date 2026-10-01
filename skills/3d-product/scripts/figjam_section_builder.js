// FigJam section builder (the board style in references/figjam-board.md) — paste into a use_figma call after setting DATA and START_Y.
// DATA = [{key, title, intro, cols?, flow: [[label, text], ...], images: [{n: nodeName, c: caption, w, h}], next}]
// Images must already be uploaded (upload_assets → your upload script) as FRAME nodes named `<section>__<name>`.
// Style: grey #E8E8E8 sections 3600 wide; title Inter Bold 64; intro 22; a flow column of white rounded boxes (640 wide,
// #757575 stroke, 16 px charcoal, left-aligned) joined by elbowed #757575 connectors with lowercase labels; a dashed
// "next" box; image cards (10 px radius, #BDBDBD stroke) in a 2- or 3-up grid, wide sheets (aspect > 2.2) full width.
const h = (r, g, b) => ({ r: r / 255, g: g / 255, b: b / 255 });
const CH = h(0x1e, 0x1e, 0x1e), GR = h(0x75, 0x75, 0x75), CARD = h(0xbd, 0xbd, 0xbd), WH = h(255, 255, 255), SEC = h(0xe8, 0xe8, 0xe8);
const BOLD = { family: 'Inter', style: 'Bold' }, MED = { family: 'Inter', style: 'Medium' };
await figma.loadFontAsync(BOLD); await figma.loadFontAsync(MED);
const page = figma.currentPage;
const byName = {}; for (const n of page.children) byName[n.name] = n;
const W = 3600, P = 120, FW = 640, GX = P + FW + 140, GW = W - GX - P, GAP = 60;
const measurer = figma.createText(); measurer.fontName = MED; measurer.fontSize = 16; measurer.textAutoResize = 'HEIGHT'; measurer.resize(FW - 150, 20);
const out = [];
let y = START_Y;
for (const D of DATA) {
  const COLS = D.cols || 3, CW = (GW - GAP * (COLS - 1)) / COLS;
  const sec = figma.createSection(); sec.name = D.key; sec.x = 0; sec.y = y; sec.resize(W, 2000);
  sec.fills = [{ type: 'SOLID', color: SEC }];
  const T = (s, size, font, w) => { const t = figma.createText(); t.fontName = font; t.characters = s; t.fontSize = size; t.fills = [{ type: 'SOLID', color: CH }]; if (w) { t.textAutoResize = 'HEIGHT'; t.resize(w, t.height); } sec.appendChild(t); return t; };
  const title = T(D.title, 64, BOLD); title.x = P; title.y = P;
  const intro = T(D.intro, 22, MED, 2400); intro.x = P; intro.y = title.y + title.height + 28;
  const y0 = intro.y + intro.height + 100;
  let fy = y0, prev = null, flowBottom = y0;
  const box = (text, dashed) => {
    measurer.characters = text; const hh = Math.max(96, measurer.height + 96);   // FigJam shape padding ≈ 75 px a side
    const s = figma.createShapeWithText(); s.shapeType = 'ROUNDED_RECTANGLE';
    s.text.fontName = MED; s.text.characters = text; s.text.fontSize = 16;
    try { s.text.textAlignHorizontal = 'LEFT'; } catch (e) {}
    s.resize(FW, hh); s.fills = [{ type: 'SOLID', color: WH }]; s.strokes = [{ type: 'SOLID', color: GR }]; s.text.fills = [{ type: 'SOLID', color: CH }];
    if (dashed) { try { s.dashPattern = [8, 6]; } catch (e) {} }
    sec.appendChild(s); return s;
  };
  const link = (a, b, label) => {
    const c = figma.createConnector(); sec.appendChild(c);
    c.connectorStart = { endpointNodeId: a.id, magnet: 'BOTTOM' }; c.connectorEnd = { endpointNodeId: b.id, magnet: 'TOP' };
    c.connectorLineType = 'ELBOWED'; c.strokes = [{ type: 'SOLID', color: GR }]; c.connectorStartStrokeCap = 'NONE'; c.connectorEndStrokeCap = 'ARROW_LINES';
    if (label) { c.text.fontName = MED; c.text.characters = label; }
    return c;
  };
  for (const [label, text] of D.flow) {
    const s = box(text); s.x = P; s.y = fy;
    if (prev) link(prev, s, label); else { const l = T(label, 16, MED); l.x = P; l.y = fy - 30; }
    prev = s; fy += s.height + 110; flowBottom = s.y + s.height;
  }
  if (D.next) { const n = box(D.next, true); n.x = P; n.y = fy; link(prev, n, 'next'); flowBottom = n.y + n.height; }
  let gx = 0, gy = y0, rowH = 0, placed = 0, miss = [];
  for (const im of D.images) {
    const node = byName[im.n]; if (!node) { miss.push(im.n); continue; }
    const wide = im.w / im.h > 2.2; const w = wide ? GW : CW; const hgt = Math.round(w * im.h / im.w);
    if ((wide && gx > 0) || (!wide && gx + w > GW + 1)) { gy += rowH + GAP; gx = 0; rowH = 0; }
    sec.appendChild(node); node.resize(w, hgt); node.x = GX + gx; node.y = gy;
    node.cornerRadius = 10; node.strokes = [{ type: 'SOLID', color: CARD }]; node.strokeWeight = 1;
    const c = T(im.c, 16, MED, w); c.x = GX + gx; c.y = gy + hgt + 14;
    rowH = Math.max(rowH, hgt + 14 + c.height); placed++;
    if (wide) { gy += rowH + GAP; gx = 0; rowH = 0; } else gx += w + GAP;
  }
  const bottom = Math.max(flowBottom, gy + rowH) + P;
  sec.resize(W, bottom);
  out.push({ key: D.key, id: sec.id, y: sec.y, h: Math.round(sec.height), placed, miss });
  y = sec.y + sec.height + 300;
}
measurer.remove();
return out;
