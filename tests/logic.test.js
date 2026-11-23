// Draai met: node tests/logic.test.js
// Speelt volledige tornooien na (3 tot 40 spelers) en controleert de logica uit index.html.
const fs = require('fs'), path = require('path'), assert = require('assert');
const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');
const src = html.match(/<script>([\s\S]*?)<\/script>/)[1].split('/* =========================================================================\n   Opslag')[0];
const window = {};
const TT = new Function('window', src + '\nreturn TT;')(window);

let seed = 42;
const rnd = () => { seed = (seed * 1664525 + 1013904223) % 4294967296; return seed / 4294967296; };
const pick = a => a[Math.floor(rnd() * a.length)];

function randomSets(bo, h = [0, 0], lead = [0, 0]) {
  if (lead[0] || lead[1]) {            // voorgift: gewone sets tot 11, score nooit onder de voorsprong
    return randomSets(bo).map(([x, y]) => [Math.max(x, lead[0]), Math.max(y, lead[1])]);
  }
  const need = Math.ceil(bo / 2), sets = [], T = 11 + Math.max(h[0], h[1]); let a = 0, b = 0;
  while (a < need && b < need) {
    const p1wins = rnd() < 0.5, hW = h[p1wins ? 0 : 1], hL = h[p1wins ? 1 : 0];
    const lose = Math.floor(rnd() * 12), win = Math.max(T, lose + hL + 2) - hW;
    if (p1wins) { sets.push([win, lose]); a++; } else { sets.push([lose, win]); b++; }
  }
  return sets;
}
// speelt één wedstrijd (poule of eindronde door elkaar)
function playOne(s) {
  TT.autoAssign(s);
  const playing = s.matches.filter(m => m.table && !TT.isDone(m));
  const seen = new Set();
  playing.forEach(m => [m.p1, m.p2].forEach(p => { assert(!seen.has(p), 'speler aan twee tafels'); assert(!TT.isToken(p)); seen.add(p); }));
  const m = pick(playing);
  TT.setResult(s, m.id, { sets: randomSets(m.bo, TT.targets(s, m).h, TT.targets(s, m).lead) });
}
function playAll(s, check) {
  let guard = 0;
  while (true) {
    TT.autoAssign(s);
    const playing = s.matches.filter(m => m.table && !TT.isDone(m));
    if (!playing.length) break;
    // geen speler aan twee tafels tegelijk
    const seen = new Set();
    playing.forEach(m => [m.p1, m.p2].forEach(p => { assert(!seen.has(p), 'speler aan twee tafels'); seen.add(p); }));
    assert(new Set(playing.map(m => m.table)).size === playing.length, 'tafel dubbel gebruikt');
    const m = pick(playing);
    TT.setResult(s, m.id, { sets: randomSets(m.bo, TT.targets(s, m).h, TT.targets(s, m).lead) });
    if (check) check(m);
    assert(guard++ < 5000);
  }
}

