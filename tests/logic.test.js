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

function randomSets(bo) {
  const need = Math.ceil(bo / 2), sets = []; let a = 0, b = 0;
  while (a < need && b < need) {
    const lose = Math.floor(rnd() * 13), win = lose <= 9 ? 11 : lose + 2;
    if (rnd() < 0.5) { sets.push([win, lose]); a++; } else { sets.push([lose, win]); b++; }
  }
  return sets;
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
    TT.setResult(s, m.id, { sets: randomSets(m.bo) });
    if (check) check(m);
    assert(guard++ < 5000);
  }
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
  s.poules.forEach(p => {
    const ms = s.matches.filter(m => m.poule === p.id), c = p.players.length;
    assert.strictEqual(ms.length, c * (c - 1) / 2);
    assert.strictEqual(new Set(ms.map(m => [m.p1, m.p2].sort().join())).size, ms.length);
  });
  playAll(s);
  assert(TT.allPoulesDone(s));
  s.poules.forEach(p => { const st = TT.pouleStandings(s, p.id); assert(st.complete); assert.strictEqual(new Set(st.rows.map(r => r.id)).size, p.players.length); });
  assert.throws(() => TT.setResult(s, s.matches[0].id, { score: [2, 0] }) || TT.startKnockout(s) || TT.setResult(s, s.matches[0].id, { score: [2, 0] }));
  if (s.stage !== 'knockout') TT.startKnockout(s);
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
// --- voorgift (VTTL heren) en scheidsrechter
{
  const s = TT.newState();
  s.settings.handicap = 'vttl';
  [['a', 'B0'], ['b', 'B2'], ['c', 'C0'], ['d', 'NG'], ['e', 'A'], ['f', '']].forEach(([id, rank]) => s.players.push({ id, name: id, rank }));
  const h = (p1, p2) => TT.handicap(s, { p1, p2 });
  assert.deepStrictEqual(h('a', 'b'), { to: 'b', n: 1 });
  assert.deepStrictEqual(h('c', 'a'), { to: 'c', n: 2 });
  assert.deepStrictEqual(h('a', 'd'), { to: 'd', n: 8 });
  assert.deepStrictEqual(h('e', 'd'), { to: 'd', n: 9 });
  assert.deepStrictEqual(h('e', 'f'), { to: 'f', n: 9 });
  assert.strictEqual(h('d', 'f'), null);
  s.settings.handicap = 'none';
  assert.strictEqual(h('a', 'd'), null);
  s.players = s.players.slice(0, 3);
  s.poules = [{ id: 'A', players: ['a', 'b', 'c'] }];
  TT.startPoules(s);
  TT.autoAssign(s);
  const m = s.matches.find(x => x.table);
  assert(m.ump && m.ump !== m.p1 && m.ump !== m.p2, 'vrije speler van de poule telt');
}
console.log('Alle logicatests geslaagd.');
