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
| torsades | "tor-say-ds" | `tor-SAHDS` (cardiac verse 6) |
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

## Interference between songs (settled in the chat)

Eight songs on one melody means the melody cues eight destinations and the
strongest wins, worst where content overlaps (trastuzumab vs T-DXd,
checkpoints in both). So:
- Same meter every song (so verses stay shufflable), different TUNE and
  different GENRE per organ. Lungs = folk rock, cardiac = celtic punk stomp.
- Never the same drug or the same sentence shape in the same verse number
  across two songs. Checkpoints: lungs 5, cardiac 9. Trastuzumab: cardiac 2,
  T-DXd: lungs 6.
- Each song has its own vocabulary for recurring concepts ("the pressure
  starts to..." was in both and got rewritten out of cardiac).
- Learn them spaced out; do not build all eight in a week.


## Forced alignment (chosen 2026-09-17, measured on a piper-spoken verse)

Three aligners were run on the same 12 s spoken clip of cardiac verse 1
(`audio/test/`), because we KNOW the words: this is forced alignment of a
known text, not transcription.

| aligner | what it is | result on the clip |
|---|---|---|
| torchaudio MMS_FA (`tool/align_mms.py`) | character CTC, no dictionary, takes our lyric text | 44/44 words in order; correct text scores mean 0.93, wrong text mean 0.35 with 70 % of words below 0.5, so the score flags a bad match |
| WhisperX (`tool/align.py`) | transcribes, then wav2vec2-aligns its own transcript; we map heard words back onto ours | onsets within 20 ms median, 58 ms max of MMS_FA; heard 3/44 words differently (Two-fifty, in, decline) |
| Montreal Forced Aligner 3.3.8, cochlea's `mfa_cpu` env, english_us_arpa | dictionary + GMM, what cochlea used for the YouTube captions | 0 unknown words on this clip; onsets median 25 ms, max 137 ms from MMS_FA |

Decision: MMS_FA is the scene's timing source. It takes the lyric as
written, so respellings like "blee-oh-MY-sin" and abbreviations like
"E.F." align as spelled with no dictionary, and its per-word score tells us
where Suno sang something else. WhisperX stays as the "what did Suno
actually sing" detector for the mispronunciation table above. MFA needs
every word in its dictionary (or a G2P model, which is not installed) and
is the one most likely to fail on sung drug names; kept only as a check.
Still unmeasured: all three on a real Suno vocal stem. Re-run the same
comparison the day the first stem lands (`align/test_aligner_comparison.md`).

Manim timing: the scene reads the renderer's clock before every word;
residual error is at most one frame (measured 66 ms at 15 fps preview,
1080p60 renders at 17 ms).

## Exclude Styles A/B (Pro plan, v6, 2026-09-17)

Pro Custom mode has an Exclude field under Advanced Options. First list
tried: instrumental intro/outro, guitar/fiddle/banjo solo, instrumental
break, sustained notes, vocal runs. Grey's report: wordless backing vocals
survived ("oooh-aaah" call-and-response harmonies, not the lyric). Extended
the list with oohs and aahs, wordless vocals, vocalise, vocal pads, ad-libs,
chanting. Next single change if they survive: style line "tight gang-vocal
harmonies" -> "gang vocals singing the lyric in unison". Intro/solo counts
with vs without the field: not yet reported.

Result of the extended exclude list (Grey, same day): lungs better, cardiac
still more filler than wanted, and on BOTH the gang vocals blur the drug
names. Diction is the point, so the next single change is the style line:
"tight gang-vocal harmonies" / "full gang-vocal chorus" replaced with
"single clear-diction male lead vocal, dry close-mic vocal with no backing
vocals" in both songs. Exclude list unchanged. If cardiac filler remains
after that, next single change: 140 -> 130 BPM.

Lungs single-lead render (Grey): diction clearer but beat, rhythm and
enunciation of the gang-vocal version were better overall. Lungs style
REVERTED to the gang-vocal line; the occasional overlapping voices are
accepted. Cardiac keeps the single-lead line until its render is judged.

## First real Suno renders aligned (2026-09-17, Pro, v6, full mixes downloaded as WAV)

Demucs htdemucs vocal stems, separated locally (no Suno credits). Stem vs
full-mix MMS_FA onsets: lungs median 0 ms, max 60 ms over 302 words;
cardiac median 0 ms over 386 words except the final line, where the mix
alignment smears into the outro. So the full mix aligns fine; the stem is
kept for the tail and for WhisperX. Suno's own "Extract Stems" is not
needed for alignment.

MMS_FA scores on sung audio are lower than on speech (lungs stem mean
0.67, cardiac stem 0.48, spoken test 0.93) but every word is placed in
order and frame checks on lungs verse 1 land the circle, underline and
notes on the sung word.

WhisperX on the lungs stem, what it heard vs what we wrote (its transcript
dropped the whole gemcitabine verse, which is why it is not the timing
source):
- tem-sir-OH-li-mus -> "Tanserolimus"; em-TOR -> "toward"
- Trastuzumab deruxtecan -> "Trastazumab Diroxacan"
- "five" (after ah-tez-oh, durva) and "HER2" not heard at all
- ev-er-OH-li-mus, BYOO-sul-fan heard correctly
Grey's own ear is the judge on these; the list says where to listen.

Cardiac stem, WhisperX: the final line IS sung, at 2:31-2:34, as "The heart
block gets done" (the "it" dropped). The zero MMS_FA scores on that line
were the aligner losing confidence at the tail, not a missing line; do not
read a zero-score run as "not sung" without the transcript. Heard
differently, worth Grey's ear:
- ipi-nivo -> "epinephrine" (a clinically confusable mishearing; respell
  or reword: "ipi with nivo")
- Bevacizumab -> "Babasazumab"; dasatinib -> "tacitinib"; Ponatinib ->
  "Potatinib"; lenvatinib -> "lenbatinib"; Capecitabine -> "Capacitabine"
- "Ibrutinib" and "M.I." not heard; lytes -> "lights"; lung -> "long"
- tor-SAHDS heard as "torsades": the respelling works
- E.F. heard as "F" three times: the letters may be running together
Which cardiac style this WAV came from (gang vocal or single lead) is not
recorded; Grey to say.

## Recall log (retrieval practice, lungs)

| date | trial | prior exposure | drugs recalled | missed |
|---|---|---|---|---|
| 2026-09-17 | 1 | 10+ passive listens | gemcitabine, methotrexate, busulfan, "something duroxican" (4/7) | bleomycin (v1), everolimus/temsirolimus (v2), the five checkpoints (v5) |

Inference, one trial only: the two multi-drug verses were both missed.