// --- volgorde in een poule van 4: 1-4, 2-3, 1-3, 2-4, 1-2, 3-4 (hoogst geplaatste eerst)
{
  const s = TT.newState();
  s.poules = [{ id: 'A', players: ['1', '2', '3', '4'] }, { id: 'B', players: ['1', '2', '3'] }, { id: 'C', players: ['1', '2', '3', '4', '5'] }];
  s.players = ['1', '2', '3', '4', '5'].map(id => ({ id, name: id, rank: 'NG' }));
  TT.startPoules(s);
  const ord = p => s.matches.filter(m => m.poule === p).map(m => m.p1 + '-' + m.p2).join(' ');
  assert.strictEqual(ord('A'), '1-4 2-3 1-3 2-4 1-2 3-4');
  assert.strictEqual(ord('B'), '2-3 1-3 1-2');
  assert(s.matches.every(m => m.p1 < m.p2));
}
// --- pouleblad: vast nummer per speler (volgorde van de loting), ook bij gelijk klassement
{
  const s = TT.newState();
  s.players = [['a', 'Pauwels', 'C2'], ['b', 'Props', 'E4'], ['c', 'De Moerloose', 'E4'], ['d', 'De Vos', 'NG']].map(([id, name, rank]) => ({ id, name, rank }));
  s.poules = [{ id: 'A', players: ['a', 'c', 'b', 'd'] }];           // De Moerloose is nr 2, Props nr 3
  TT.startPoules(s);
  assert.deepStrictEqual(s.matches.map(m => m.p1 + m.p2), ['ad', 'cb', 'ab', 'cd', 'ac', 'bd']);
  const rows = TT.pouleStandings(s, 'A').rows;
  assert.deepStrictEqual(rows.map(r => r.id + r.nr), ['a1', 'c2', 'b3', 'd4'], 'voor de start: volgorde van het pouleblad');
  TT.setResult(s, s.matches[1].id, { sets: [[5, 11], [5, 11]] });      // nr 3 wint van nr 2
  const r2 = TT.pouleStandings(s, 'A').rows;
  assert.strictEqual(r2[0].id, 'b');
  assert.strictEqual(r2.find(r => r.id === 'b').nr, 3, 'nummer blijft vast');
}
// --- kleine eenheden
assert.deepStrictEqual(TT.parseSet('11-7'), [11, 7]);
assert.deepStrictEqual(TT.parseSet('7'), [11, 7]);
assert.deepStrictEqual(TT.parseSet('-9'), [9, 11]);
assert.deepStrictEqual(TT.parseSet('12'), [14, 12]);
assert.deepStrictEqual(TT.parseSet('-0'), [0, 11]);
assert.strictEqual(TT.parseSet(''), null);
assert.strictEqual(TT.parseSet('abc'), undefined);
assert(TT.validSet([11, 9]) && TT.validSet([15, 13]) && !TT.validSet([11, 10]) && !TT.validSet([13, 9]) && !TT.validSet([10, 8]));
assert(TT.checkSets([[11, 5], [11, 5]], 3).ok);
assert(!TT.checkSets([[11, 5], [5, 11]], 3).ok);
assert(!TT.checkSets([[11, 5], [11, 5], [11, 5]], 3).ok);
assert(TT.checkSets([[11, 5], [5, 11], [11, 5], [11, 5]], 5).ok);

for (let n = 3; n <= 60; n++) {
  const sz = TT.pouleSizes(n, 4);
  assert.strictEqual(sz.reduce((a, b) => a + b, 0), n);
  assert(sz.every(x => x >= 3 && x <= (n === 5 ? 5 : 4)), `poulegrootte fout bij ${n}: ${sz}`);
}

// --- onderling resultaat bij gelijkstand: A>B, B>C, C>A, allen winnen van D
{
  const s = TT.newState();
  ['A', 'B', 'C', 'D'].forEach(n => s.players.push({ id: n, name: n, rank: 'NG' }));
  s.poules = [{ id: 'A', players: ['A', 'B', 'C', 'D'] }];
  TT.startPoules(s);
  const res = (x, y, sets) => { const m = s.matches.find(m => (m.p1 === x && m.p2 === y) || (m.p1 === y && m.p2 === x)); TT.setResult(s, m.id, { sets: m.p1 === x ? sets : sets.map(([a, b]) => [b, a]) }); };
  res('A', 'B', [[11, 2], [11, 2]]);          // A wint 2-0
  res('B', 'C', [[11, 9], [9, 11], [11, 9]]); // B wint 2-1
  res('C', 'A', [[11, 9], [9, 11], [11, 9]]); // C wint 2-1
  ['A', 'B', 'C'].forEach(x => res(x, 'D', [[11, 1], [11, 1]]));
  // onderling sets: A 3-2, B 2-3, C 3-3  -> A, C, B
  assert.deepStrictEqual(TT.pouleStandings(s, 'A').rows.map(r => r.id), ['A', 'C', 'B', 'D']);
}

