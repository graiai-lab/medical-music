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
