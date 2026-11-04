#!/usr/bin/env python3
"""Step 35, part 5 (B4): the climate of every era, written down.

The old code had two hard-coded events — the Little Ice Age and the Year Without a Summer — and
nothing at all for the four thousand three hundred years before them. This is the table that
replaces them: the warm periods, the cold ones, the volcanic winters, the megadroughts, the
failed monsoons and the famines, from the end of the African humid period to the modern warming.

**The one thing that shaped the whole table:** a 2019 synthesis of more than ninety proxy records
(PAGES 2k) found that the Roman Warm Period, the Medieval Warm Period and the Little Ice Age were
*regional phenomena, not globally coherent episodes*. The old code applied the Little Ice Age to
the whole world at once. That is not what the evidence says, so every row here has a centre and a
radius, and a handful that are genuinely hemispheric say so in their note.

Each row is:

    (id, name, kind, startYear, endYear, lat, lon, radiusKm,
     tempChangeDegrees, precipChangePercent, yieldImpactPercent, severity, note, certainty)

* `kind`  — WARMING, COOLING, VOLCANIC, DROUGHT, PLUVIAL, MONSOON, SOLAR
* `lat`, `lon`, `radiusKm` — where it was felt. Radius 0 means everywhere, and is used only for
  the volcanic winters, which really are hemispheric within a year or two.
* `tempChangeDegrees` — degrees Celsius against the twentieth-century mean, over that region
* `precipChangePercent` — change in rainfall
* `yieldImpactPercent` — what it did to a harvest
* `severity` — 1 to 10, for the register to rank by
* `certainty` — "recorded" where the year is in the record (an eruption, a famine with dates);
  "estimated" where it is a reconstruction with soft edges, which most of these are

Sources: Wikipedia's *List of periods and events in climate history* and *Volcanic winter*, the
Journal of Climate study of the 1876-78 Global Famine, and the standard reconstructions of each
region. Numbers are rounded, deliberately: a reconstruction that says 0.4 degrees is not claiming
a second decimal place.
"""
# id, name, kind, start, end, lat, lon, radius km, tempC, precip%, yield%, severity, note, certainty
PERIODS = [
    # ------------------------------------------------- the long periods of the Holocene ----
    ("african_humid_end", "End of the African Humid Period", "DROUGHT", -3500, -1500,
     22.0, 15.0, 3000, 0.0, -50.0, -30.0, 8,
     "The monsoon withdrew and the Sahara came back. Where there had been lakes and giraffes and "
     "cattle herders there was sand, and the people went to the Nile.", "estimated"),
    ("piora_oscillation", "Piora Oscillation", "COOLING", -3200, -2900,
     47.0, 10.0, 2500, -0.5, 10.0, -10.0, 4,
     "A cold snap, wetter in Europe and drier elsewhere, at the time the horse was being "
     "domesticated on the steppe.", "estimated"),
    ("neopluvial", "Neopluvial of North America", "PLUVIAL", -3000, 1,
     40.0, -100.0, 3000, 0.0, 20.0, 8.0, 3,
     "Three thousand years of wetter country across North America, as the world begins.",
     "estimated"),
    ("four_point_two_ka", "4.2-kiloyear event", "DROUGHT", -2200, -2100,
     0.0, 0.0, 0, -0.3, -30.0, -35.0, 9,
     "Dry through most of the twenty-second century BC, across the Old Kingdom of Egypt, the "
     "Akkadian empire, the cities of the Indus and the cultures of Persia and China. All four "
     "broke at once, and the beginning of the Meghalayan stage is dated from it.", "estimated"),
    ("meghalayan_stage", "Meghalayan stage", "DROUGHT", -2250, 1850,
     0.0, 0.0, 0, 0.0, 0.0, 0.0, 1,
     "The stage of the Holocene the world is in: begun with the 4.2 ka event, and cooler and "
     "drier than the Northgrippian before it. This row carries no anomaly on purpose. Every "
     "other number in this table is measured against the twentieth century, which is itself in "
     "the Meghalayan, so subtracting the stage as well would take the same thing off twice. It "
     "is here so that the era reads as itself when a player asks what the climate was.",
     "estimated"),
    ("ghaggar_hakra_dry", "The drying of the Ghaggar-Hakra", "DROUGHT", -1900, -1500,
     29.0, 74.0, 1500, 0.0, -35.0, -40.0, 8,
     "The summer monsoon weakened and the Ghaggar, the great river of the eastern Indus country, "
     "dried where it ran. The cities that had depended on it were left for the Ganges and the "
     "Gujarat coast, and the Indus cities of the east went with them.", "estimated"),
    ("mba_cold_epoch", "Middle Bronze Age Cold Epoch", "COOLING", -1800, -1500,
     55.0, -20.0, 4000, -0.5, 0.0, -12.0, 4,
     "Unusually cold across the North Atlantic, and the glaciers of the Alps came down.",
     "estimated"),
    ("thera_1600", "The eruption of Thera", "VOLCANIC", -1650, -1600,
     36.4, 25.4, 900, -0.5, 0.0, -20.0, 6,
     "Santorini blew up in the Aegean, in the years Minoan Crete was at its height. The ash fell "
     "on Crete and on Egypt; how far the cooling reached is argued, so this one is held to the "
     "islands.", "estimated"),
    ("three_point_two_ka", "The 3.2-kiloyear event", "DROUGHT", -1200, -1150,
     37.0, 30.0, 2500, -0.2, -25.0, -30.0, 7,
     "A sudden dry and cold spell across the eastern Mediterranean and the Near East, at the "
     "time of the Late Bronze Age collapse: Hattusa, Ugarit and Mycenae fell within a "
     "generation of each other, and the Sea Peoples came south.", "estimated"),
    ("two_point_eight_ka", "The 2.8-kiloyear event", "COOLING", -850, -760,
     55.0, -20.0, 4000, -0.4, -5.0, -10.0, 5,
     "A Bond event: cold and dry across the North Atlantic, with the Sun at its Homeric "
     "minimum, at the time the Greek world was rebuilding after the dark age.", "estimated"),
    ("iron_age_cold", "Iron Age Cold Epoch", "COOLING", -900, -300,
     55.0, -20.0, 4000, -0.6, -5.0, -12.0, 5,
     "Cold in the North Atlantic from the ninth century BC, perhaps the Homeric Minimum of solar "
     "activity. Wet in the bogs of northern Europe, which is where the bog bodies come from.",
     "estimated"),
    ("homeric_minimum", "Homeric Minimum", "SOLAR", -800, -500,
     55.0, -20.0, 4000, -0.2, 0.0, -4.0, 3,
     "A long low in the Sun's activity, named after the Greek poets whose age it fell in.",
     "estimated"),

    # ------------------------------------------------------------ the warm and cold ages ----
    ("roman_warm", "Roman Warm Period", "WARMING", -250, 400,
     46.0, 5.0, 3000, 0.5, 8.0, 8.0, 5,
     "Warm in Europe, the Mediterranean and the North Atlantic: olives grew beyond their limits "
     "and the vine went north. A 2019 synthesis of ninety proxy records found it was a regional "
     "warmth, not a world-wide one.", "estimated"),
    ("roman_humid", "Roman Humid Period", "PLUVIAL", -200, 200,
     38.0, 15.0, 2000, 0.0, 15.0, 6.0, 4,
     "Wetter round the Mediterranean and in North Africa, and high Nile floods, through the "
     "centuries of Rome's greatest reach.", "estimated"),
    ("dark_ages_cold", "Dark Ages Cold Period", "COOLING", 400, 800,
     55.0, -10.0, 4000, -0.4, -5.0, -10.0, 5,
     "Cooler across the North Atlantic between the Roman warm and the Medieval.", "estimated"),
    ("late_antique_lia", "Late Antique Little Ice Age", "COOLING", 536, 660,
     0.0, 0.0, 0, -0.8, -5.0, -20.0, 8,
     "The longest and deepest cold of the last two thousand years, begun by the eruptions of 536 "
     "and 540 and kept up by 547 and 626. The Justinian plague came with it, and the steppe "
     "peoples moved.", "recorded"),
    ("moche_el_nino", "The El Nino floods that ended the Moche", "MONSOON", 550, 600,
     -8.0, -78.0, 1200, 0.0, 60.0, -40.0, 7,
     "Megafloods on the north coast of Peru, read out of the mud layers in the adobe of the "
     "Moche temples: the canals silted, the fields were buried, and the Moche state did not "
     "come back.", "estimated"),
    ("tang_warm", "The Sui-Tang warm period", "WARMING", 570, 780,
     34.0, 108.0, 2500, 0.5, 5.0, 8.0, 5,
     "Warm across eastern China through the Sui and the Tang: the bureau that supplied the "
     "courts with citrus could grow oranges further north than it can now, and the empire had "
     "the grain to feed half a million people in Chang'an.", "estimated"),
    ("nile_floods_medieval", "The high Niles of the Middle Ages", "PLUVIAL", 950, 1250,
     24.0, 33.0, 2000, 0.0, 12.0, 10.0, 4,
     "Three centuries of high floods on the Nile, read off the nilometer at Rawda: wetter "
     "headwaters in the Ethiopian highlands, and full granaries in Egypt.", "estimated"),
    ("mca_east_asia", "The Medieval Warm Period in East Asia", "WARMING", 950, 1250,
     34.0, 108.0, 2500, 0.3, 3.0, 5.0, 4,
     "Warm in eastern China and Japan while the North Atlantic was warm too, though the two are "
     "not the same episode and did not begin and end together.", "estimated"),
    ("medieval_warm", "Medieval Warm Period", "WARMING", 950, 1250,
     55.0, -10.0, 4000, 0.4, 5.0, 8.0, 5,
     "Warm in the North Atlantic and in Europe: vines in England, the Norse in Greenland and at "
     "L'Anse aux Meadows. But the tropical Pacific was cooler at the same time, and these are "
     "the centuries of the great droughts in the Americas.", "estimated"),
    ("little_ice_age", "Little Ice Age", "COOLING", 1300, 1850,
     55.0, -10.0, 4000, -0.6, 0.0, -8.0, 6,
     "Cold across the North Atlantic and Europe for five and a half centuries: the Norse left "
     "Greenland, the Alpine glaciers came down over farms and villages, and the Thames froze. "
     "Not a world-wide episode, and not synchronous — different places were coldest hundreds of "
     "years apart.", "recorded"),
    ("nile_low_lia", "The low Niles of the Little Ice Age", "DROUGHT", 1310, 1500,
     24.0, 33.0, 2000, -0.2, -12.0, -20.0, 6,
     "Low floods through the fourteenth and fifteenth centuries, and famine in Egypt with them: "
     "the plague of the 1340s came into a country already short of grain.", "estimated"),
    ("lia_andes", "The Little Ice Age in the Andes", "COOLING", 1500, 1800,
     -15.0, -70.0, 2500, -0.5, -10.0, -15.0, 6,
     "The glaciers of the Cordillera Blanca and of Patagonia came forward, and the high farms "
     "and the herders' pastures went under ice. Different centuries from Europe's coldest.",
     "estimated"),
    ("lia_east_asia", "The Little Ice Age in Asia", "COOLING", 1350, 1900,
     40.0, 110.0, 3600, -0.6, -5.0, -15.0, 6,
     "Cold from the fourteenth century across China and Japan, read out of the phenology of the "
     "cherry blossom and the frozen lakes of the Yangtze delta; across Siberia, where the ground "
     "froze deeper every year and never quite thawed; and, at the edge of this circle, over "
     "South Asia, where the same centuries show up as a weaker monsoon and harder winters. Its "
     "coldest decades were not Europe's, which is why it is not the same row.", "estimated"),
    ("lia_north_america", "The Little Ice Age in North America", "COOLING", 1400, 1850,
     45.0, -100.0, 3000, -0.4, -5.0, -8.0, 5,
     "Cold over the continent from the fifteenth century: shorter growing seasons in New "
     "England, the ice on the Great Lakes lasting into June, and the glaciers of the Rockies "
     "advancing. A fourth cold region with its own dates, not Europe's Little Ice Age carried "
     "across the Atlantic.", "estimated"),
    ("modern_warming", "Modern warming, to 1950", "WARMING", 1850, 1950,
     0.0, 0.0, 0, 0.3, 0.0, 2.0, 4,
     "The world comes out of the Little Ice Age and begins to warm, slowly at first.",
     "recorded"),
    ("modern_warming_late", "Modern warming, after 1970", "WARMING", 1970, 2025,
     0.0, 0.0, 0, 1.0, 0.0, 0.0, 7,
     "The warming quickens, and every decade after 1970 is warmer than the one before it.",
     "recorded"),

    # ---------------------------------------------------------------- the solar minima ----
    ("oort_minimum", "Oort Minimum", "SOLAR", 1010, 1050,
     55.0, -10.0, 4000, -0.2, 0.0, -4.0, 3,
     "A low in sunspots near the beginning of the Medieval Warm Period.", "estimated"),
    ("wolf_minimum", "Wolf Minimum", "SOLAR", 1280, 1350,
     55.0, -10.0, 4000, -0.2, 0.0, -5.0, 3,
     "Sunspots almost stop for seventy years, and the Great Famine comes at the end of it.",
     "recorded"),
    ("sporer_minimum", "Sporer Minimum", "SOLAR", 1450, 1540,
     55.0, -10.0, 4000, -0.3, 0.0, -7.0, 4,
     "The long low in solar activity that ran from the mid-fifteenth century into the "
     "sixteenth.", "estimated"),
    ("maunder_minimum", "Maunder Minimum", "SOLAR", 1645, 1715,
     55.0, -10.0, 4000, -0.3, -5.0, -9.0, 6,
     "The coldest stretch of the Little Ice Age. Sunspots were counted in dozens instead of "
     "thousands for seventy years; the Thames froze solid enough to hold a frost fair on it, and "
     "in Scotland these were the seven ill years.", "recorded"),
    ("dalton_minimum", "Dalton Minimum", "SOLAR", 1790, 1830,
     55.0, -10.0, 4000, -0.2, 0.0, -6.0, 4,
     "A low in solar activity with cold summers across Europe, ending in the Year Without a "
     "Summer.", "recorded"),
    ("modern_maximum", "Modern Maximum", "SOLAR", 1914, 2000,
     0.0, 0.0, 0, 0.1, 0.0, 2.0, 2,
     "The Sun at its most active in eight thousand years, at the same time as the world warms.",
     "estimated"),

    # -------------------------------------------------------------- the volcanic winters ----
    ("volcanic_536", "Volcanic winter of 536", "VOLCANIC", 536, 546,
     0.0, 0.0, 0, -1.4, -5.0, -30.0, 9,
     "The worst year to be alive. A dry fog dimmed the sun for eighteen months; snow fell in "
     "summer in China; crops failed from Ireland to China; the Justinian plague followed. A "
     "second eruption in 540 kept it going, and 547 and 626 finished the work.", "recorded"),
    ("baekdu_946", "The Millennium Eruption of Baekdu", "VOLCANIC", 946, 948,
     42.0, 128.1, 2500, -0.6, 0.0, -15.0, 7,
     "Changbaishan, on the border of Korea and Manchuria, in one of the two or three largest "
     "eruptions of the last two thousand years. Its ash is found as far as northern Japan, and "
     "the summer of 947 was cold across Eurasia.", "recorded"),
    ("samalas_1257", "Samalas eruption of 1257", "VOLCANIC", 1258, 1260,
     0.0, 0.0, 0, -1.3, 0.0, -25.0, 8,
     "The single greatest injection of sulfur into the stratosphere of the Common Era, from "
     "Rinjani on Lombok. Famine and mass burials across Europe, and the beginning of the Little "
     "Ice Age is dated from it.", "recorded"),
    ("kuwae_1452", "Mystery eruptions of 1452 and 1458", "VOLCANIC", 1453, 1460,
     0.0, 0.0, 0, -1.2, 0.0, -20.0, 8,
     "Two great eruptions eight years apart, one in each hemisphere. The attribution of the "
     "southern one to Kuwae caldera is still argued over.", "recorded"),
    ("huaynaputina_1600", "Huaynaputina, 1600", "VOLCANIC", 1600, 1603,
     0.0, 0.0, 0, -0.8, -5.0, -30.0, 8,
     "The largest eruption in South American history, in Peru, in February 1600. It brought on "
     "the Russian famine of 1601-1603, which killed two million people.", "recorded"),
    ("parker_1641", "The eruption of Mount Parker, 1641", "VOLCANIC", 1641, 1643,
     6.0, 125.0, 2500, -0.4, -5.0, -15.0, 6,
     "A very large eruption in Mindanao, in January 1641, that darkened the sky over the "
     "Philippines and is read in the tree rings of Eurasia: one of the coldest years of the "
     "seventeenth century, in the middle of the droughts that ended the Ming.", "recorded"),
    ("laki_1783", "Laki, 1783", "VOLCANIC", 1783, 1785,
     60.0, -20.0, 3000, -1.0, -10.0, -25.0, 7,
     "An eight-month fissure eruption in Iceland that put a hundred and twenty million tonnes of "
     "sulfur dioxide into the air. It killed a fifth of Iceland's people, its livestock and its "
     "crops, and a blue haze hung over Europe and a hard winter came after it.", "recorded"),
    ("tambora_1815", "Tambora, 1815: the Year Without a Summer", "VOLCANIC", 1815, 1818,
     0.0, 0.0, 0, -0.7, 10.0, -25.0, 8,
     "Tambora blew in April 1815 and 1816 was the Year Without a Summer: snow in June in New "
     "England, harvests failed across Europe and the worst famine of the century, and in the "
     "wet, dark summer at Geneva Mary Shelley wrote Frankenstein.", "recorded"),
    ("krakatoa_1883", "Krakatoa, 1883", "VOLCANIC", 1883, 1886,
     0.0, 0.0, 0, -0.3, 0.0, -8.0, 5,
     "Thirty thousand dead in the Sunda Strait, and three years of red sunsets and cooler "
     "summers round the world.", "recorded"),
    ("agung_1963", "Agung, 1963", "VOLCANIC", 1963, 1965,
     0.0, 0.0, 0, -0.2, 0.0, -3.0, 3,
     "An eruption on Bali that cooled the world for two years.", "recorded"),
    ("pinatubo_1991", "Pinatubo, 1991", "VOLCANIC", 1991, 1993,
     0.0, 0.0, 0, -0.5, 0.0, -6.0, 4,
     "Twenty million tonnes of sulfur dioxide, tracked by satellite: the clearest instrumented "
     "volcanic winter there is.", "recorded"),

    # ------------------------------------------------------ droughts, and the states they broke ----
    ("maya_drought", "The Maya droughts", "DROUGHT", 760, 930,
     19.0, -90.0, 1500, 0.0, -45.0, -50.0, 9,
     "Four pulses of drought about fifty years apart, centred on 760, 810, 860 and 910: the most "
     "severe drought of the last seven thousand years on the Yucatan, with rainfall down by "
     "perhaps half at its worst. The great cities were abandoned one after another in step with "
     "them.", "recorded"),
    ("tiwanaku_drought", "The Tiwanaku drought", "DROUGHT", 1000, 1100,
     -16.0, -68.0, 1200, 0.0, -30.0, -40.0, 7,
     "A century without steady rain on the altiplano. Lake Titicaca fell, the raised fields of "
     "Tiwanaku dried, and the city was left.", "estimated"),
    ("ancestral_puebloan", "The Great Drought of the Ancestral Puebloans", "DROUGHT", 1276, 1299,
     36.0, -108.0, 1200, 0.0, -25.0, -45.0, 8,
     "Twenty-three years without rain enough, read out of the tree rings year by year. Mesa "
     "Verde and the cliff dwellings of the Four Corners were left, and the people went south to "
     "the Rio Grande and the Hopi mesas.", "recorded"),
    ("north_american_megadrought", "The Medieval megadrought of North America", "DROUGHT",
     900, 1300, 40.0, -100.0, 2200, -0.2, -20.0, -25.0, 6,
     "Centuries of drought across the Great Plains and the west, through the same years the "
     "North Atlantic was warm.", "estimated"),
    ("khmer_drought", "The droughts that ended Angkor", "DROUGHT", 1300, 1450,
     13.0, 104.0, 1200, 0.0, -25.0, -35.0, 7,
     "Long droughts and then great floods against a water system built for a steady monsoon; "
     "the canals of Angkor broke and the city was left to the forest.", "estimated"),
    ("great_famine_1315", "The Great Famine of 1315", "PLUVIAL", 1315, 1317,
     50.0, 5.0, 2500, -0.5, 60.0, -60.0, 9,
     "Rain without pause from the spring of 1315 to harvest, and again, and again. The grain "
     "rotted in the field, the salt could not be made, the sheep died of rot, and a tenth of "
     "Europe's people were dead by 1317. It is how the Little Ice Age began.", "recorded"),
    ("aztec_famine_1450", "The famine of One Rabbit", "DROUGHT", 1450, 1454,
     19.4, -99.1, 900, 0.0, -40.0, -55.0, 8,
     "Frosts in the Basin of Mexico, then four years without rain under Moctezuma the elder. "
     "The Annals of Cuauhtitlan tell of people eating the weeds of the lake shore and selling "
     "their children for maize, and of the Flower Wars fought to take captives for the "
     "sacrifice that was meant to end it.", "recorded"),
    ("european_drought_1540", "The drought of 1540", "DROUGHT", 1540, 1540,
     48.0, 8.0, 2000, 2.0, -60.0, -40.0, 7,
     "Eleven months without rain across Europe. The Rhine, the Loire and the Po could be walked "
     "across, the wells went dry, the woods burned, and the wine was sweet enough to be "
     "remembered for centuries.", "estimated"),
    ("cocoliztli_1545", "The drought and the cocoliztli of 1545", "DROUGHT", 1545, 1550,
     19.5, -99.0, 1200, 0.0, -35.0, -50.0, 9,
     "A drought across central Mexico, and then a haemorrhagic fever that killed perhaps "
     "fifteen million people, four fifths of the country — the worst epidemic of the "
     "conquest, and it came back in 1576. The fever was not caused by the weather; the "
     "hunger that met it was.", "recorded"),
    ("deccan_famine_1630", "The Deccan famine of 1630-32", "DROUGHT", 1630, 1632,
     20.0, 76.0, 1800, 0.0, -45.0, -55.0, 8,
     "The monsoon failed twice running across the Deccan and Gujarat, in the third year of Shah "
     "Jahan's reign. Seven million died; the Dutch and the English at Surat wrote of the roads "
     "full of the dead.", "recorded"),
    ("ming_drought", "The drought of the last Ming years", "DROUGHT", 1637, 1643,
     35.0, 108.0, 1800, -0.3, -30.0, -45.0, 8,
     "The worst drought in northern China in five centuries, through the last years of the Ming: "
     "the wells dried, the locusts came, and the rebellions that ended the dynasty began.",
     "estimated"),
    ("bengal_famine_1770", "The Great Bengal famine of 1770", "MONSOON", 1770, 1771,
     23.0, 89.0, 1500, 0.0, -40.0, -60.0, 9,
     "The monsoon failed across Bengal and Bihar, on land where the Company had just taken the "
     "right to collect the revenue and had no mind to remit it. Ten million died, a third of "
     "the province.", "recorded"),
    ("chalisa_famine", "The Chalisa famine", "DROUGHT", 1783, 1784,
     26.0, 78.0, 2000, 0.0, -40.0, -50.0, 8,
     "The monsoon failed across northern India in the same years that Laki was in the air, and "
     "the Doj Bara, the skull famine of 1791, followed within a decade.", "estimated"),
    ("aji_famine", "The Great Tenmei famine", "DROUGHT", 1782, 1788,
     38.0, 140.0, 1200, -0.3, -25.0, -45.0, 7,
     "Cold and wet and then starving in northern Japan through the Tenmei era, the worst of "
     "Japan's three great famines.", "estimated"),
    ("dust_bowl", "The Dust Bowl", "DROUGHT", 1930, 1936,
     37.0, -100.0, 1400, 0.3, -35.0, -45.0, 8,
     "Years of drought on the southern plains, on land ploughed out of grass that had held it "
     "down, and the soil went east in black blizzards.", "recorded"),
    ("sahel_drought", "The Sahel drought", "DROUGHT", 1968, 1985,
     15.0, 0.0, 2200, 0.0, -30.0, -35.0, 8,
     "Seventeen years without the rains across the Sahel, from Senegal to Sudan; Lake Chad fell "
     "and the herders came into the towns.", "recorded"),

    # ------------------------------------------------------------- El Nino and the famines ----
    ("el_nino_1876_world", "The Global Famine of 1876-78", "MONSOON", 1876, 1879,
     0.0, 0.0, 0, 0.0, -8.0, -8.0, 10,
     "Drought in India, China, Brazil, Egypt and southern Africa at the same time: a record El "
     "Nino in 1877-78 on top of a record Indian Ocean dipole in 1877. More than fifty million "
     "died, three per cent of everyone alive. It is the worst climate disaster in the record.",
     "recorded"),
    ("el_nino_1876_india", "The Great Famine in India", "MONSOON", 1876, 1878,
     20.0, 78.0, 2200, 0.0, -45.0, -45.0, 10,
     "The monsoon failed in 1876 and again in 1877, the driest summer monsoon ever recorded. "
     "Between twelve and twenty-nine million died, in a country where the Viceroy held that "
     "relief should not be given too freely. In Telangana the old tanks and lakes — Ramappa "
     "among them — were what saved the districts that had them.", "recorded"),
    ("el_nino_1876_china", "The Northern Chinese Famine", "MONSOON", 1876, 1879,
     35.0, 108.0, 2000, 0.0, -40.0, -45.0, 10,
     "The Dingwu famine: the worst drought in northern China in three hundred years, worst in "
     "Shanxi, where the relief never reached the mountain valleys. Between nineteen and thirty "
     "million died.", "recorded"),
    ("el_nino_1876_brazil", "The Grande Seca of Brazil", "MONSOON", 1877, 1879,
     -8.0, -38.0, 2000, 0.0, -50.0, -45.0, 9,
     "The greatest drought in Brazil's history; two million died in the backlands of the north "
     "east, and half a million left for the Amazon.", "recorded"),
    ("indian_famines_1896", "The Indian famines of 1896 and 1899", "MONSOON", 1896, 1902,
     20.0, 78.0, 2200, 0.0, -30.0, -45.0, 8,
     "The monsoon failed twice in five years, and famine and plague took millions across the "
     "Deccan, the Central Provinces and Gujarat.", "recorded"),
    ("el_nino_1982", "The El Nino of 1982-83", "MONSOON", 1982, 1983,
     0.0, -140.0, 5000, 0.3, -30.0, -15.0, 6,
     "One of the strongest of the century: drought in Australia, Indonesia and southern Africa, "
     "floods in Ecuador and Peru, and the coral of the eastern Pacific bleached.", "recorded"),
    ("el_nino_1997", "The El Nino of 1997-98", "MONSOON", 1997, 1998,
     0.0, -140.0, 5000, 0.3, -25.0, -12.0, 6,
     "Fires in Indonesia, floods in California and Peru, and a failed monsoon that the Indian "
     "economy did not even notice.", "recorded"),
    # ---------------------------------------------------------- the hard winters of Europe ----
    ("great_frost_1709", "The Great Frost of 1709", "COOLING", 1709, 1709,
     48.0, 5.0, 2200, -3.0, 0.0, -40.0, 8,
     "The coldest winter in five hundred years of records: every river in France froze, the "
     "Seine and the Venetian lagoon with them, the olive trees of Provence died where they "
     "stood, and the harvest of 1709 did not come. Six hundred thousand died in France alone.",
     "recorded"),
    ("irish_frost_1740", "The Great Frost of 1740-41", "COOLING", 1740, 1741,
     53.3, -8.0, 1200, -2.0, 0.0, -45.0, 8,
     "Bliain an Air, the year of the slaughter: the coldest winter in the Irish record, then a "
     "dry spring and no harvest. The potato and the grain both failed and perhaps four hundred "
     "thousand died of hunger and of the fevers that came with it.", "recorded"),
    ("irish_famine", "The Irish famine, 1845-52", "PLUVIAL", 1845, 1852,
     53.3, -8.0, 800, -0.3, 25.0, -60.0, 9,
     "Cool wet summers in which Phytophthora infestans took the potato, on an island where a "
     "third of the people ate nothing else. A million died and a million left; Ireland has "
     "fewer people now than it had in 1841.", "recorded"),

    # ---------------------------------------------- the famines of the last five centuries ----
    ("russian_famine_1891", "The Russian famine of 1891-92", "DROUGHT", 1891, 1892,
     53.0, 48.0, 1800, 0.0, -35.0, -50.0, 7,
     "The Volga country went dry: the winter grain never came up, and half a million died of "
     "hunger and cholera across seventeen provinces.", "recorded"),
    ("russian_famine_1921", "The Russian famine of 1921-22", "DROUGHT", 1921, 1922,
     52.0, 45.0, 2000, 0.0, -40.0, -55.0, 9,
     "Drought on the Volga on top of seven years of war and requisitioning: five million died, "
     "and it took two years of American relief to stop it.", "recorded"),
    ("china_famine_1928", "The Chinese famine of 1928-30", "DROUGHT", 1928, 1930,
     35.0, 105.0, 2000, 0.0, -35.0, -50.0, 8,
     "Three years without rain across the north west — Gansu, Shaanxi, Henan, Shandong — on top "
     "of the wars; between three and six million died.", "estimated"),
    ("ethiopian_famine_1983", "The Ethiopian famine of 1983-85", "DROUGHT", 1983, 1985,
     10.0, 39.0, 1600, 0.0, -35.0, -55.0, 8,
     "The rains failed across the highlands, and war was being fought in the same provinces: a "
     "million dead, and the famine that the world watched on television.", "recorded"),
    ("east_africa_2011", "The East Africa drought of 2011", "DROUGHT", 2011, 2011,
     5.0, 42.0, 1800, 0.0, -40.0, -55.0, 7,
     "The worst drought in sixty years across Somalia, Ethiopia and Kenya: thirteen million "
     "needed food aid, and the herders of the Horn lost their herds.", "recorded"),

    # ------------------------------------------------- the droughts and heat of our own day ----
    ("australian_federation_drought", "The Federation Drought", "DROUGHT", 1895, 1903,
     -30.0, 140.0, 2200, 0.0, -35.0, -45.0, 7,
     "Eight years of drought over most of Australia, as the federation was being made: the "
     "sheep died in their millions and the country never quite went back to where it had been.",
     "recorded"),
    ("australian_millennium_drought", "The Millennium Drought", "DROUGHT", 1997, 2009,
     -33.0, 145.0, 2200, 0.2, -25.0, -25.0, 7,
     "Thirteen years of the Big Dry across south eastern Australia: the Murray ran out, "
     "Adelaide and Melbourne built desalination plants, and the water of the basin was "
     "rationed.", "recorded"),
    ("european_heatwave_2003", "The European heatwave of 2003", "WARMING", 2003, 2003,
     47.0, 5.0, 2300, 2.5, -30.0, -25.0, 8,
     "The hottest summer in five hundred years of European records: two or three degrees above "
     "the mean for three months, with seventy thousand more deaths than usual, and the old "
     "dying in the flats of Paris.", "recorded"),
    ("russian_heatwave_2010", "The Russian heatwave of 2010", "WARMING", 2010, 2010,
     56.0, 38.0, 2000, 5.0, -35.0, -45.0, 8,
     "Forty days over thirty degrees in Moscow, seven degrees above the mean, the wheat harvest "
     "down by a third and exports stopped: fifty-five thousand dead and bread prices rising in "
     "Egypt.", "recorded"),
    ("syrian_drought", "The Levant drought of 2006-10", "DROUGHT", 2006, 2010,
     35.0, 38.0, 1200, 0.0, -35.0, -50.0, 7,
     "The worst drought in the instrumental record of the Fertile Crescent. The wells of the "
     "north east went dry and four hundred thousand people left the land for the cities; how "
     "much of the war that followed belongs to the drought is still being argued.", "recorded"),
    ("cape_town_drought", "The Cape Town drought", "DROUGHT", 2015, 2018,
     -33.9, 18.4, 600, 0.0, -40.0, -40.0, 6,
     "Three winters without rain in the Western Cape, and a city of four million counting down "
     "to Day Zero, when the taps would have been turned off.", "recorded"),
    ("amazon_drought_2023", "The Amazon droughts", "DROUGHT", 2023, 2024,
     -3.0, -60.0, 2200, 0.5, -30.0, -20.0, 7,
     "The rivers of Amazonia at their lowest ever measured, in 2023 and again in 2024: the "
     "floating villages of the Solimoes cut off, the fish dying in the warm shallows, and the "
     "forest itself beginning to dry.", "recorded"),
    ("drought_2022", "The drought of 2022", "DROUGHT", 2022, 2022,
     45.0, 10.0, 2500, 1.5, -30.0, -25.0, 7,
     "The driest summer in five hundred years over Europe, at the same time as the Yangtze ran "
     "dry and the hydropower of Sichuan failed; the rivers of Italy, France, Spain and Germany "
     "could be walked across.", "recorded"),
]
