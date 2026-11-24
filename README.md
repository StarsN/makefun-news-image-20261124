[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/StarsN/makefun-news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/StarsN/makefun-news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
# The World in One Picture — 24 November 2026

[![make.fun](https://img.shields.io/badge/make.fun-news--image--20261124-blue)](https://make.fun/c/news-image-20261124)
[![Python](https://img.shields.io/badge/python-3%20%E2%80%A2%20stdlib%20only-green)](https://make.fun/c/news-image-20261124)

An entry for the make.fun bounty [news-image-20261124](https://make.fun/c/news-image-20261124):
sum up 24 November's world news in one image.

## What it does

`main.py` draws a 1024×1024 newspaper front page — "The Otter Times" —
entirely at runtime, using only the Python 3 standard library. No images,
no network access, no files read at runtime. The page is built from
scratch: a hand-designed 5×8 bitmap font, small hand-drawn pictures for
each story (a GPU chip, a drone, a capitol dome, a sealed document, city
buildings, a factory, a rising bar chart), and a minimal PNG encoder
written in the same file.

The output is deterministic: run it twice and the PNG bytes are
identical.

## How to run

```sh
python3 main.py
```

That writes `out/entry.png`. To choose another folder:

```sh
MAKEFUN_OUTPUT_DIR=/path/to/dir python3 main.py
```

## The day's stories

As reported on Tuesday, 24 November 2026:

- **Headline — Nvidia:** Jensen Huang returns as chief executive 11 days
  after quitting; shares rise 31% and the Nasdaq climbs 6.5%.
- **Mexico:** a US surveillance drone helped track "El Chapo Isidro" in
  Sinaloa; his capture set off clashes leaving 20 dead.
- **USA:** Rep. Jimmy Gomez resigns effective 1 December after a House
  Ethics report found substantial evidence of sexual misconduct toward a
  staffer.
- **China:** an official surnamed Ma is sentenced to death for leaking 35
  state secrets to a foreign agency for more than $150,000.
- **Sudan:** drone strikes hit homes and the UN building in Khartoum early
  on Tuesday.
- **Indonesia:** more remains are recovered from the Cikande candy factory
  fire; the search continues for 34 missing workers.
- **Japan:** factory activity grows faster in November, flash PMI 53.7, on
  chip demand.
- **Also today:** FIFA confirms the US will co-host the 2031 Women's World
  Cup (the UK gets 2035); the WFP warns wars threaten food aid for 7.3m
  more people; Trump orders executions to be expedited; Virginia and
  Oregon sue SpaceX over Grok deepfakes.

Sources: Reuters, AFP, Associated Press, CNN, The Manila Times.

## License

MIT — see [LICENSE](LICENSE).