// --- slangsysteem en clubtabellen (zoals 'Tabellen voor eindrondes')
{
  const mk = n => Array.from({ length: n }, (_, i) => ({ id: 'p' + (i + 1), name: 'S' + (i + 1), rank: 'NG' }));
  const snake = n => TT.drawPoules(mk(n), 4).map(p => p.players.join(' '));
  assert.deepStrictEqual(snake(7), ['p1 p4 p5', 'p2 p3 p6 p7']);
  assert.deepStrictEqual(snake(10), ['p1 p6 p7', 'p2 p5 p8', 'p3 p4 p9 p10']);
  assert.deepStrictEqual(snake(16), ['p1 p8 p9 p16', 'p2 p7 p10 p15', 'p3 p6 p11 p14', 'p4 p5 p12 p13']);
  const s29 = snake(29);
  assert.deepStrictEqual(s29.map(x => x.split(' ').length), [3, 3, 3, 4, 4, 4, 4, 4]);
  assert.strictEqual(s29[0], 'p1 p16 p17');
  assert.strictEqual(s29[3], 'p4 p13 p20 p29');
  assert.strictEqual(s29[7], 'p8 p9 p24 p25');
  // tabel 1&2 en 3&4 van 5 poules bij 17 spelers
  const s = TT.newState();
  s.players = mk(17);
  s.poules = TT.drawPoules(s.players, 4);
  TT.startPoules(s);
  // de hoogst geplaatste wint altijd: stand in elke poule = volgorde in de poule
  const idx = id => +id.slice(1);
  const playSeeded = () => { for (;;) { const m = s.matches.find(m => !TT.isDone(m) && TT.isPlayable(m)); if (!m) break; const need = Math.ceil(m.bo / 2); TT.setResult(s, m.id, { score: idx(m.p1) < idx(m.p2) ? [need, 0] : [0, need] }); } };
  playSeeded();
  TT.startKnockout(s);
  const name = id => { if (id === 'BYE') return '-'; const p = s.poules.find(p => p.players.includes(id)); return p.id + (p.players.indexOf(id) + 1); };
  const first = kind => s.matches.filter(m => m.kind === kind && m.gsize === m.B).sort((a, b) => a.idx - b.idx).flatMap(m => [name(m.p1), name(m.p2)]).join(' ');
  assert.strictEqual(first('main'), 'A1 - B2 C2 E1 - - D1 C1 - - E2 D2 A2 - B1');
  assert.strictEqual(first('cons'), 'A3 - - - E3 - - D3 C3 - - E4 D4 - - B3');
  playSeeded();
  const fr = TT.finalRanking(s);
  assert.deepStrictEqual(fr.map(x => x.pos), Array.from({ length: 17 }, (_, i) => i + 1));
  assert.strictEqual(fr[0].pid, 'p1');
}

