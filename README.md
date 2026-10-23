# Tamagotchi Paradise Genes Generator

Preview any body, eyes and colour combination for Tamagotchi Paradise characters, then keep track of the ones you raise.

**Live site:** https://iceomort.github.io/tamaparageneratorv2/

## What it does

**Generator.** Pick a body, eyes and colour, and the preview updates straight away. Each picker has its own randomise button, and Randomise all rerolls all three. Preview all shows every option with your other selections applied. Match copies the character from the other card, which covers the common case where no complicated breeding is involved.

**Filters.** Choose which biomes appear: Jade Forest, Land, Water, Sky, Ice and Tropics. Optional toggles include non-adult bodies, Lab Tama bodies and Lab Tama eyes. You may need to remake your selections after changing filters.

**Growth instructions.** Click any history item to see point-form steps for raising that combination (breeding, field, food, care), based on the official Tamagotchi Paradise growth charts. If body, eyes and colour all come from the same character, it tells you to hatch a new egg instead.

**History and Favourites.** History logs every generated combination, and re-picked combinations move to the top. Favourite a character with the heart button and rename it (for example, "Henry the LEOPATCHI").

**Memories.** Save a tama you are raising with its date of birth, optional death date and an age counter (1 Tama Year = 1 real day). Each memory has:

- a diary, with entries added through a pop-up, editable later, with an optional photo and a mood icon
- free-text tags, with colours assigned by the app
- reordering with move up and down
- a clean report card view in Pastel, Night or Paper themes, with JPG export of either the newest three diary entries or the full diary

**Sync.** Sign in with Google to sync History, Favourites and Memories across devices (Firebase Auth and Firestore). Without signing in, data stays in the current browser only.

## Running locally

The site is a single static `index.html` with no build step. Open the file in a browser, or serve the folder:

```sh
python3 -m http.server 8000
```

Then visit `http://localhost:8000`.

## Deploying

The site is hosted on GitHub Pages from the `main` branch. To publish a change, replace `index.html`, then:

```sh
git add .
git commit -m "Describe the change"
git push
```

## Data source

The app is driven by `data.json`, which holds character and palette definitions.

### Characters

`Characters` is a list of character definitions:

- `Name`: name of the character
- `Id`: ID as found in game data. Lab Tama characters have no real ID, so they start at `60100` and run sequentially in the order given to the data generator.
- `Stage`: `5` is adult; anything lower is not breedable
- `IsJade`: Jade Forest-exclusive
- `IsExternal`: from Lab Tama
- `EyePos`: `[x, y]` of the eye sprite relative to the top left of the body sprite. All eye sprites must share the same dimensions.
- `MouthPos`: `[x, y]` of the mouth sprite relative to the top left of the body sprite. All mouth sprites must share the same dimensions.

Sprites live in `images/` as `{Id}_{type}.png`, where type is `body`, `eyes` or `mouth`. Sprites must be palette-indexed.

### Palettes

`Palettes` is a list of colour definitions:

- `Name`: name of the colour
- `Colors`: R/G/B/A values flattened in the order returned by Pillow's `Image.getpalette()`, 8 * 4 elements. These replace the body and mouth sprite palettes from the start. Other lengths are not enforced but may render oddly.

`Original` has no `Colors`, so the sprite's own palette is kept.

## Credits

Character data and field mappings are from the Tamagotchi Paradise wiki. Tamagotchi is a trademark of Bandai; this is an unofficial fan project.
