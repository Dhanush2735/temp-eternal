#!/usr/bin/env python3
"""Step 35, part 4 (B2): the water that moved. A hand-written table, not a fetched one.

B2 asks what no data set gives: coasts, deltas, river courses and shrinking seas, by year. There
is no download for this. Wikidata has an item for the Aral Sea and none for the year the Yellow
River left the Huai; nobody publishes a shapefile of the Zuiderzee in 1500. So this table is
written, one line at a time, from the historical record, and every line carries the year it
happened, where, how wide an area it covers, and whether the year is a recorded one or an
estimate.

The rule for putting a row in: **a person standing there in that year would have noticed.** The
Aral Sea going, the Zuiderzee closing, the Yellow River moving four hundred miles, London's
Thames a mile wide where the Embankment is now. Not: every marsh drained, every harbour silted by
a metre.

Each row is:

    (name, kind, lat, lon, radiusKm, year, endYear or None, change, note, certainty)

* `kind`     — what moved: river, coast, delta, lake, sea, marsh, strait, canal, works
* `change`   — what happened:
      course    the river took a new bed
      dried     the water went away entirely
      shrank    the water drew back, but did not go
      flooded   land became water
      drained   people let the water out of a lake or a marsh
      dammed    a river was stopped and a lake made behind it
      advanced  the land grew out into the water
      retreated the water came back over the land
      reclaimed the water was made into land by people
      diverted  the river's water was taken somewhere else
      silted    a channel or a harbour filled up
      closed    a strait, a bay or an arm of the sea was cut off
      breached  a dam, a dike or a bank gave way
      rose      the level went up
      subsided  the land sank under the water
* `year`     — when it happened; `endYear` when the change was undone or completed
* `certainty`— "recorded" where a date is in the record, "estimated" where it is a range, a
               tradition, or an inference. Every row is one or the other; there is no third kind.

Nothing here is fetched, so nothing here can be re-fetched. The sources are named in the pack.
"""
# name, kind, lat, lon, radius km, year, end year, change, note, certainty
CHANGES = [
    # ---------------------------------------------------------------- China ----
    ("Yellow River, Yu's course", "river", 38.00, 117.70, 120, -3000, -602, "course",
     "The river ran north past Tianjin into the Bohai Sea, as it had since before records begin.",
     "estimated"),
    ("Yellow River, first recorded avulsion", "river", 37.90, 118.60, 130, -602, 11, "course",
     "The Western Han course: the river turned east and entered the sea on the north coast of "
     "Shandong. The first of 26 recorded changes of course.", "recorded"),
    ("Yellow River, Eastern Han course", "river", 37.80, 119.10, 130, 11, 1048, "course",
     "Wang Jing's works held the river on a new bed to the sea for a thousand years, the longest "
     "it has ever been held.", "recorded"),
    ("Yellow River, Northern Song course", "river", 38.98, 117.68, 140, 1048, 1128, "course",
     "The river broke north into the Hai River system and entered the sea at Dagu, its "
     "northernmost mouth.", "recorded"),
    ("Yellow River, the southern diversion", "river", 34.00, 120.30, 200, 1128, 1194, "course",
     "Du Chong broke the southern dikes to stop the Jin army. The river took the Si and the Huai "
     "and emptied into the Yellow Sea south of Shandong, for the first time in record.", "recorded"),
    ("Huai River, mouth lost", "river", 33.50, 120.50, 120, 1194, None, "silted",
     "The Yellow River came south into the Huai and silted its mouth shut. The Huai never "
     "reached the sea again; it pools into Hongze Lake and runs south to the Yangtze.", "recorded"),
    ("Yellow River, the Guo River course", "river", 33.80, 118.00, 180, 1289, 1324, "course",
     "The river took the bed of the Guo and much of the Huai, entering the Yellow Sea well south "
     "of Shandong.", "recorded"),
    ("Yellow River, return to the Bohai", "river", 34.85, 114.75, 250, 1855, None, "course",
     "The river broke its north bank at Tongwaxiang in Lankao on 1 August 1855 and took the old "
     "bed of the Daqing River to the Bohai Sea, four hundred miles from its old mouth.",
     "recorded"),
    ("Yellow River, Huayuankou breach", "river", 34.92, 113.65, 200, 1938, 1947, "breached",
     "The southern levee was opened at Huayuankou to stop the Japanese advance. For nine years "
     "the whole river ran into the Huai; millions were drowned and displaced, and the Huai basin "
     "was wrecked for a generation.", "recorded"),
    ("Grand Canal, Sui completion", "canal", 34.30, 117.20, 300, 609, None, "opened",
     "The Sui joined the earlier canals into one waterway from the Yangtze to Zhuo commandery "
     "near Beijing, over a thousand miles.", "recorded"),
    ("Grand Canal, Yuan rerouting", "canal", 36.00, 116.50, 200, 1283, 1293, "opened",
     "The Yuan cut the canal east of the old Sui line, straight to Dadu (Beijing), and abandoned "
     "the loop through Luoyang and Kaifeng.", "recorded"),
    ("Dongting Lake", "lake", 29.30, 112.90, 90, 1825, 1978, "shrank",
     "The largest lake of the Yangtze plain, 6,000 square kilometres in the Daoguang reign, was "
     "poldered down to a quarter of that; the 1998 flood was the bill for it.", "estimated"),
    ("Poyang Lake", "lake", 29.10, 116.30, 70, 1950, 2000, "shrank",
     "Reclamation and the Three Gorges dam together halved the summer area of China's largest "
     "freshwater lake.", "estimated"),
    ("Lop Nur", "lake", 40.50, 90.30, 80, 1964, None, "dried",
     "The Tarim's terminal lake, a saltpan of 3,000 square kilometres when Marco Polo passed, "
     "was emptied by upstream reservoirs and is now a dry salt crust.", "recorded"),
    ("Three Gorges reservoir", "lake", 30.85, 111.00, 300, 2003, None, "dammed",
     "The dam closed in 1994 and the reservoir filled by 2003: a lake 600 kilometres long, a "
     "million people moved, and the sediment that used to feed the Yangtze delta now held behind "
     "a wall.", "recorded"),
    ("Saemangeum", "coast", 35.80, 126.50, 60, 2006, None, "reclaimed",
     "The 33-kilometre seawall closed in April 2006, cutting off an estuary and making 400 "
     "square kilometres of new land on Korea's west coast.", "recorded"),
    ("Hachirogata", "lake", 39.90, 140.00, 30, 1957, 1977, "reclaimed",
     "Japan's second largest lake was poldered into rice fields over twenty years. What is left "
     "is a shallow lagoon.", "recorded"),
    ("Isahaya Bay", "coast", 32.90, 130.20, 25, 1997, None, "closed",
     "A seven-kilometre dike shut the inner bay of the Ariake Sea in 1997; the tidal flats behind "
     "it died.", "recorded"),

    # ------------------------------------------------------- Central and West Asia ----
    ("Aral Sea, the diversion begins", "sea", 45.00, 59.00, 200, 1960, None, "shrank",
     "Soviet irrigation took the Amu Darya and the Syr Darya into the cotton fields. The sea was "
     "the fourth largest lake on earth, 68,000 square kilometres; by 1961 the level was falling "
     "20 centimetres a year.", "recorded"),
    ("Aral Sea, the split", "sea", 45.50, 58.50, 150, 1987, None, "shrank",
     "The sea divided into the Small Aral in the north and the Great Aral in the south, and the "
     "fishing towns were left tens of kilometres from the water.", "recorded"),
    ("Aral Sea, the eastern basin", "sea", 45.20, 60.00, 120, 2014, None, "dried",
     "In August 2014 the eastern basin dried completely, the first time in six hundred years. It "
     "is the Aralkum desert now.", "recorded"),
    ("Kara-Bogaz-Gol", "sea", 41.10, 52.80, 60, 1980, 1992, "closed",
     "A dam across the channel to the Caspian in 1980 let the shallow gulf evaporate into a salt "
     "plain; the dam was blown open in 1992 and the gulf filled again.", "recorded"),
    ("Caspian Sea, the Soviet fall", "sea", 42.00, 51.00, 400, 1929, 1977, "shrank",
     "The level fell almost three metres as the Volga was dammed and drawn on, stranding the "
     "harbours of Baku and Krasnovodsk.", "recorded"),
    ("Caspian Sea, the unexpected rise", "sea", 42.00, 51.00, 400, 1978, 1995, "rose",
     "The level then rose two and a half metres in eighteen years, drowning oilfields and whole "
     "streets of Baku, and fell again after 1995.", "recorded"),
    ("Lake Urmia", "lake", 37.70, 45.40, 80, 1995, None, "shrank",
     "Once the largest lake in the Middle East, it has lost most of its area to upstream dams and "
     "groundwater pumping since the 1990s.", "recorded"),
    ("Lake Sevan", "lake", 40.40, 45.30, 50, 1933, 1988, "shrank",
     "Soviet drawdown for hydroelectric power and irrigation cut the level by nearly twenty "
     "metres; the lake was partly refilled after 2000.", "recorded"),
    ("Mesopotamian Marshes", "marsh", 31.00, 47.00, 120, 1991, None, "drained",
     "The marshes of the lower Tigris and Euphrates, home to the Marsh Arabs for five thousand "
     "years, were drained by canal and dike to a tenth of their extent. Partly reflooded after "
     "2003.", "recorded"),
    ("Ur, the sea leaves", "coast", 30.96, 46.10, 90, -3000, -500, "advanced",
     "Ur and Eridu stood at the head of the Persian Gulf; the silt of the two rivers has carried "
     "the shore two hundred kilometres south since, so that Ur is now far inland.", "estimated"),
    ("Shatt al-Arab", "river", 30.00, 48.50, 100, 1200, None, "opened",
     "The joined mouth of the Tigris and Euphrates, in the shape it has now, is a late formation; "
     "before it the two rivers reached the gulf apart.", "estimated"),
    ("Marib Dam, the great breach", "works", 15.40, 45.28, 60, 575, None, "breached",
     "The dam of the Sabaeans, which had watered Marib for a thousand years, broke and was not "
     "repaired. The Quran makes of it a parable, and the kingdom's fields went back to desert.",
     "estimated"),
    ("Dead Sea", "lake", 31.50, 35.50, 60, 1960, None, "shrank",
     "The Jordan's water taken for irrigation and potash works has dropped the level more than a "
     "metre a year, and the shore has withdrawn kilometres.", "recorded"),
    ("Lake Hula", "lake", 33.10, 35.60, 25, 1951, 1958, "drained",
     "The lake and its papyrus swamp were drained to make farmland; the soil then oxidized and "
     "sank, and part of the valley was reflooded in 1994.", "recorded"),
    ("Lake Amik", "lake", 36.30, 36.50, 40, 1940, 1975, "drained",
     "The lake of Antioch, a marsh of 300 square kilometres, was drained for cotton; its "
     "waterbirds and its fishing villages went with it.", "recorded"),
    ("Ephesus, the harbour lost", "coast", 37.94, 27.34, 20, 300, 700, "silted",
     "The Cayster silted the harbour of Ephesus, and the city that had been the greatest port of "
     "Asia was left two kilometres from the sea.", "estimated"),
    ("Miletus, the harbour lost", "coast", 37.53, 27.28, 20, 100, 500, "silted",
     "The Maeander filled the Latmian gulf. Miletus, mother of eighty colonies, became a ruin "
     "standing in a plain.", "estimated"),

    # ------------------------------------------------------------------ Africa ----
    ("Lake Chad", "lake", 13.50, 14.50, 250, -1000, 2000, "shrank",
     "Mega-Chad, a sea of 330,000 square kilometres, shrank with the end of the African humid "
     "period; it was still 25,000 in 1963 and under 2,000 by the turn of the century.",
     "estimated"),
    ("Wadi Howar, the Yellow Nile", "river", 18.00, 29.00, 200, -2000, None, "dried",
     "A Nile that ran west into the Sahara past the Ennedi, and carried people and cattle with "
     "it. It was dry by the time of the New Kingdom.", "estimated"),
    ("Lake Moeris and the Faiyum", "lake", 29.40, 30.60, 60, -1850, -1600, "drained",
     "The Middle Kingdom kings took in the swamp of the Faiyum and made farmland of it, the "
     "greatest single reclamation of the ancient world.", "estimated"),
    ("Nile, the Pelusiac branch", "river", 31.05, 32.50, 80, 800, 1200, "dried",
     "Of the seven branches of the Nile in the delta, the easternmost silted up and left Pelusium "
     "high and dry.", "estimated"),
    ("Nile, the Canopic branch", "river", 31.30, 30.30, 70, 500, 900, "dried",
     "The western branch of the delta, the one Herodotus sailed up, closed; Canopus was "
     "abandoned.", "estimated"),
    ("Heracleion-Thonis", "coast", 31.32, 30.15, 20, 700, None, "subsided",
     "Egypt's harbour on the Mediterranean, where the customs of the Greek trade were collected, "
     "went under the sea in Aboukir Bay, with its temples and its ships.", "estimated"),
    ("Alexandria, the eastern harbour", "coast", 31.20, 29.92, 15, 365, None, "subsided",
     "The earthquake of 21 July 365 dropped the royal quarter and the Heptastadion into the "
     "harbour; the palaces of the Ptolemies lie under water to this day.", "recorded"),
    ("Aswan Low Dam", "works", 24.03, 32.88, 60, 1902, None, "dammed",
     "The British dammed the first cataract, and the temple of Philae began to drown.", "recorded"),
    ("Lake Nasser", "lake", 22.50, 32.00, 250, 1964, 1971, "dammed",
     "The High Dam, closed in 1970, made a lake 500 kilometres long. Nubia was drowned; Abu "
     "Simbel was cut out of the rock and moved; the silt that built the delta stopped at Aswan.",
     "recorded"),
    ("Nile delta, the coast retreats", "delta", 31.45, 30.40, 80, 1964, None, "retreated",
     "With the silt held behind the High Dam, the delta's shore began to be eaten by the sea at "
     "tens of metres a year.", "recorded"),
    ("Sudd", "marsh", 7.50, 31.50, 200, -3000, None, "flooded",
     "The Nile's great swamp in South Sudan, as big as England, where the White Nile loses half "
     "its water to evaporation and no boat could pass until the 19th century.", "estimated"),
    ("Jonglei Canal", "canal", 7.10, 31.60, 150, 1978, 1984, "opened",
     "Egypt began to cut a canal past the Sudd to save the water; the work stopped in 1984 when "
     "the civil war reached the diggers, and the canal was never finished.", "recorded"),
    ("Lake Kariba", "lake", -16.90, 28.00, 140, 1958, 1963, "dammed",
     "The Zambezi was closed at Kariba Gorge and the largest man-made lake in the world then "
     "filled behind it; 57,000 people and 5,000 animals were moved in Operation Noah.", "recorded"),
    ("Lake Volta", "lake", 7.50, 0.50, 200, 1965, None, "dammed",
     "Akosombo dammed the Volta and made the largest lake by area on earth; 78,000 people of 700 "
     "towns were resettled.", "recorded"),
    ("Lake Victoria, the Owen Falls", "lake", 0.45, 33.20, 120, 1954, None, "rose",
     "The dam at Jinja raised the lake and made the Ripon Falls, which Speke had named as the "
     "source of the Nile, disappear under water.", "recorded"),
    ("Lake Turkana", "lake", 3.50, 36.00, 120, 1975, None, "shrank",
     "The Omo's dams and irrigation have drawn the Jade Sea down; its level has fallen tens of "
     "metres since the 1970s.", "estimated"),

    # ----------------------------------------------------------- South and Southeast Asia ----
    ("Ghaggar-Hakra", "river", 29.30, 74.30, 200, -1900, None, "dried",
     "The river the Vedas call Sarasvati, glacier-fed to 2500 BCE and lined with hundreds of "
     "Harappan towns, went dry and left its people to move east to the Ganges and south to "
     "Saurashtra. The date is argued: somewhere between 2500 and 1900 BCE.", "estimated"),
    ("Ghaggar-Hakra, the monsoon river", "river", 29.30, 74.30, 200, -2500, None, "shrank",
     "Before it failed, it had already fallen from a glacier-fed perennial river to a monsoon-fed "
     "seasonal one.", "estimated"),
    ("Kosi, the sorrow of Bihar", "river", 25.50, 87.00, 150, 1731, 2008, "course",
     "The Kosi has walked more than a hundred kilometres west across its fan since 1731, and on "
     "18 August 2008 took an old channel back and drowned a thousand square kilometres in a "
     "fortnight.", "recorded"),
    ("Brahmaputra, the western shift", "river", 25.00, 89.70, 150, 1780, 1830, "course",
     "The river left its old channel past Mymensingh for the Jamuna, and the towns of the old "
     "bank were left on a dead branch.", "estimated"),
    ("Allah Bund, the Rann of Kutch", "coast", 24.60, 69.50, 90, 1819, None, "flooded",
     "The earthquake of 16 June 1819 raised a dam eighty kilometres long across the Rann and "
     "drove the Indus off its old bed; the Nara became its eastern channel.", "recorded"),
    ("Rann of Kutch", "sea", 23.90, 69.80, 120, -3000, 1819, "shrank",
     "A shallow arm of the Arabian Sea, navigable in the time of Alexander's pilots, that the "
     "Indus and the earthquake turned into a salt desert.", "estimated"),
    ("Indus delta", "delta", 24.00, 67.50, 120, 1932, None, "retreated",
     "The Sukkur barrage and the dams above it took the water and the silt; the delta has been "
     "eaten back ever since.", "recorded"),
    ("Sundarbans", "delta", 21.90, 89.00, 150, 1200, None, "advanced",
     "The Ganges-Brahmaputra delta, where the mangrove forest grows as fast as the sea takes it, "
     "and where the tigers swim.", "estimated"),
    ("Chao Phraya and the Gulf of Siam", "coast", 13.70, 100.50, 90, 1350, 1782, "advanced",
     "Ayutthaya stood near the sea; Bangkok's site was marsh three hundred years ago, and the "
     "shore has moved seaward ever since as the river fills the gulf.", "estimated"),
    ("Mekong delta", "delta", 9.80, 106.30, 150, 1623, None, "advanced",
     "Khmer and then Vietnamese canals took the delta from the sea in three centuries; it is "
     "still the rice bowl of two countries.", "estimated"),
    ("Dwarka", "coast", 22.24, 68.97, 25, -1500, None, "subsided",
     "The city of Krishna, whose temples and walls lie under the sea off Gujarat. Tradition puts "
     "its drowning at the end of the Dvapara age; the archaeology is a harbour town built over "
     "and over.", "estimated"),
    ("Adam's Bridge", "strait", 9.10, 79.50, 60, 1480, None, "breached",
     "The chain of shoals between India and Lanka, which the chronicles say could be walked, was "
     "opened by a storm in about 1480. The tradition is old; the year is not certain.",
     "estimated"),

    # ------------------------------------------------------------------ Europe ----
    ("Zuiderzee, the St Lucia flood", "sea", 52.70, 5.30, 120, 1287, 1932, "flooded",
     "On 14 December 1287 a North Sea storm broke the dunes between Texel and the mainland and "
     "turned the fresh lake of Almere into a salt bay. Fifty thousand drowned, and Amsterdam got "
     "its sea access and became a port. The bay it made lasted until the Afsluitdijk closed it "
     "in 1932.", "recorded"),
    ("Biesbosch, the St Elizabeth flood", "sea", 51.75, 4.75, 60, 1421, None, "flooded",
     "The night of 18-19 November 1421 took the Grote Waard, seventy villages and their churches, "
     "and left behind a freshwater tidal wetland of reeds and creeks.", "recorded"),
    ("Haarlemmermeer", "lake", 52.35, 4.65, 30, 1852, None, "drained",
     "The Haarlem lake, 'the water wolf' that had eaten the land around it for three centuries, "
     "was pumped dry by three steam engines and became farmland.", "recorded"),
    ("Zuiderzee, the Afsluitdijk", "sea", 52.95, 5.05, 120, 1932, None, "closed",
     "On 28 May 1932 the last gap, the Vlieter, was filled and the sea became a lake. The salt "
     "water was flushed out by the IJssel and the IJsselmeer was born, and a new province came "
     "after it: Wieringermeer 1930, the Noordoostpolder 1942, Flevoland 1957 and 1968.",
     "recorded"),
    ("North Sea flood of 1953", "coast", 51.70, 4.00, 120, 1953, None, "flooded",
     "The night of 31 January to 1 February 1953: 1,836 dead in the Netherlands, 307 in England, "
     "and the Delta Works begun in answer.", "recorded"),
    ("Delta Works", "coast", 51.65, 3.70, 120, 1953, 1997, "closed",
     "Forty-four years of dams, sluices and storm barriers that shut the mouths of the Rhine, "
     "the Meuse and the Scheldt; the Oosterscheldekering was finished in 1986 and the whole "
     "scheme in 1997.", "recorded"),
    ("Dollart", "sea", 53.28, 7.15, 40, 1277, 1520, "flooded",
     "The Ems broke into the moorland behind it and drowned a dozen villages; the bay is still "
     "there at the German border.", "recorded"),
    ("Jadebusen", "sea", 53.50, 8.20, 35, 1164, 1511, "flooded",
     "Storm tides ate the coast of Oldenburg and made a bay where Wilhelmshaven now stands.",
     "recorded"),
    ("Lauwerszee", "sea", 53.40, 6.20, 30, 1969, None, "closed",
     "The last of the Dutch arms of the sea to be shut, after the 1953 flood, and made into a "
     "lake.", "recorded"),
    ("The Fens", "marsh", 52.60, 0.10, 80, 1630, 1652, "drained",
     "Cornelius Vermuyden and the Earl of Bedford drained the Great Level: 3,000 square "
     "kilometres of marsh made into the richest farmland in England, and the ground sinking ever "
     "since for the want of the peat that was taken out.", "recorded"),
    ("Somerset Levels", "marsh", 51.10, -2.80, 50, 1200, 1800, "drained",
     "Monastic and then secular drainage of the Brue and the Parrett took the winter flood off "
     "the moors, slowly, over six centuries.", "estimated"),
    ("The Wash", "coast", 52.90, 0.20, 60, 500, 1800, "retreated",
     "The coast of Norfolk and Lincolnshire has been eaten back for a thousand years: "
     "Ravenser Odd, and whole villages of Holderness, are gone into the sea.", "estimated"),
    ("Lulea, the harbour that rose", "coast", 65.58, 22.15, 30, 1621, 1649, "advanced",
     "The land of the Gulf of Bothnia is still rising nine millimetres a year out of the sea "
     "after the ice. Lulea's first harbour silted within a generation and the town was moved "
     "bodily to a new site in 1649.", "recorded"),
    ("Malaren, cut off from the sea", "lake", 59.40, 17.60, 60, 1200, None, "closed",
     "Post-glacial rebound closed the strait between Lake Malaren and the Baltic, and Birka, "
     "which had been a port of the sea, was left on a lake.", "estimated"),
    ("St Petersburg", "marsh", 59.90, 30.30, 50, 1703, None, "reclaimed",
     "Peter the Great built a capital in 1703 on the marshy islands of the Neva delta, on piles "
     "driven into a swamp, at the cost of tens of thousands of lives.", "recorded"),
    ("Lake Neusiedl", "lake", 47.80, 16.75, 40, 1866, 1871, "dried",
     "The shallow steppe lake has dried up several times in the record; the last time, from 1866 "
     "to 1871, it was ploughed and sown with wheat.", "recorded"),
    ("Copais", "lake", 38.45, 23.05, 35, 1880, 1930, "drained",
     "The Boeotian lake that swallowed the Minyan cities of Orchomenus was drained for cotton and "
     "tobacco by a Scottish company.", "recorded"),
    ("Lake Karla", "lake", 39.50, 22.75, 30, 1962, None, "drained",
     "Thessaly's lake was drained in 1962 for farmland; it is being refilled now, at great cost.",
     "recorded"),
    ("Lake Kerkini", "lake", 41.20, 23.10, 30, 1932, None, "dammed",
     "The Strymon was dammed at Lithotopos to make a reservoir in the plain of Serres, which has "
     "since become one of the great bird lakes of Europe.", "recorded"),
    ("Thermopylae", "coast", 38.80, 22.55, 15, -480, None, "advanced",
     "The Spercheios has carried the shore out more than two kilometres since Leonidas held the "
     "pass; the hot gates are a plain now, and the sea is far away.", "estimated"),
    ("Pontine Marshes", "marsh", 41.45, 12.90, 60, 1928, 1939, "drained",
     "The marshes south of Rome, malarial and empty since antiquity, were drained and settled "
     "under Mussolini; Littoria and Sabaudia were built on them.", "recorded"),
    ("Lake Fucino", "lake", 41.98, 13.55, 30, 1854, 1875, "drained",
     "The largest lake of the Apennines, which the Emperor Claudius had tried to drain through a "
     "tunnel three miles long, was finally emptied by Prince Torlonia, and its bed became the "
     "most productive land in Italy.", "recorded"),
    ("Po, the Ficarolo breach", "river", 44.95, 11.44, 100, 1152, None, "course",
     "The Po broke its bank at Ficarolo and left its old channel through Ferrara; the Po di "
     "Volano became a backwater and the delta began to build east.", "recorded"),
    ("Venice lagoon, the Brenta diverted", "river", 45.30, 12.05, 60, 1507, None, "diverted",
     "Venice turned the Brenta out of the lagoon to stop it silting the city up, and the river "
     "that had made Venice was made to go round it.", "recorded"),
    ("Ebro delta", "delta", 40.75, 0.80, 50, 1300, None, "advanced",
     "Deforestation in the Ebro basin sent the river's silt down and pushed the delta out into "
     "the Mediterranean; most of it is younger than the Black Death.", "estimated"),
    ("Camargue and the Rhone delta", "delta", 43.50, 4.50, 70, 1, None, "advanced",
     "The Rhone's delta has built seaward since Roman times; the Rhone's own mouth has moved, and "
     "the Camargue was a Roman vineyard before it was a marsh.", "estimated"),
    ("Danube delta, the Sulina arm", "river", 45.15, 29.65, 80, 1862, None, "course",
     "The European Commission of the Danube straightened and cut the Sulina arm to make a "
     "navigable channel to the Black Sea, and the delta's other arms starved.", "recorded"),
    ("Tanais", "coast", 47.27, 39.30, 40, 200, 400, "silted",
     "The Greek colony at the mouth of the Don, where the nomads and the Mediterranean traded, "
     "silted up and was abandoned; the Don's delta moved on without it.", "estimated"),

    # ---------------------------------------------------------------- Americas ----
    ("Lake Texcoco", "lake", 19.45, -99.05, 60, 1325, None, "flooded",
     "The Mexica built Tenochtitlan on an island in the shallowest of the five lakes of the "
     "Valley of Mexico; the city's whole shape, its canals and its chinampas, is the shape of "
     "that lake.", "recorded"),
    ("Tenochtitlan, the drainage begins", "lake", 19.45, -99.05, 70, 1607, 1789, "drained",
     "After the floods of 1604 and 1607 the Spanish cut the Nochistongo outlet through the hills "
     "to the north to let the lakes out; the work took nearly two centuries and drained the "
     "valley of Mexico City, which has been sinking into the old lake bed ever since.", "recorded"),
    ("Chinampas of Xochimilco", "marsh", 19.27, -99.10, 25, 1000, None, "reclaimed",
     "The floating gardens: strips of reed and mud staked into the shallow lake, the most "
     "productive farming in Mesoamerica, and the only part of the lake system that survives.",
     "estimated"),
    ("Salton Sea", "lake", 33.30, -115.90, 60, 1905, 1907, "flooded",
     "The Colorado broke through an irrigation headgate in 1905 and ran into the Salton Sink for "
     "two years, making California's largest lake out of a mistake.", "recorded"),
    ("Colorado delta", "delta", 31.70, -114.70, 90, 1935, None, "retreated",
     "Hoover Dam and the ones above it took the river's water and its silt; the delta, which was "
     "a green maze of channels and lagoons, is a salt flat.", "recorded"),
    ("Lake Mead", "lake", 36.20, -114.40, 90, 1936, None, "dammed",
     "Hoover Dam closed in 1935 and Lake Mead, the largest reservoir in the United States, filled "
     "by 1936; St Thomas, Nevada, was drowned under it.", "recorded"),
    ("Lake Powell", "lake", 37.00, -111.30, 100, 1963, 1980, "dammed",
     "Glen Canyon Dam closed in 1963 and the reservoir filled for seventeen years, drowning Glen "
     "Canyon and its hundred side canyons.", "recorded"),
    ("Owens Lake", "lake", 36.40, -117.90, 40, 1913, 1926, "dried",
     "Los Angeles took the Owens River by aqueduct in 1913 and the lake was dry by 1926; the dust "
     "from its bed is the worst particulate air pollution in America.", "recorded"),
    ("Tulare Lake", "lake", 36.00, -119.70, 60, 1850, 1900, "drained",
     "Once the largest freshwater lake west of the Mississippi, it was drained for cotton and "
     "wheat and is now a farmed basin that floods only in the wettest years.", "recorded"),
    ("Everglades", "marsh", 26.00, -80.80, 150, 1882, 1928, "drained",
     "From 1882, and in earnest after 1905, canals cut the great sawgrass marsh of south Florida "
     "and half of it was turned into sugar fields and suburbs.", "recorded"),
    ("Chicago, the river reversed", "river", 41.80, -87.70, 40, 1900, None, "diverted",
     "The Sanitary and Ship Canal opened in January 1900 and turned the Chicago River away from "
     "Lake Michigan into the Mississippi watershed, so as to stop the city drinking its own "
     "sewage.", "recorded"),
    ("Mississippi, the Atchafalaya", "river", 31.00, -91.70, 100, 1542, None, "course",
     "The Atchafalaya has been trying to capture the Mississippi since before the French came; "
     "only the Old River Control Structure, finished in 1963, keeps the river going past Baton "
     "Rouge and New Orleans instead of to Morgan City.", "estimated"),
    ("Mississippi delta", "delta", 29.20, -89.30, 120, 1930, None, "retreated",
     "Levees that stop the river flooding also stop it building, and the delta's wetlands have "
     "been turning to open water at the rate of a football field an hour.", "recorded"),
    ("New Orleans", "coast", 29.95, -90.07, 40, 1718, None, "subsided",
     "The city was founded in 1718 on a natural levee a metre or two above the sea; drained "
     "marsh behind it has since sunk below it, and levees hold the water out on every side.",
     "recorded"),
    ("Lake Poopo", "lake", -18.70, -67.00, 60, 2015, None, "dried",
     "Bolivia's second largest lake, shallow and salty, was gone by December 2015; the Uru-Murato "
     "who fished it moved away.", "recorded"),
    ("Itaipu", "lake", -25.40, -54.60, 120, 1982, 1984, "dammed",
     "The dam on the Parana filled in October 1982 and drowned the Sete Quedas falls, the largest "
     "waterfall by volume on earth, under a lake 170 kilometres long.", "recorded"),
    ("Panama, Gatun Lake", "lake", 9.20, -79.90, 60, 1913, None, "dammed",
     "The Chagres was dammed at Gatun and the valley flooded to make the lake that carries ships "
     "across the isthmus; the canal opened in August 1914.", "recorded"),

    # ---------------------------------------------------- canals, tanks and anicuts ----
    ("Han Gou canal", "canal", 32.40, 119.45, 80, -486, None, "opened",
     "Fuchai of Wu cut a canal from the Yangtze to the Huai to move his army north, the first "
     "reach of what would become the Grand Canal.", "recorded"),
    ("Canal of the Pharaohs", "canal", 30.30, 32.35, 100, -500, None, "opened",
     "Darius I finished the canal from the Nile at Bubastis to the Red Sea, so that ships could "
     "sail from Egypt to Persia. Trajan reopened it; Amr ibn al-As reopened it again in 641 to "
     "carry grain to Arabia; al-Mansur closed it in 767, and it has been dry since.", "recorded"),
    ("Dujiangyan", "works", 31.00, 103.60, 60, -256, None, "diverted",
     "Li Bing cut the Min River at the neck of a mountain and split it between a channel for "
     "irrigation and one for flood, without a dam. It still waters half a million hectares of "
     "Sichuan, two thousand two hundred years later.", "recorded"),
    ("Zhengguo Canal", "canal", 34.50, 109.00, 100, -246, None, "opened",
     "The Qin dug a canal from the Jing to the Luo to irrigate the Guanzhong plain: meant to "
     "exhaust them, it fed them instead, and the plain that fed Qin fed the army that took China.",
     "recorded"),
    ("Lingqu Canal", "canal", 25.60, 110.70, 50, -214, None, "opened",
     "The Qin cut two miles of canal to join the Xiang to the Li, and with them the Yangtze to "
     "the Pearl River, so that the army could be supplied on its way south.", "recorded"),
    ("Grand Anicut, Kallanai", "works", 10.83, 78.82, 60, 150, None, "diverted",
     "Karikala Chola built a dam of uncut stone across the Kaveri and turned the river into the "
     "channels of the Tanjore delta. It is the oldest barrage still working, and the delta is "
     "the rice country of Tamil Nadu because of it.", "estimated"),
    ("Angkor, the East Baray", "works", 13.45, 103.92, 20, 900, None, "dammed",
     "Yasovarman I made a reservoir seven kilometres long to hold the monsoon for the dry "
     "months; it was the first of the great tanks that held the city.", "estimated"),
    ("Angkor, the West Baray", "works", 13.44, 103.80, 25, 1050, None, "dammed",
     "Udayadityavarman II made a greater one, eight kilometres by two, with a temple on an "
     "island in the middle. Between them they watered a city of three quarters of a million "
     "people.", "estimated"),
    ("Hussain Sagar", "lake", 17.42, 78.47, 15, 1563, None, "dammed",
     "Ibrahim Quli Qutb Shah built the tank on the Musi that gave Hyderabad its name city of "
     "Hussain, and its water, for four centuries.", "recorded"),
    ("Upper Anicut, Kaveri", "works", 10.87, 78.48, 40, 1836, None, "diverted",
     "Arthur Cotton built the Upper Anicut at the head of the delta to settle which branch of "
     "the Kaveri should carry the flood, and the delta stopped fighting over it.", "recorded"),
    ("Godavari anicut", "works", 16.95, 81.78, 80, 1852, None, "diverted",
     "Cotton's anicut at Dowleswaram, four kilometres of masonry across the Godavari, turned "
     "the delta of the Godavari from a famine country into the granary it is.", "recorded"),
    ("Krishna anicut", "works", 16.50, 80.62, 70, 1855, None, "diverted",
     "The anicut at Vijayawada took the Krishna into the canals of the coastal delta.",
     "recorded"),
    ("Upper Ganga Canal", "canal", 29.95, 78.16, 150, 1854, None, "opened",
     "Proby Cautley took the Ganges out at Haridwar and carried it five hundred kilometres "
     "across the Doab; the canal and its branches made the western districts of the United "
     "Provinces the most irrigated land in India.", "recorded"),
    ("Agra Canal", "canal", 28.30, 77.50, 100, 1874, None, "opened",
     "The canal from Okhla on the Yamuna, built to carry food to a province that had just been "
     "famine, and opened the year before the great famine came.", "recorded"),
    ("Lower Chenab Canal", "canal", 31.50, 73.00, 120, 1892, None, "opened",
     "The first of the Punjab canal colonies: the Chenab was taken out of its bed into a desert "
     "doab, and a million people were settled on land that had grazed camels.", "recorded"),
    ("Musi flood of 1908", "river", 17.37, 78.49, 30, 1908, None, "flooded",
     "On 28 September 1908 the Musi rose nearly four metres in a few hours and took a third of "
     "Hyderabad with it. The twin reservoirs that were built after it, Osman Sagar in 1920 and "
     "Himayat Sagar in 1927, still hold the city's water.", "recorded"),

    # ------------------------------------------- the older world, before the modern record ----
    ("Spina and the Po delta", "coast", 44.70, 12.20, 40, -500, -200, "silted",
     "Spina was the port where the Greeks of the Adriatic met the Etruscans of the Po, on a "
     "lagoon at the river's mouth. The Po silted it in and the town was gone by the time Rome "
     "came north.", "estimated"),
    ("Ostia and the Tiber mouth", "coast", 41.75, 12.28, 25, -300, 500, "advanced",
     "The Tiber has carried its mouth seaward some four kilometres since Rome was founded; "
     "Ostia is inland, and Claudius's great harbour at Portus silted up within four centuries "
     "of being dug.", "estimated"),
    ("Classe, the port of Ravenna", "coast", 44.40, 12.20, 25, -27, 800, "silted",
     "Augustus built the fleet harbour of Classe on the Adriatic; the Po's silt filled it, and "
     "by the ninth century Ravenna had no port at all.", "estimated"),
    ("Troy's plain", "coast", 39.95, 26.20, 25, -1180, None, "advanced",
     "The Scamander and the Simois have filled the bay of Troy; Hisarlik, whose ships the "
     "Achaeans beached below, stands five kilometres from the sea.", "estimated"),
    ("Babylon and the Euphrates", "river", 32.54, 44.42, 50, -1750, 100, "course",
     "The Euphrates has moved west across its plain; the course that ran through Babylon when "
     "Hammurabi was king is not the one that runs past the ruins now.", "estimated"),
    ("Memphis and the Nile", "river", 29.85, 31.26, 50, -2500, 641, "course",
     "The Nile has worked east across the valley since the Old Kingdom, and Memphis's harbour "
     "quarter, the 'Balance of the Two Lands', was left on dry ground long before the Arabs "
     "founded Fustat.", "estimated"),
    ("Mohenjo-daro and the Indus", "river", 27.32, 68.14, 50, -2600, -1900, "course",
     "The city was built on the silt the Indus left, rebuilt on silt again after every flood, "
     "and at last abandoned; the river has since moved east of it.", "estimated"),
    ("Debal and the Indus delta", "coast", 24.75, 67.50, 70, 700, 1300, "course",
     "Debal, the port where the Arab armies landed in 711, was left high as the Indus built its "
     "delta westward; Banbhore is four kilometres from the sea it once commanded.", "estimated"),
    ("Uzboy, the Amu to the Caspian", "river", 41.00, 58.00, 200, -3000, 1600, "dried",
     "For much of antiquity the Amu Darya ran west across the Kara Kum by the Uzboy channel "
     "into the Caspian, past the walls of Khorezm, and not to the Aral at all. When it turned "
     "north, the oases of the old channel died.", "estimated"),
    ("Beemster", "lake", 52.55, 4.93, 20, 1612, None, "reclaimed",
     "The first great Dutch polder: a lake pumped dry by forty-three windmills, and the "
     "speculators who paid for it were given farmland better than any in Holland.", "recorded"),
    ("Schermer", "lake", 52.60, 4.68, 20, 1633, None, "reclaimed",
     "North Holland's last big lake to be drained by windmill, and the biggest: forty-eight "
     "square kilometres.", "recorded"),
    ("Lake Biwa Canal", "canal", 35.00, 135.85, 40, 1890, None, "opened",
     "The canal from Lake Biwa to Kyoto, with Japan's first hydroelectric tramway on it, "
     "finished in 1890.", "recorded"),
    ("Nile Delta Barrage", "works", 30.18, 31.12, 80, 1861, None, "dammed",
     "Mougel Bey's barrage at the apex of the delta, the first attempt to hold the Nile's flood "
     "back and let it out again at will, and the ancestor of every dam on the river.",
     "recorded"),

    # ------------------------------------- the towns the mod's own test places stand on ----
    ("Pataliputra and the Son", "river", 25.61, 85.14, 70, -300, None, "course",
     "Pataliputra was founded where the Son met the Ganges, and the confluence has moved; the "
     "rivers that made the Mauryan capital a port are not where Mauryan Pataliputra stood.",
     "estimated"),
    ("Nahrawan Canal", "canal", 33.60, 44.60, 120, -300, 1258, "opened",
     "The great canal that took the Tigris out across the plain east of Baghdad, feeding the "
     "fields of the Sasanian and Abbasid capitals; neglected after the tenth century, it was "
     "cut for good by the Mongols, and that countryside went back to steppe.", "estimated"),
    ("Vijayanagara's tanks and channels", "works", 15.33, 76.46, 40, 1350, 1565, "dammed",
     "The capital of the last Hindu empire of the Deccan stood on the Tungabhadra in a bowl of "
     "rock; its kings dammed the river into channels and tanks, and watered a city of half a "
     "million in a land that gets its rain in four months.", "estimated"),
    ("Timbuktu and the Niger", "river", 16.77, -3.01, 40, 1100, None, "course",
     "Timbuktu was founded on a channel of the Niger; the river moved away, and for centuries "
     "the city was joined to its own port at Kabara by a canal that had to be dug out after "
     "every dry season and at last silted for good.", "estimated"),
    ("Hauz Khas", "lake", 28.55, 77.19, 15, 1300, None, "dammed",
     "Alauddin Khalji's tank for the new city of Siri, one of the thousands of tanks and "
     "stepwells that make Delhi's water. It held the city through sieves of drought and was "
     "deserted when the empire moved on.", "estimated"),
    ("Edo, the Hibiya inlet", "coast", 35.68, 139.75, 20, 1590, 1640, "reclaimed",
     "When Ieyasu came to Edo, the sea ran in to Hibiya where the Imperial Palace gardens are; "
     "the inlet was filled in and the castle wards laid out on it, and the city grew outward "
     "into the bay from there.", "recorded"),
    ("Western Yamuna Canal", "canal", 29.70, 77.05, 150, 1817, None, "opened",
     "The British rebuilt a channel the Delhi sultans and the Mughals had cut and abandoned, and "
     "brought the Yamuna back to the land between the rivers: three hundred kilometres of canal "
     "and the end of the region's worst famines.", "recorded"),
    ("London, the Fleet", "river", 51.52, -0.11, 15, 1300, 1737, "silted",
     "The Fleet, the Walbrook and the Tyburn ran open through London; by the eighteenth century "
     "they were sewers and were roofed over, so that the rivers of London became the streets "
     "above them.", "estimated"),
    ("London, the Thames embanked", "river", 51.51, -0.12, 20, 1862, 1874, "reclaimed",
     "Bazalgette's embankments took the tidal mud of the Thames and made it into the Victoria "
     "Embankment, narrowing the river by a third and putting London's sewage in a pipe instead "
     "of the tide.", "recorded"),
    ("Canal de l'Ourcq", "canal", 48.93, 2.39, 60, 1822, None, "opened",
     "Paris brought the Ourcq in from a hundred kilometres away to water its streets, fill its "
     "fountains and flush its gutters, which until then ran down the middle of the road.",
     "recorded"),
    ("Collect Pond", "lake", 40.72, -74.00, 5, 1811, None, "drained",
     "The pond that was New York's fresh water for two centuries, then its tanners' sink, was "
     "filled in 1811; the ground has been sinking ever since, and the Tombs prison was built on "
     "it.", "recorded"),
    ("Moscow Canal", "canal", 56.10, 37.20, 90, 1937, None, "opened",
     "The canal from the Volga to the Moskva, opened in 1937 and built by convict labour, that "
     "made Moscow a port of five seas and drowned villages and a monastery to do it.",
     "recorded"),
    ("Sydney's Tank Stream", "river", -33.86, 151.21, 10, 1788, 1850, "silted",
     "The stream the first fleet settled beside, and Sydney's only fresh water for forty years; "
     "it was an open sewer by 1826 and was built over within the century.", "recorded"),
    ("Cahokia and the American Bottom", "river", 38.66, -90.06, 50, 800, 1400, "course",
     "Cahokia stood on the floodplain the Mississippi had abandoned, among oxbow lakes and "
     "cypress swales full of fish; the river's channels kept moving, and the city's fields and "
     "its fish traps went with them.", "estimated"),

    # -------------------------------------------------- the changes before the world ----
    ("Doggerland", "coast", 54.50, 2.50, 250, -6500, None, "flooded",
     "The land that joined Britain to the Continent: forest, marsh and Mesolithic camps, drowned "
     "by the Storegga slide and the rising sea long before this world begins. It is under the "
     "North Sea now, and trawlers bring up its antlers.", "estimated"),
    ("Beringia", "strait", 65.50, -169.00, 300, -11000, None, "flooded",
     "The land bridge between Asia and America, and the road the first Americans took. The sea "
     "closed it around 11,000 years ago, before this world begins.", "estimated"),
    ("The Black Sea flood", "sea", 43.00, 34.00, 300, -5600, None, "flooded",
     "The Mediterranean broke into the fresh lake that the Black Sea then was, in a few months or "
     "a few years, and the farmers of its shore were scattered into Europe. When it happened, and "
     "whether it happened as the story tells it, are still argued. It is done before this world "
     "begins.", "estimated"),
    ("Sundaland", "coast", -1.00, 110.00, 400, -10000, None, "flooded",
     "The exposed shelf that joined Borneo, Java and Sumatra to the Malay peninsula through the "
     "ice age, drowned as the sea rose. Before this world begins.", "estimated"),
    ("The Baltic, the Ancylus and the Littorina", "sea", 57.00, 19.00, 300, -7000, -2000,
     "flooded",
     "The Baltic was a lake, then a fresh sea, then the salt Littorina Sea of the Bronze Age, as "
     "the ice melted and the land rose and the straits opened and closed. Salty enough for cod by "
     "2000 BCE; emptying of salt since.", "estimated"),
    ("Mega-Chad", "lake", 15.00, 17.00, 400, -3000, -1000, "shrank",
     "A lake of 330,000 square kilometres, bigger than the Caspian, in the middle of the Sahara "
     "when the world begins; the African humid period ends, and it shrinks towards the Chad we "
     "know.", "estimated"),
    ("The Green Sahara", "coast", 25.00, 12.00, 900, -3000, -1000, "dried",
     "The Sahara of 3000 BCE had rivers, lakes, giraffes and cattle herders where there is now "
     "sand. The monsoon retreated and the desert came back, and the people went to the Nile.",
     "estimated"),
]