// --- volledige tornooien
const RANKS = ['B2', 'B6', 'C0', 'C2', 'C4', 'C6', 'D0', 'D2', 'D4', 'D6', 'E0', 'E2', 'E4', 'E6', 'NG'];
for (let n = 3; n <= 40; n++) for (let rep = 0; rep < 15; rep++) for (const cons of [true, false]) {
  const s = TT.newState();
  s.settings.consolation = cons;
  s.settings.handicap = ['lead', 'target', 'none', 'lead', 'target'][rep % 5]; s.settings.hcRound = rep % 2 ? 'up' : 'down';
  s.settings.tables = 1 + Math.floor(rnd() * 8);
  for (let i = 0; i < n; i++) s.players.push({ id: TT.nextId(s, 'p'), name: 'Speler ' + (i + 1), rank: pick(RANKS) });
  s.poules = TT.drawPoules(s.players, s.settings.pouleSize, rep % 2 === 1, rnd);
  const k = s.poules.length;
  assert.strictEqual(s.poules.flatMap(p => p.players).length, n);
  assert.strictEqual(new Set(s.poules.flatMap(p => p.players)).size, n);
  // potten: de k sterkste spelers zitten elk in een andere poule, enz.
  const sorted = s.players.slice().sort((a, b) => TT.rankValue(a.rank) - TT.rankValue(b.rank));
  for (let pot = 0; (pot + 1) * k <= n; pot++) {
    const worst = TT.rankValue(sorted[(pot + 1) * k - 1].rank), best = TT.rankValue(sorted[pot * k].rank);
    s.poules.forEach(p => assert(p.players.some(id => { const v = TT.rankValue(s.players.find(x => x.id === id).rank); return v >= best && v <= worst; }), 'pot niet verdeeld'));
  }
  s.poules.forEach(p => assert(p.players.length >= 3 || n < 3));
  TT.startPoules(s);
  const early = rep % 4 >= 2;   // eindrondes al aanmaken vóór de poules gespeeld zijn
  if (early) TT.startKnockout(s);
  s.poules.forEach(p => {
    const ms = s.matches.filter(m => m.poule === p.id), c = p.players.length;
    assert.strictEqual(ms.length, c * (c - 1) / 2);
    assert.strictEqual(new Set(ms.map(m => [m.p1, m.p2].sort().join())).size, ms.length);
  });
  if (early) { let g = 0; while (!TT.allPoulesDone(s)) { playOne(s); assert(g++ < 5000); } } else playAll(s);
  assert(TT.allPoulesDone(s));
  s.poules.forEach(p => { const st = TT.pouleStandings(s, p.id); assert(st.complete); assert.strictEqual(new Set(st.rows.map(r => r.id)).size, p.players.length); });
  if (!early) TT.startKnockout(s);
  assert(!s.matches.some(m => m.kind !== 'poule' && (TT.isToken(m.p1) || TT.isToken(m.p2) || TT.isToken(m.winner))), 'plaatshouder niet ingevuld');
  const main = s.matches.filter(m => m.kind === 'main');
  const Q = Math.min(2, 99) * k;
  // eerste ronde: geen twee spelers uit dezelfde poule tegen elkaar (als er minstens 2 poules zijn)
  const pouleOf = id => s.poules.find(p => p.players.includes(id))?.id;
  if (k >= 2) main.filter(m => m.gsize === m.B && TT.isPlayable(m)).forEach(m => assert.notStrictEqual(pouleOf(m.p1), pouleOf(m.p2), `zelfde poule in ronde 1 (n=${n})`));
  // poulewinnaars krijgen de vrije rondes
  {
    const byes = main.filter(m => m.gsize === m.B && m.bye).map(m => m.winner);
    const winners = s.poules.map(p => TT.pouleStandings(s, p.id).rows[0].id);
    if (byes.length <= k) byes.forEach(b => assert(winners.includes(b), 'vrije ronde niet naar poulewinnaar'));
    else winners.forEach(w => assert(byes.includes(w), 'poulewinnaar zonder vrije ronde'));
  }
  // best of 5 enkel voor plaatsen 1-4 van de hoofdtabel
  s.matches.filter(m => m.kind !== 'poule').forEach(m => assert.strictEqual(m.bo, m.kind === 'main' && m.gstart + m.gsize - 1 <= 4 ? 5 : 3));
  playAll(s);
  assert(s.matches.every(m => TT.isDone(m)), 'niet alle wedstrijden gespeeld');
  const fr = TT.finalRanking(s);
  const expected = cons ? n : (n >= 3 ? Math.min(n, Q) : 0);
  assert.strictEqual(fr.length, expected, `eindklassement ${fr.length} != ${expected} (n=${n})`);
  assert.deepStrictEqual(fr.map(x => x.pos), Array.from({ length: expected }, (_, i) => i + 1), `plaatsen niet doorlopend (n=${n})`);
  assert.strictEqual(new Set(fr.map(x => x.pid)).size, expected);
  // vrije plaatsen eindigen altijd onderaan: labels "Plaats x-y" kloppen dus
  ['main', 'cons'].forEach(kind => {
    const fin = s.matches.filter(m => m.kind === kind && m.gsize === 2);
    const slots = fin.flatMap(m => [[m.gstart, m.winner], [m.gstart + 1, m.winner === m.p1 ? m.p2 : m.p1]]).sort((a, b) => a[0] - b[0]);
    const firstBye = slots.findIndex(x => x[1] === 'BYE');
    if (firstBye >= 0) assert(slots.slice(firstBye).every(x => x[1] === 'BYE'), `vrije plaats boven echte speler (n=${n})`);
  });
  const pod = TT.podium(s, 'main');
  assert(pod && pod.first === fr[0].pid && pod.second === fr[1].pid);
  // uitslag van de finale wijzigen kan, eerdere ronde niet meer
  const final = s.matches.find(m => m.kind === 'main' && m.gstart === 1 && m.gsize === 2);
  TT.setResult(s, final.id, { wo: final.winner === final.p1 ? 1 : 2 });
  assert.strictEqual(TT.podium(s, 'main').first, pod.second);
  const semi = s.matches.find(m => m.kind === 'main' && m.gstart === 1 && m.gsize === 4 && !m.bye);
  if (semi) assert.throws(() => TT.clearResult(s, semi.id));
  // wissen en opnieuw ingeven van een kwartfinale-achtige wedstrijd na terugdraaien
  if (semi) {
    s.matches.filter(m => m.kind === 'main' && m.gsize === 2 && m.gstart <= 3 && !m.bye).forEach(m => TT.clearResult(s, m.id));
    TT.clearResult(s, semi.id);
    assert(!s.matches.filter(m => m.kind === 'main' && m.gsize === 2 && m.gstart <= 3).some(m => m.p1 && m.p2 && m.p1 !== 'BYE' && m.p2 !== 'BYE' && TT.isDone(m)));
    playAll(s);
    assert(s.matches.every(m => TT.isDone(m)));
    assert.strictEqual(TT.finalRanking(s).length, expected);
  }
}

