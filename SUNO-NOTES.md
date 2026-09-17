# Suno pronunciation notes

What Suno actually did with the Lungs lyrics, and what fixed it. Add to this
after every render.

| written | Suno sang | fix that was tried |
|---|---|---|
| bleomycin | mispronounced | `Blee-oh-MY-sin`; if it still breaks, spaces: `BLEE oh MY sin` |
| FiO2 | "Feye-O2" | avoid the abbreviation, or `F.I.O. two` / `eff-eye-oh-two` |
| ILD | "illed" | keep ILD (it is the payload, not filler): `I.L.D.`, fallback `eye-el-dee` |
| gemcitabine | gem-sit-a-bine | `Gem-SITE-uh-been` (blocks the short-i "citrus" reading) |
| atezolizumab / atezo | slurred | `ah-tez-oh`; regenerate two or three times before calling the line too dense |
| HER2 | unverified, may be "her two" / "hertz" | `H.E.R. two`, or reword |
| DLCO, PFTs, RT | untested | `D.L.C.O.` / `dee-el-see-oh`, "lung function tests", `R.T.` or "radiation" |

Rules learned:
- Every abbreviation is read as a word unless letters are separated. Periods
  with spaces work better than hyphens.
- Capitalised syllables (`SITE`, `MY`) steer the vowel.
- One slurred word in a five-name line is as likely take-to-take variance as a
  real meter problem. Regenerate before rewriting.
- Dropping a syllable to give spelled letters room is a legitimate lever.

## Locked format for the chemo/immunotherapy set (settled in the chat, 2026-09)

Style prompt (positive-only; Suno strips negations entirely rather than
inverting them, tested by Grey with and without "Do not ..." lines, same output):

    folk rock, clear-diction male lead with tight gang-vocal harmonies,
    strummed acoustic guitar and upright bass, driving 130 BPM four-on-the-floor
    kick, one syllable per note, vocals every bar, consistent full-band energy

Suno normalises the prompt into its own description; artist-adjacent words
("British", "revival") get sanded off, mechanical descriptors survive. It adds
"subtle plate reverb" on its own. Exclude Styles is not a separate field in
the mode Grey uses and is not applied.

Meter: common meter 8-6-8-6, rhyme on every 6-syllable line, every 8-syllable
line strictly iambic and ending on a stressed syllable.

Titles: `Drug-Induced [Organ] Toxicity`, numbered if they should sort.

Respellings that worked: blee-oh-MY-sin, gem-SITE-uh-bean, BYOO-sul-fan,
em-TOR, ah-tez-oh; periods for abbreviations (I.L.D., R.T., P.F.T.).

Interlude control: end the lyrics with `[End]` on its own line; fill the
runtime (seven dense verses in ~2 min leaves no room for solos); crop the
intro with Suno's trim tool rather than regenerating.

For cardiac Grey wants the flavour nearer Mumford & Sons, Clumsy Lovers, sea
shanties, Flogging Molly. Artist names do not survive normalisation, so
translate to mechanical descriptors (banjo-forward, stomp-and-clap, call-and-
response gang vocals, accordion/fiddle, 6/8 or driving 4/4).
