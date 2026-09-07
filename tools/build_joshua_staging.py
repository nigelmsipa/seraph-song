#!/usr/bin/env python3
"""Build the word-for-word KJV staging package for Seraph Song: Joshua."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source-texts" / "KJV.txt"
OUTPUT = ROOT / "joshua"
ABSOLUTE_LIMIT = 5000


# Each boundary follows a complete narrative, speech, list, or liturgical movement.
# Styles share a stable acoustic/choral vocabulary while allowing the book's four
# movements—entry, conquest, allotment, and covenant—to acquire distinct colors.
PLAN = [
    {
        "reference": "1:1-18",
        "name": "The Commission: Be Strong and of a Good Courage",
        "style_name": "THRESHOLD HYMN",
        "style": "sacred folk-orchestral, countertenor lead, clear KJV diction, fingerpicked classical guitar, warm cello, measured frame drum, restrained chapel choir, modal harmony, 76 BPM, steady forward motion, gradual rise on the courage refrain, spacious reverent mix, no vocal overlap",
        "why": "Joshua's divine commission and the people's answering pledge form one succession ceremony. The sound begins with Moses' absence, gathers strength through the threefold courage command, and resolves when Israel echoes that command back to Joshua.",
    },
    {
        "reference": "2:1-24",
        "name": "Rahab and the Scarlet Cord",
        "style_name": "NIGHT WATCH FOLK",
        "style": "nocturnal lo-fi folk, female alto narration, clear KJV diction, fingerpicked acoustic guitar, brushed cajon, bowed double bass, faint harmonica, restrained chapel choir, minor-to-major modal turn, 74 BPM, intimate tense verses, hopeful lift at Rahab's confession, warm tape texture, no vocal overlap",
        "why": "The complete spy episode is a single suspense arc: danger, concealment, confession, oath, escape, and faithful report. An intimate night sound honors Rahab's courage without turning espionage into spectacle.",
    },
    {
        "reference": "3:1-17",
        "name": "The Jordan Stands in a Heap",
        "style_name": "RIVER PROCESSIONAL",
        "style": "ritual sacred folk ambient, clear KJV diction, low male lead, handpan, concert harp, low cello drone, slow frame drum procession, distant mixed choir, 72 BPM, spacious river atmosphere, restrained beginning, luminous choral expansion when the waters part, solemn and unhurried, no vocal overlap",
        "why": "Preparation, divine promise, and the crossing itself rise continuously toward Israel standing on dry ground. The procession supplies motion while the choir marks the miracle rather than dominating every verse.",
    },
    {
        "reference": "4:1-24",
        "name": "Twelve Stones for the Children",
        "style_name": "MEMORIAL FOLK",
        "style": "warm sacred folk, clear KJV diction, acoustic guitar, gentle harmonica responses, hand drum pulse, warm cello, mixed chapel choir used as a soft refrain, 74 BPM, storytelling cadence, calm anticipatory phrasing, widening harmony at 'What mean ye by these stones?', natural intimate production, no vocal overlap",
        "why": "The stones from the river, the completed crossing, and the explanation to future children belong together as one act of remembrance. The folk setting makes the chapter sound handed down rather than merely announced.",
    },
    {
        "reference": "5:1-15",
        "name": "Gilgal, Passover, and the Captain of the Host",
        "style_name": "HOLY GROUND",
        "style": "ethereal choral sacred ambient, clear KJV diction, countertenor lead, concert harp, low strings, soft pads, distant soprano layers, minimal percussion, modal and ancient-sounding, 68 BPM, deep hush, gradual movement from consecration to Passover to holy-ground awe, cathedral space, no vocal overlap",
        "why": "Circumcision, Passover, the end of manna, and the Captain of the LORD's host collectively consecrate Israel before battle. The chapter should feel like preparation on holy ground, not a pre-battle anthem.",
    },
    {
        "reference": "6:1-27",
        "name": "The Fall of Jericho",
        "style_name": "SEVENFOLD PROCESSION",
        "style": "ritual cinematic folk, clear KJV diction, low male chant, measured frame drums, ram's-horn calls, plucked strings, boy choir accents, low brass used sparingly, 78 BPM, disciplined repetitive procession, dramatic use of near-silence, one controlled orchestral-choral release at the shout, grave aftermath, no vocal overlap",
        "why": "The plan, sevenfold marching, shout, judgment, Rahab's rescue, and Jericho's curse form one indivisible event. Repetition carries the ritual; silence and a single release keep the miracle from becoming generic battle music.",
    },
    {
        "reference": "7:1-15",
        "name": "The Hidden Sin and the Defeat at Ai",
        "style_name": "DARK SACRED TRIP-HOP",
        "style": "dark sacred trip-hop, clear KJV diction, low piano, bowed bass, sparse sub pulse, restrained dry drums, low male choir, occasional female lament, 68 BPM, descending minor harmony, tense negative space, no swagger, no triumph, unresolved ending after the guilty person is named but not yet found, no vocal overlap",
        "why": "Achan's concealed trespass, the defeat at Ai, Joshua's lament, and God's explanation form the first movement: Israel knows the cause and the coming procedure, but the guilty person remains hidden. The unresolved dark palette holds that tension without sensationalizing the judgment.",
    },
    {
        "reference": "7:16-26",
        "name": "Achan Taken in the Valley of Achor",
        "style_name": "ACHOR JUDGMENT LAMENT",
        "style": "sparse sacred lament, clear KJV diction, grave male baritone, low cello, dark concert harp, distant wordless choir, minimal frame drum, 64 BPM, inexorable narrowing cadence through the lots, bare confession, mournful judicial climax, long somber decay at the great heap of stones, no vocal overlap",
        "why": "The lot narrows from tribe to household to man; confession, recovery of the devoted things, and judgment then complete the episode. A slower lament distinguishes exposure from the preceding defeat and gives the Valley of Achor its full moral weight.",
    },
    {
        "reference": "8:1-13",
        "name": "The Ambush Set Behind Ai",
        "style_name": "FOLK-HOP STRATEGY",
        "style": "cinematic folk-hop, clear KJV diction, rhythmic male narration, fingerpicked guitar ostinato, bowed cello, frame drum and brushed snare, restrained low choir, 78 BPM, quiet tactical tension, layered entrances, dry forward pulse, spacious midrange, no vocal overlap",
        "why": "God's renewed command and Joshua's positioning of the ambush make one deliberate preparation movement. The pulse communicates strategy and restored resolve without prematurely celebrating the victory.",
    },
    {
        "reference": "8:14-29",
        "name": "Ai Drawn Out and Taken",
        "style_name": "CONTROLLED BATTLE TRIP-HOP",
        "style": "cinematic orchestral trip-hop, clear KJV diction, steady low drum pulse, cello ostinato, dark strings, restrained low brass, male lead with brief choral accents, 80 BPM, controlled escalation, sharp pivot when Joshua stretches out the spear, grave rather than triumphant, clean vocal space, no vocal overlap",
        "why": "Ai's pursuit, the signal, the burning city, and the king's death comprise the complete battle action. The style intensifies the preceding tactical groove while retaining the moral gravity of the text.",
    },
    {
        "reference": "8:30-35",
        "name": "The Law Read on Mount Ebal",
        "style_name": "COVENANT HYMN",
        "style": "sacred hymn, clear KJV diction, countertenor lead, concert harp, warm cello, oboe, gentle strings, balanced mixed choir, 70 BPM, simple resolving harmony, unhurried public-reading cadence, luminous but restrained climax, wide reverent space, no vocal overlap",
        "why": "The altar, written law, blessings and cursings, and complete public reading are a distinct liturgical answer to the battle. Its brevity is a virtue: the song becomes a clean covenantal seal.",
    },
    {
        "reference": "9:1-27",
        "name": "The Gibeonite Ruse and the Unbroken Oath",
        "style_name": "UNEASY LO-FI FOLK",
        "style": "understated lo-fi folk, clear KJV diction, alternating male voices, plucked acoustic guitar, brushed percussion, bowed bass, muted harmonica, 74 BPM, gently deceptive groove, subtle harmonic unease at 'asked not counsel', sober resolution rather than comedy, small choir only at the oath, warm dry mix, no vocal overlap",
        "why": "The disguise, negotiation without counsel, discovery, and resolution all depend on one oath. A single understated groove lets the listener feel both the cleverness of the ruse and the seriousness of Israel's sworn word.",
    },
    {
        "reference": "10:1-15",
        "name": "The Sun Stands Still over Gibeon",
        "style_name": "COSMIC BATTLE ORATORIO",
        "style": "cinematic sacred orchestral, clear KJV diction, urgent male lead, driving frame drums, low brass, tremolo strings, full choir held in reserve, 82 BPM, decisive march, vast suspended harmony and thinned percussion when the sun stands still, then one majestic choral return, high dynamic range, no vocal overlap",
        "why": "Gibeon's appeal, Israel's night march, hailstones, Joshua's command to sun and moon, and the unmatched day form the book's cosmic military climax. The arrangement must make time itself seem suspended.",
    },
    {
        "reference": "10:16-27",
        "name": "The Five Kings Brought from the Cave",
        "style_name": "CAVE JUDGMENT",
        "style": "dark ritual folk-hop, clear KJV diction, low male vocal, cavernous hand drum, bowed bass, sparse cello, muted brass, grave unison chant, 76 BPM, claustrophobic verses, stern controlled build, no celebratory swagger, abrupt weight at the execution, long dark decay, no vocal overlap",
        "why": "The kings' concealment, capture, public humiliation, execution, and sealing in the cave form a severe judicial episode. The sound stays enclosed and heavy rather than heroic.",
    },
    {
        "reference": "10:28-43",
        "name": "The Southern Campaign",
        "style_name": "GRAVE CINEMATIC FOLK-HOP",
        "style": "grave cinematic folk-hop, clear KJV diction, rhythmic narration, acoustic guitar ostinato, hand drums, low cello, restrained brass, sparse male choir, 80 BPM, repeating campaign motif with small variations for each city, compressed forward motion, sober final resolution at Gilgal, no vocal overlap",
        "why": "The repeated victories from Makkedah through Debir are one campaign catalogue ending with the whole southern country subdued. A recurring motif makes the repetition intelligible while the restrained tone avoids triumphal excess.",
    },
    {
        "reference": "11:1-23",
        "name": "The Northern Coalition and the Rest of the Land",
        "style_name": "NORTHERN MODAL CHOIR",
        "style": "dark modal orchestral folk, clear KJV diction, haunting unison male voices expanding into restrained close-harmony choir, bowed strings, low drone, subtle frame drum, 76 BPM, cold spacious atmosphere, controlled battle surge, gradual release into stillness at 'the land rested from war', no vocal overlap",
        "why": "The vast northern coalition, Hazor's fall, summary of conquest, hardening of the kings, removal of the Anakim, and final rest form one concluding arc. The arrangement should cool and empty as warfare gives way to rest.",
    },
    {
        "reference": "12:1-24",
        "name": "The Roll of the Defeated Kings",
        "style_name": "KING-COUNT LITANY",
        "style": "hypnotic sacred percussion, clear KJV diction, countertenor recitation, dry frame drum and shaker, plucked harp, low cello drone, restrained unison responses, 78 BPM, steady walking tempo, subtle variation through the names, count-like cadence, spacious mix, firm final resolution at thirty and one, no vocal overlap",
        "why": "The eastern and western kings constitute the formal roll call closing the conquest. A litany turns the list into cumulative memory rather than filler, with the final count supplying the natural cadence.",
    },
    {
        "reference": "13:1-14",
        "name": "Much Land Remains and the Land beyond Jordan",
        "style_name": "UNFINISHED PROMISE AMBIENT",
        "style": "sacred ambient folk, clear KJV diction, mature male baritone, classical guitar harmonics, low cello, soft pads, distant choir, minimal hand drum, 68 BPM, spacious unfinished cadence, sober age and undiminished promise, gentle lift as the land is assigned, no vocal overlap",
        "why": "God's address to the aged Joshua names the unconquered land and commands its distribution; the narration then identifies the inheritance already given beyond Jordan and closes with Levi's distinct portion. This hinge moves completely from warfare into inheritance without ending mid-sentence.",
    },
    {
        "reference": "13:15-33",
        "name": "The Inheritances of Reuben, Gad, and Half-Manasseh",
        "style_name": "ALLOTMENT PULSE",
        "style": "meditative sacred folk pulse, clear KJV diction, classical guitar arpeggios, handpan, soft frame drum, warm cello, countertenor narration, 72 BPM, measured geographic phrasing, subtle recurring inheritance motif, sober remembrance of Balaam, open uncluttered mix, no vocal overlap",
        "why": "The specific tribal grants to Reuben, Gad, and half-Manasseh form the detailed eastern allotment inherited under Moses. A stable pulse carries the geography without flattening the tribal distinctions.",
    },
    {
        "reference": "14:1-15",
        "name": "Caleb: Give Me This Mountain",
        "style_name": "WEATHERED FOLK GOSPEL",
        "style": "weathered acoustic folk gospel, clear KJV diction, mature male baritone, fingerpicked guitar, fiddle, gentle harmonica, upright bass, restrained chapel choir, 76 BPM, warm major-modal harmony, patient storytelling, strong lift at 'give me this mountain', humble resolving cadence, natural production, no vocal overlap",
        "why": "The formal division of Canaan leads directly to Caleb's forty-five-year testimony and request for Hebron. Folk gospel gives the old warrior warmth, endurance, and conviction without turning him into a caricature.",
    },
    {
        "reference": "15:1-12",
        "name": "The Borders of Judah",
        "style_name": "BOUNDARY MEDITATION",
        "style": "intricate sacred rhythm, clear KJV diction, countertenor lead, classical guitar, concert harp, handpan, light frame drum, 74 BPM, precise flowing enumeration, gently circling motif, balanced acoustic texture, meditative geographic movement, no vocal overlap",
        "why": "Judah's four borders form a single carefully traced circuit. The arrangement circles with the text and closes naturally when the boundary returns to the Great Sea.",
    },
    {
        "reference": "15:13-19",
        "name": "Caleb, Othniel, and the Springs of Water",
        "style_name": "SPRINGS FOLK BALLAD",
        "style": "intimate acoustic folk ballad, clear KJV diction, alternating male and female leads, fingerpicked guitar, fiddle, warm cello, light hand percussion, 74 BPM, narrative simplicity, gentle melodic rise for Achsah's request, bright resolving figure at the upper and nether springs, natural room sound, no vocal overlap",
        "why": "Caleb's conquest, Othniel's reward, and Achsah's request make a compact family narrative inside the allotment lists. Alternating voices clarify the dialogue and the springs provide the musical release.",
    },
    {
        "reference": "15:20-63",
        "name": "The Cities of Judah",
        "style_name": "JUDAH CITY LITANY",
        "style": "minimalist folk-hop litany, clear KJV diction, rhythmic low male recitation, muted plucked strings, dry frame drum, bowed bass, faint wordless choir, 78 BPM, steady mnemonic groove, small instrumental variations between regions, restrained ending on Jerusalem and the Jebusites, spacious vocal midrange, no vocal overlap",
        "why": "The regional city lists are one territorial catalogue, ending with the unresolved Jebusite presence in Jerusalem. A mnemonic groove carries the names while regional shifts provide subtle internal chapters.",
    },
    {
        "reference": "16:1-10",
        "name": "The Inheritance of Ephraim",
        "style_name": "NEOCLASSICAL ALLOTMENT",
        "style": "neoclassical acoustic meditation, clear KJV diction, classical guitar lead, delicate harp, soft cello, restrained brushed beat, countertenor vocal, 72 BPM, clean melodic lines, measured border recitation, minor shading at the Canaanites remaining in Gezer, intimate high-fidelity mix, no vocal overlap",
        "why": "Joseph's boundary and Ephraim's specific inheritance form one concise allotment ending with incomplete dispossession. The clean guitar line gives the geography shape and leaves room for the darker final qualification.",
    },
    {
        "reference": "17:1-18",
        "name": "Manasseh, Zelophehad's Daughters, and the Forest",
        "style_name": "DIALOGUE LO-FI FOLK",
        "style": "lo-fi sacred folk, clear KJV diction, alternating male narration and small female ensemble, fingerpicked guitar, bowed double bass, soft hand drum, warm cello, restrained choir, 74 BPM, conversational pacing, tender clarity for Zelophehad's daughters, firmer rhythmic lift at 'cut it down', warm tape texture, no vocal overlap",
        "why": "Manasseh's inheritance, the daughters' lawful claim, remaining Canaanites, and Joseph's request for more land all concern possession within one tribal house. Distinct voices make the legal and argumentative turns legible.",
    },
    {
        "reference": "18:1-10",
        "name": "Shiloh and the Survey of the Land",
        "style_name": "SHILOH AMBIENT FOLK",
        "style": "sacred ambient folk, clear KJV diction, low male lead, concert harp, handpan, soft pads, gentle frame drum, distant mixed choir, 70 BPM, tent-of-meeting stillness, patient survey rhythm, luminous transition when the descriptions are laid before the LORD and the lot is cast, spacious reverent mix, no vocal overlap",
        "why": "The tabernacle is set at Shiloh, Joshua rebukes the seven tribes' delay, the surveyors traverse the land, and the lots are cast before the LORD. This is a complete administrative-sacred movement centered on ordered worship.",
    },
    {
        "reference": "18:11-28",
        "name": "The Lot and Cities of Benjamin",
        "style_name": "BENJAMIN BOUNDARY MEDITATION",
        "style": "intricate sacred acoustic rhythm, clear KJV diction, countertenor lead, classical guitar, delicate harp, handpan, light frame drum, warm cello, 74 BPM, precise border recitation, gently circling melodic figure, subtle cadence change for the cities, clean spacious mix, no vocal overlap",
        "why": "Benjamin's northern, western, southern, and eastern boundaries lead directly into its city list. The self-contained allotment receives a more rhythmic variation of the Shiloh palette.",
    },
    {
        "reference": "19:1-31",
        "name": "Simeon, Zebulun, Issachar, and Asher",
        "style_name": "PLUCKED WORLD LITANY",
        "style": "acoustic world-sacred litany, clear KJV diction, countertenor recitation, kora-like plucked texture, classical guitar, frame drum and shaker, warm bass drone, restrained chapel responses, 76 BPM, flowing place-name cadence, subtle motif change at each tribe, organic dry mix, no vocal overlap",
        "why": "The next four tribal lots form the first half of the remaining allotments. A lightly global plucked texture broadens the palette while remaining acoustic, reverent, and rhythmically useful for long names.",
    },
    {
        "reference": "19:32-51",
        "name": "Naphtali, Dan, and Joshua's Inheritance",
        "style_name": "ALLOTMENT RESOLUTION",
        "style": "warm neoclassical folk, clear KJV diction, classical guitar, handpan, soft cello, measured frame drum, male lead with restrained mixed choir, 72 BPM, patient geographic pulse, brighter motion when Dan takes Leshem, gentle resolving expansion when Joshua receives Timnathserah, no vocal overlap",
        "why": "The final tribal lots culminate in Joshua receiving his own city and the completion formula at Shiloh. The established allotment palette now resolves rather than merely continuing.",
    },
    {
        "reference": "20:1-9",
        "name": "The Cities of Refuge",
        "style_name": "REFUGE HYMN",
        "style": "gentle sacred hymn, clear KJV diction, countertenor lead, concert harp, warm cello, soft organ pad, light walking pulse, compassionate mixed choir, 70 BPM, stable sheltering harmony, calm legal narration, subtle lift as the six cities are named, spacious and consoling, no vocal overlap",
        "why": "The command, legal purpose, and naming of all six cities form one complete institution of refuge. Stable harmony makes the song itself feel like shelter while preserving the law's precision.",
    },
    {
        "reference": "21:1-26",
        "name": "The Cities of the Priests and Kohathites",
        "style_name": "PRIESTLY CITY LITANY",
        "style": "dignified priestly minimalism, clear KJV diction, countertenor recitation, concert harp, precise plucked strings, dry frame drum, low sustained cello, 72 BPM, orderly repeated cadence, clean tones, subtle clan-response motif, elevated but restrained, no vocal overlap",
        "why": "The Levites' request, casting of lots, and the complete priestly and Kohathite allotments make the first natural clan division. Precision and repeated cadence serve the city names.",
    },
    {
        "reference": "21:27-45",
        "name": "The Levitical Cities and the Promise Fulfilled",
        "style_name": "FULFILMENT LITANY",
        "style": "sacred harp procession, clear KJV diction, countertenor lead, concert harp, cello, oboe, measured frame drum, mixed choir gradually entering, 74 BPM, orderly city litany opening into broad resolving harmony, full but uncluttered climax at 'there failed not ought', cathedral space, no vocal overlap",
        "why": "The Gershonite and Merarite cities complete the Levitical list, which then opens into the book's great fulfillment declaration. The same priestly language expands naturally into choir at the theological conclusion.",
    },
    {
        "reference": "22:1-9",
        "name": "The Eastern Tribes Sent Home",
        "style_name": "HOMECOMING FOLK HYMN",
        "style": "warm acoustic folk hymn, clear KJV diction, mature male lead, fingerpicked guitar, fiddle, gentle harmonica, upright bass, restrained chapel choir, 74 BPM, grateful homeward motion, affectionate blessing, natural unpolished warmth, dignified rather than sentimental, no vocal overlap",
        "why": "Joshua's commendation, blessing, and the tribes' wealthy return to Gilead form a complete homecoming movement. Its warmth makes the sudden altar crisis that follows genuinely disruptive.",
    },
    {
        "reference": "22:10-20",
        "name": "The Altar and the Charge of Rebellion",
        "style_name": "TENSE COVENANT TRIP-HOP",
        "style": "tense sacred trip-hop, clear KJV diction, spoken-sung male delegation, low piano, bowed bass, dry frame drums, restrained low choir, 72 BPM, gathering pressure, grave pauses around Peor and Achan, dark but controlled mix, accusation without rage, open vocal midrange, no vocal overlap",
        "why": "The altar's discovery, Israel's preparation for war, and Phinehas's full accusation are one mounting case against apparent apostasy. Controlled tension keeps the moral stakes high without prejudging the answer.",
    },
    {
        "reference": "22:21-34",
        "name": "The Altar Called Ed: A Witness",
        "style_name": "RECONCILIATION CALL-AND-RESPONSE",
        "style": "acoustic sacred folk call-and-response, clear KJV diction, alternating male ensembles, fingerpicked guitar, warm cello, hand drum, restrained mixed choir, 74 BPM, earnest defense, gradual harmonic release as peace returns, bright but sober cadence on 'a witness between us', natural room sound, no vocal overlap",
        "why": "The eastern tribes' complete defense and the western tribes' acceptance form the answer to the preceding charge. Alternating ensembles clarify the dialogue and the harmony resolves only when communion is restored.",
    },
    {
        "reference": "23:1-16",
        "name": "Joshua's Final Charge to the Leaders",
        "style_name": "ELDER'S DEVOTIONAL FOLK",
        "style": "sparse devotional folk, clear KJV diction, weathered male baritone, fingerpicked acoustic guitar, warm cello, bowed bass, very light hand drum, distant chapel choir, 68 BPM, intimate elder's cadence, firm lift at 'be ye therefore very courageous', darkening harmony through the final warning, no vocal overlap",
        "why": "Joshua's retrospective, exhortation, promise, and warning are one continuous farewell address. A weathered voice and restrained arrangement allow the authority to come from the words rather than cinematic force.",
    },
    {
        "reference": "24:1-13",
        "name": "From Beyond the Flood to the Promised Land",
        "style_name": "COVENANT HISTORY PROCESSIONAL",
        "style": "cinematic sacred folk processional, clear KJV diction, male narrator, acoustic guitar, subtle mbira-like plucked pattern, hand drum, low cello, restrained choir, 74 BPM, cumulative historical motion, recurring grace motif under each divine act, widening orchestration at the gift of the land, no vocal overlap",
        "why": "The divine first-person history from Abraham through Egypt, wilderness, conquest, and gift of the land is a complete covenant recital. A recurring processional motif makes the many acts sound like one providential movement.",
    },
    {
        "reference": "24:14-33",
        "name": "Choose This Day and the End of an Era",
        "style_name": "COVENANT RESPONSE AND CODA",
        "style": "acoustic sacred folk with restrained Black gospel call-and-response, clear KJV diction, male lead, piano, fingerpicked guitar, warm organ, hand drum, mixed choir, 74 BPM, disciplined congregational responses, strong but uncluttered rise at 'choose you this day', covenant-sealing cadence at the witness stone, then a sparse funeral coda with solo cello and distant choir, no vocal overlap",
        "why": "Joshua's choice, the people's repeated answer, covenant sealing, dismissal, and the three burials close both the assembly and the conquest generation. The communal response earns a gospel color; the arrangement then relinquishes it for a quiet funeral coda.",
    },
]


VERSE_RE = re.compile(r"^Joshua (\d+):(\d+)\t(.*)$")


def parse_reference(reference: str) -> tuple[tuple[int, int], tuple[int, int]]:
    start_text, end_text = reference.split("-", 1)
    start_chapter, start_verse = (int(part) for part in start_text.split(":"))
    if ":" in end_text:
        end_chapter, end_verse = (int(part) for part in end_text.split(":"))
    else:
        end_chapter, end_verse = start_chapter, int(end_text)
    return (start_chapter, start_verse), (end_chapter, end_verse)


def load_joshua() -> dict[tuple[int, int], str]:
    verses: dict[tuple[int, int], str] = {}
    for line in SOURCE.read_text(encoding="utf-8").splitlines():
        match = VERSE_RE.match(line)
        if match:
            verses[(int(match.group(1)), int(match.group(2)))] = match.group(3)
    if not verses:
        raise RuntimeError("No Joshua verses found in source-texts/KJV.txt")
    return verses


def verse_keys(
    verses: dict[tuple[int, int], str], reference: str
) -> list[tuple[int, int]]:
    start, end = parse_reference(reference)
    return [key for key in sorted(verses) if start <= key <= end]


def song_title(chunk_num: int, reference: str) -> str:
    start, end = parse_reference(reference)
    if start[0] == end[0]:
        span = f"CHAPTER {start[0]} VERSES {start[1]}-{end[1]}"
    else:
        span = f"CHAPTER {start[0]}:{start[1]} TO {end[0]}:{end[1]}"
    return f"SUNO CHUNK {chunk_num} | JOSHUA {span}"


def build() -> None:
    verses = load_joshua()
    staged = []
    covered: list[tuple[int, int]] = []

    for chunk_num, item in enumerate(PLAN, start=1):
        keys = verse_keys(verses, item["reference"])
        if not keys:
            raise ValueError(f"No verses resolved for {item['reference']}")
        covered.extend(keys)
        # Preserve one verse per line. Only spaces become underscores, matching
        # the established Deuteronomy workaround without changing the KJV words.
        lyrics = "\n".join(verses[key].replace(" ", "_") for key in keys)
        if len(lyrics) >= ABSOLUTE_LIMIT:
            raise ValueError(
                f"Chunk {chunk_num} is {len(lyrics)} characters; "
                f"absolute limit is below {ABSOLUTE_LIMIT}."
            )
        staged.append(
            {
                "chunk_num": chunk_num,
                "title": song_title(chunk_num, item["reference"]),
                "reference": item["reference"],
                "chunk_name": item["name"],
                "lyrics": lyrics,
                "style_name": item["style_name"],
                "style": item["style"],
                "why": item["why"],
                "char_count": len(lyrics),
            }
        )

    expected = sorted(verses)
    if covered != expected:
        missing = [key for key in expected if key not in covered]
        duplicates = sorted({key for key in covered if covered.count(key) > 1})
        raise ValueError(f"Coverage failure. Missing: {missing}; duplicates: {duplicates}")

    OUTPUT.mkdir(exist_ok=True)
    (OUTPUT / "staging_plan.json").write_text(
        json.dumps(staged, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    index_lines = [
        "JOSHUA - COMPLETE CHUNK INDEX",
        "===============================",
        f"{len(staged)} chunks total, covering Joshua 1:1-24:33",
        "KJV word-for-word; underscores replace spaces for Suno.",
        f"Absolute lyric limit: fewer than {ABSOLUTE_LIMIT} characters per chunk.",
        "Boundaries follow complete narrative, speech, list, or liturgical movements.",
        "",
        "CHUNK | REFERENCE | CHARACTERS | TITLE",
        "------|-----------|------------|------",
    ]
    for item in staged:
        index_lines.append(
            f"{item['chunk_num']:>5} | {item['reference']:<9} | "
            f"{item['char_count']:>10} | {item['chunk_name']}"
        )
    index_lines.extend(
        [
            "",
            "BOOK MOVEMENT",
            "-------------",
            "Conquest and entry: Chunks 1-17 (Joshua 1:1-12:24)",
            "Division of the land: Chunks 18-32 (Joshua 13:1-21:45)",
            "Covenant and farewell: Chunks 33-38 (Joshua 22:1-24:33)",
        ]
    )
    (OUTPUT / "chunk_index.txt").write_text(
        "\n".join(index_lines) + "\n", encoding="utf-8"
    )

    chunks = []
    for item in staged:
        chunks.extend(
            [
                f"=== {item['title']} ===",
                f"REFERENCE: Joshua {item['reference']}",
                f"MOVEMENT: {item['chunk_name']}",
                f"STYLE: {item['style']}",
                "",
                item["lyrics"],
                "",
            ]
        )
    (OUTPUT / f"chunks_01-{len(staged):02d}.txt").write_text(
        "\n".join(chunks).rstrip() + "\n", encoding="utf-8"
    )

    style_lines = [
        f"JOSHUA STYLE MAP - ALL {len(staged)} CHUNKS",
        "=================================",
        "North star: the text determines the movement; the beat must still carry it.",
        "Cohesion: acoustic strings, hand percussion, low strings, and restrained choir recur.",
        "Variety: choral, folk-hop, trip-hop, neoclassical, gospel, and world textures appear only where earned.",
        "Vocal rule: clear KJV diction, open midrange, and no overlapping lyric lines.",
        "",
        "FORMAT: CHUNK | REFERENCE | STYLE NAME | STYLE TAG | WHY",
    ]
    for item in staged:
        style_lines.extend(
            [
                "",
                f"CHUNK {item['chunk_num']} | Joshua {item['reference']} | {item['style_name']}",
                f'"{item["style"]}"',
                f"WHY: {item['why']}",
            ]
        )
    (OUTPUT / "style_map.txt").write_text(
        "\n".join(style_lines) + "\n", encoding="utf-8"
    )

    print(
        f"Built {len(staged)} Joshua chunks; "
        f"range {min(item['char_count'] for item in staged)}-"
        f"{max(item['char_count'] for item in staged)} characters."
    )


if __name__ == "__main__":
    build()