// --- afmelden en laatkomer
{
  const s = TT.newState();
  for (let i = 0; i < 17; i++) s.players.push({ id: TT.nextId(s, 'p'), name: 'S' + i, rank: pick(RANKS) });
  s.poules = TT.drawPoules(s.players, 4);
  TT.startPoules(s);
  const before = s.matches.length, target = s.poules.find(p => p.players.length === 3);
  const late = TT.addLatePlayer(s, 'Laat', 'D4', target.id);
  assert.strictEqual(s.matches.length, before + 3);
  const gone = s.poules[0].players[0];
  TT.withdraw(s, gone);
  assert(s.matches.filter(m => m.p1 === gone || m.p2 === gone).every(m => m.winner && m.winner !== gone));
  playAll(s);
  TT.startKnockout(s);
  assert(!s.matches.some(m => m.kind !== 'poule' && (m.p1 === gone || m.p2 === gone)));
  playAll(s);
  const fr = TT.finalRanking(s);
  assert.strictEqual(fr.length, 17);
  assert(fr.some(x => x.pid === late.id));
}
// --- voorgift (sterkste speelt tot 11 + n) en scheidsrechter
{
  const s = TT.newState();
  [['a', 'B0'], ['b', 'B2'], ['c', 'C0'], ['d', 'NG'], ['e', 'A'], ['f', '']].forEach(([id, rank]) => s.players.push({ id, name: id, rank }));
  const tg = (p1, p2) => TT.targets(s, { p1, p2 });
  assert.strictEqual(s.settings.handicap, 'lead');             // standaard: voorgift
  // voorgift: laagst geklasseerde start met voorsprong, iedereen tot 11
  assert.deepStrictEqual(tg('a', 'b').lead, [0, 0]);           // 1 klassement: niets
  assert.deepStrictEqual([tg('a', 'c').lead, tg('a', 'c').t, tg('a', 'c').h], [[0, 2], [11, 11], [0, 0]]);
  assert.deepStrictEqual(tg('c', 'a').lead, [2, 0]);
  assert.deepStrictEqual(tg('a', 'd').lead, [0, 8]);           // B0-NG: 16 klassementen -> 8
  assert.deepStrictEqual(tg('d', 'f').lead, [0, 0]);
  {
    const l = tg('a', 'c').lead;                               // c start met 2-0
    assert(TT.validSet([11, 7], [0, 0], l) && TT.validSet([9, 11], [0, 0], l) && TT.validSet([11, 2], [0, 0], l) && TT.validSet([14, 12], [0, 0], l));
    assert(!TT.validSet([11, 1], [0, 0], l), 'c begon al met 2');
    assert(!TT.validSet([13, 7], [0, 0], l) && !TT.validSet([11, 10], [0, 0], l), 'gewone regels tot 11');
    assert.deepStrictEqual(TT.checkSets([[11, 7], [9, 11], [11, 5]], 3, [0, 0], l).score, [2, 1]);
    assert(!TT.checkSets([[11, 0], [11, 5]], 3, [0, 0], l).ok);
    s.poules = [{ id: 'A', players: ['a', 'c', 'd'] }];
    TT.startPoules(s);
    const mm = s.matches.find(m => m.p1 === 'a' && m.p2 === 'c');
    assert.throws(() => TT.setResult(s, mm.id, { sets: [[11, 1], [11, 5]] }));
    TT.setResult(s, mm.id, { sets: [[11, 5], [11, 5]] });
    assert.strictEqual(mm.winner, 'a');
    s.matches = []; s.poules = [];
  }
  // oude back-ups: zonder uitslagen -> voorgift, met uitslagen blijft het oude systeem
  assert.deepStrictEqual(TT.migrate({ settings: { handicap: 'half' }, matches: [] }).settings, { handicap: 'lead', hcRound: 'down', drawTie: 'az' });
  assert.deepStrictEqual(TT.migrate({ settings: { handicap: 'up' }, matches: [{ winner: 'x' }] }).settings, { handicap: 'target', hcRound: 'up', drawTie: 'az' });
  assert.strictEqual(TT.migrate({ settings: { handicap: 'none' } }).settings.handicap, 'none');
  s.settings.handicap = 'none';
  assert.deepStrictEqual(tg('a', 'd').t, [11, 11]);            // uit
  assert.deepStrictEqual(tg('a', 'd').lead, [0, 0]);
  s.settings.handicap = 'target';                              // handicap: sterkste speelt verder
  assert.deepStrictEqual(tg('a', 'b').t, [11, 11]);            // 1 klassement: niets
  assert.deepStrictEqual(tg('a', 'c').t, [13, 11]);            // B0-C0: 4 klassementen -> +2
  assert.deepStrictEqual(tg('c', 'a').t, [11, 13]);
  assert.deepStrictEqual(tg('a', 'd').t, [19, 11]);            // B0-NG: 16 klassementen -> +8
  assert.deepStrictEqual(tg('b', 'd').t, [18, 11]);            // B2-NG: 15 -> +7
  assert.deepStrictEqual(tg('d', 'f').t, [11, 11]);            // geen klassement = NG
  s.settings.hcRound = 'up';
  assert.deepStrictEqual(tg('a', 'b').t, [12, 11]);
  s.settings.hcRound = 'down';
  const h = tg('a', 'c').h;                                    // a tot 13, c tot 11
  assert.deepStrictEqual(h, [0, 2]);
  assert(TT.validSet([13, 7], h) && TT.validSet([9, 11], h) && TT.validSet([12, 11], h));
  assert(!TT.validSet([11, 7], h), 'sterkste moet 13 halen');
  assert(!TT.validSet([13, 11], h), 'beiden op doelscore kan niet');
  assert(TT.validSet([15, 11], h) && TT.validSet([13, 13], h), 'verlenging met 2 verschil');
  assert.deepStrictEqual(TT.parseSet('7', h), [13, 7]);
  assert.deepStrictEqual(TT.parseSet('-9', h), [9, 11]);
  assert.deepStrictEqual(TT.parseSet('-12', h), [12, 12]);     // verlenging: 12 + 2 voorgift tegen 12
  assert.deepStrictEqual(TT.parseSet('10', h), [14, 10]);
  assert.deepStrictEqual(TT.parseSet('7'), [11, 7]);
  // 12-11 telt als set voor c (de laagst geklasseerde), 13-9 voor a
  assert.deepStrictEqual(TT.checkSets([[12, 11], [13, 9], [10, 11]], 3, h).score, [1, 2]);
  s.poules = [{ id: 'A', players: ['a', 'c', 'd'] }];
  TT.startPoules(s);
  const mm = s.matches.find(m => m.p1 === 'a' && m.p2 === 'c' || m.p1 === 'c' && m.p2 === 'a');
  assert.throws(() => TT.setResult(s, mm.id, { sets: [[11, 5], [11, 5]] }));
  TT.setResult(s, mm.id, { sets: mm.p1 === 'a' ? [[13, 5], [13, 5]] : [[5, 13], [5, 13]] });
  assert.strictEqual(mm.winner, 'a');
  s.settings.handicap = 'none';
  s.players = s.players.slice(0, 3);
  s.poules = [{ id: 'A', players: ['a', 'b', 'c'] }];
  TT.startPoules(s);
  TT.autoAssign(s);
  const m = s.matches.find(x => x.table);
  assert(m.ump && m.ump !== m.p1 && m.ump !== m.p2, 'vrije speler van de poule telt');
}
// --- eindrondes vroeg aanmaken geeft dezelfde tabel als wachten tot alle poules klaar zijn
for (const n of [8, 13, 17, 22, 29, 30]) {
  const mk = () => { const s = TT.newState(); s.settings.handicap = 'none'; for (let i = 0; i < n; i++) s.players.push({ id: 'p' + (i + 1), name: 'S' + (i + 1), rank: RANKS[i % RANKS.length] }); s.poules = TT.drawPoules(s.players, 4); TT.startPoules(s); return s; };
  const a = mk(), b = mk();
  TT.startKnockout(a);
  const first = s => s.matches.filter(m => m.kind !== 'poule' && m.gsize === m.B).map(m => m.kind + m.idx + ':' + m.p1 + '-' + m.p2).join(' ');
  assert(/\?A:1/.test(first(a)), 'plaatshouders verwacht');
  assert(!a.matches.some(m => m.kind !== 'poule' && TT.isPlayable(m)), 'nog niets speelbaar');
  const order = a.matches.filter(m => m.kind === 'poule').map(m => m.id);
  const res = {};
  order.forEach(id => { res[id] = randomSets(3); });
  // poule A eerst afwerken: dan kent de tabel al de spelers van poule A
  order.forEach(id => { TT.setResult(a, id, { sets: res[id] }); TT.setResult(b, id, { sets: res[id] }); });
  TT.startKnockout(b);
  assert.strictEqual(first(a), first(b), `vroege en late tabel verschillen (n=${n})`);
  const byes = s => s.matches.filter(m => m.kind !== 'poule' && m.bye).map(m => m.id + ':' + m.winner).join(' ');
  assert.strictEqual(byes(a), byes(b));
  // een poule-uitslag wissen maakt de plaatsen van die poule weer onbekend, opnieuw ingeven herstelt de tabel
  const pm = a.matches.find(m => m.kind === 'poule' && m.poule === 'B');
  TT.clearResult(a, pm.id);
  assert(/\?B:1/.test(first(a)) && !/\?A:1/.test(first(a)));
  TT.setResult(a, pm.id, { sets: res[pm.id] });
  assert.strictEqual(first(a), first(b));
  // na een gespeelde eindrondewedstrijd mag een poule-uitslag die de deelnemers verandert niet meer
  const km = a.matches.find(m => m.kind === 'main' && TT.isPlayable(m) && !m.bye);
  TT.setResult(a, km.id, { score: [Math.ceil(km.bo / 2), 0] });
  const pouleOfP1 = a.poules.find(p => p.players.includes(km.p1)).id;
  const snap = JSON.stringify(a);
  const victim = a.matches.find(m => m.kind === 'poule' && m.poule === pouleOfP1);
  assert.throws(() => TT.clearResult(a, victim.id), /al gespeelde eindrondewedstrijd/);
  const a2 = JSON.parse(snap);
  // dezelfde uitslag opnieuw ingeven verandert niets en mag wel
  TT.setResult(a2, victim.id, { sets: res[victim.id] });
  assert.strictEqual(first(a2), first(b));
}

