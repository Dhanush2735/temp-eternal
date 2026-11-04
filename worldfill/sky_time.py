#!/usr/bin/env python3
"""Julian Day Numbers and the two calendars, for step 35 (B22, B23).

Why this file exists: NASA's eclipse catalogues date their eclipses in the **Julian calendar**
before 1582 Oct 04 and the **Gregorian** after 1582 Oct 15, while the mod's `KnowledgeDate` is
**proleptic Gregorian** for every year, including the ones before there was a Gregorian calendar.
So an eclipse that history books date "20 September 331 BCE" -- the one before Gaugamela, which is
in NASA's table as year -330, month 9, day 20 -- has to be moved five days to be put on the mod's
calendar. Getting this wrong by ten days is how a mod tells a player an eclipse fell on a day it
did not.

Everything here is the standard algorithm (Meeus, *Astronomical Algorithms*, chapters 1 and 7):
the Julian Day Number of a calendar date, and back. Years are **astronomical** throughout -- 1 BCE
is 0, 331 BCE is -330 -- which is what both NASA's tables and `KnowledgeDate` use.

Self-test: `python3 sky_time.py`.
"""
import math


def jdn_from_gregorian(year, month, day):
    """Julian Day Number at 0h UT of a proleptic Gregorian date. Years are astronomical."""
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    return (day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045)


def jdn_from_julian(year, month, day):
    """Julian Day Number at 0h UT of a proleptic Julian date. Years are astronomical."""
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    return day + (153 * m + 2) // 5 + 365 * y + y // 4 - 32083


