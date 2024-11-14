# Former-Searcher

Searches for minimum/maximum solutions to games of [former](https://www.nrk.no/former).

## Usage
```
python search.py
```

## Configuration
Edit the bottom of `search.py` to read a file containing `G`, `B`, `O`, `P` in a grid, e.g.

```
GBGOOOG
BGGPPBG
BPGPBOB
PPBPBGG
OBPGOBO
BOBOBBB
BOPOGBO
OOGGGGO
OOPGOBB
```

To change between maximum and minimum, change the name of the function being called.

To change other options, just read the function signature and change them.