// Loting bij gelijk klassement: alfabetisch, omgekeerd, willekeurig of lijstvolgorde
{
  const pl = [['p1', 'Zeger', 'C0'], ['p2', 'Bart', 'D0'], ['p3', 'Anna', 'C0'], ['p4', 'Mia', 'D0'], ['p5', 'Carl', 'B0'], ['p6', 'élise', 'D0']]
    .map(([id, name, rank]) => ({ id, name, rank }));
  const flat = tie => { const ps = TT.drawPoules(pl, 3, false, Math.random, tie); return ps[0].players.map((a, i) => [a, ps[1].players[i]]); };
  const seq = tie => { const ps = TT.drawPoules(pl, 6, false, Math.random, tie); return ps[0].players.join(' '); };
  assert.strictEqual(seq('list'), 'p5 p1 p3 p2 p4 p6');
  assert.strictEqual(seq(undefined), 'p5 p1 p3 p2 p4 p6');
  assert.strictEqual(seq('az'), 'p5 p3 p1 p2 p6 p4');
  assert.strictEqual(seq('za'), 'p5 p1 p3 p4 p6 p2');
  const seen = new Set();
  for (let i = 0; i < 60; i++) {
    const r = seq('random').split(' ');
    assert.strictEqual(r[0], 'p5');
    assert.deepStrictEqual(r.slice(1, 3).sort(), ['p1', 'p3']);
    assert.deepStrictEqual(r.slice(3).sort(), ['p2', 'p4', 'p6']);
    seen.add(r.join(' '));
  }
  assert.ok(seen.size > 3, 'willekeurig geeft verschillende volgordes');
  assert.strictEqual(TT.newState().settings.drawTie, 'az');
  assert.strictEqual(TT.migrate({ settings: { handicap: 'lead' }, matches: [] }).settings.drawTie, 'az');
  assert.strictEqual(flat('az').length, 3);
}

// Alfabetisch bij gelijk klassement = op familienaam; namen staan als "Familienaam Voornaam"
{
  assert.strictEqual(TT.sortName('De Moerloose Wim'), 'De Moerloose Wim');
  assert.strictEqual(TT.sortName('  pauwels   carl '), 'pauwels carl');
  assert.strictEqual(TT.sortName('De Vos, Wim'), 'De Vos Wim');
  assert.strictEqual(TT.sortName('Madonna'), 'Madonna');
  const pl = ['De Vos Wim', 'PAUWELS CARL', 'Props Filip', 'De Moerloose Wim', 'de vos, anna', 'Aerts Zoë'].map((name, i) => ({ id: 'p' + (i + 1), name, rank: 'D0' }));
  const seq = tie => TT.drawPoules(pl, 6, false, Math.random, tie)[0].players.join(' ');
  assert.strictEqual(seq('az'), 'p6 p4 p5 p1 p2 p3');   // Aerts, De Moerloose, de vos anna, De Vos Wim, Pauwels, Props
  assert.strictEqual(seq('za'), 'p3 p2 p1 p5 p4 p6');
}
console.log('Alle logicatests geslaagd.');