def gregorian_from_jdn(jdn):
    """(year, month, day) in the proleptic Gregorian calendar, astronomical year."""
    a = jdn + 32044
    b = (4 * a + 3) // 146097
    c = a - 146097 * b // 4
    d = (4 * c + 3) // 1461
    e = c - 1461 * d // 4
    m = (5 * e + 2) // 153
    day = e - (153 * m + 2) // 5 + 1
    month = m + 3 - 12 * (m // 10)
    year = 100 * b + d - 4800 + m // 10
    return year, month, day


def julian_from_jdn(jdn):
    """(year, month, day) in the proleptic Julian calendar, astronomical year."""
    c = jdn + 32082
    d = (4 * c + 3) // 1461
    e = c - 1461 * d // 4
    m = (5 * e + 2) // 153
    day = e - (153 * m + 2) // 5 + 1
    month = m + 3 - 12 * (m // 10)
    year = d - 4800 + m // 10
    return year, month, day


def nasa_to_mod(year, month, day):
    """NASA's eclipse-catalogue date -> the mod's proleptic Gregorian date.

    NASA uses the Julian calendar up to 1582 Oct 04 and the Gregorian from 1582 Oct 15; the ten
    days in between do not exist. The mod uses proleptic Gregorian everywhere, so a date before
    1582 is read as Julian and converted.
    """
    key = year * 10000 + month * 100 + day
    if key < 15821004:
        jdn = jdn_from_julian(year, month, day)
    else:
        jdn = jdn_from_gregorian(year, month, day)
    return gregorian_from_jdn(jdn)


# ---------------------------------------------------------------------------
# what the sky does with a date: where the Sun is, and how long the day is
# ---------------------------------------------------------------------------

def julian_day(year, month, day, hour=0.0):
    """Julian Day (with fraction) from a proleptic Gregorian date and UT hour."""
    return jdn_from_gregorian(year, month, day) + (hour - 12.0) / 24.0


def solar_longitude(jd):
    """Apparent longitude of the Sun, degrees, from a Julian Day (low precision, +-0.01 deg).

    Meeus ch. 25, abridged: good enough to place the seasons and the solstices in a game.
    """
    t = (jd - 2451545.0) / 36525.0
    m = math.radians(357.52910 + 35999.05030 * t - 0.0001559 * t * t - 0.00000048 * t ** 3)
    c = (1.914600 - 0.004817 * t - 0.000014 * t * t) * math.sin(m) \
        + (0.019993 - 0.000101 * t) * math.sin(2 * m) \
        + 0.000290 * math.sin(3 * m)
    return (280.46645 + 35999.37270 * t - 0.000005 * t * t + c) % 360.0


def declination_of_sun(jd):
    """Solar declination in degrees -- what makes summer and winter."""
    lam = math.radians(solar_longitude(jd))
    eps = math.radians(obliquity(jd))
    return math.degrees(math.asin(math.sin(eps) * math.sin(lam)))


def obliquity(jd):
    """The tilt of the Earth's axis, degrees, for a Julian Day."""
    t = (jd - 2451545.0) / 36525.0
    return 23.43929111 - 0.013004167 * t - 0.0000001639 * t * t + 0.0000005036 * t ** 3


SUNRISE_ALTITUDE = -0.833      # degrees: the upper limb touching the horizon, with refraction.
                               # This is what an almanac means by sunrise, and it is why the
                               # equinox gives 12h07m of daylight rather than 12h00m.


def day_length_hours(lat, jd):
    """Hours of daylight at a latitude on a Julian Day. 24 at midnight sun, 0 in polar night."""
    dec = math.radians(declination_of_sun(jd))
    latr = math.radians(lat)
    alt = math.radians(SUNRISE_ALTITUDE)
    cos_h = (math.sin(alt) - math.sin(latr) * math.sin(dec)) / (math.cos(latr) * math.cos(dec))
    if cos_h <= -1.0:
        return 24.0            # the Sun never sets
    if cos_h >= 1.0:
        return 0.0             # the Sun never rises
    return 2.0 * math.degrees(math.acos(cos_h)) / 15.0


def moon_phase(jd):
    """The Moon's phase as 0..1: 0 new, 0.25 first quarter, 0.5 full, 0.75 last quarter.

    Uses the mean synodic month from a known new moon. Over 12,000 years the mean error reaches
    a day or so, which the register states rather than hides: this is the phase, not an almanac.
    """
    synodic = 29.530588861
    known_new = 2451549.9      # 2000 Jan 06 14:20 UT, the new moon NASA numbers lunations from
    return ((jd - known_new) / synodic) % 1.0


def moon_age_days(jd):
    """Days since the last new moon."""
    return moon_phase(jd) * 29.530588861


if __name__ == "__main__":
    ok = True

    def check(got, want, what):
        global ok
        good = got == want
        ok = ok and good
        print("%s  %-58s got %s want %s" % ("OK  " if good else "FAIL", what, got, want))

    # the anchors of the whole scheme
    check(jdn_from_gregorian(2000, 1, 1), 2451545, "JDN of 2000 Jan 1 (JD 2451545.0 is noon on it; J2000.0 the epoch)")
    check(jdn_from_gregorian(1582, 10, 15), 2299161, "JDN of the first Gregorian day")
    check(jdn_from_julian(1582, 10, 4), 2299160, "JDN of the last Julian day")
    check(jdn_from_gregorian(-330, 9, 15), jdn_from_julian(-330, 9, 20),
          "the Gaugamela eclipse: Julian 20 Sep = Gregorian 15 Sep")
    check(gregorian_from_jdn(jdn_from_gregorian(-4712, 1, 1)), (-4712, 1, 1),
          "Gregorian round trip at the start of the Julian period")
    check(julian_from_jdn(jdn_from_gregorian(1582, 10, 15)), (1582, 10, 5),
          "Gregorian 15 Oct 1582 is Julian 5 Oct 1582")
    check(nasa_to_mod(-330, 9, 20), (-330, 9, 15), "NASA -> mod for the Gaugamela eclipse")
    check(nasa_to_mod(1504, 3, 1), (1504, 3, 11), "NASA -> mod for Columbus's eclipse")
    check(nasa_to_mod(1919, 5, 29), (1919, 5, 29), "dates after 1582 move not at all")

    # the Sun and the day
    # Published values: 12h07m at the equator on the equinox; London's longest day is 16h38m and
    # its shortest 7h50m. The residual minute is the low-precision solar longitude (+-0.01 deg).
    check(round(day_length_hours(0.0, julian_day(2000, 3, 20)), 2), 12.11,
          "day length at the equator on the equinox (12h07m)")
    check(round(day_length_hours(51.5, julian_day(2000, 6, 21)), 2), 16.64,
          "day length in London at the June solstice (16h38m)")
    check(round(day_length_hours(51.5, julian_day(2000, 12, 21)), 2), 7.83,
          "day length in London at the December solstice (7h50m)")
    check(day_length_hours(78.0, julian_day(2000, 6, 21)), 24.0, "midnight sun in Svalbard")
    check(day_length_hours(78.0, julian_day(2000, 12, 21)), 0.0, "polar night in Svalbard")
    check(round(declination_of_sun(julian_day(2000, 6, 21)), 1), 23.4,
          "solar declination at the June solstice")
    check(round(moon_age_days(2451549.9), 1), 0.0, "moon age at the reference new moon")

    print("\nall checks passed" if ok else "\nFAILURES")
    raise SystemExit(0 if ok else 1)
