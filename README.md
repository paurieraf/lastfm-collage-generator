![](https://img.shields.io/pypi/dm/lastfmcollagegenerator?)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# lastfm-collage-generator

Python library to create Last.fm collages from user's top albums. 

It supports different configurations like the grid size or the period.


## Features

- Choose the number of rows and columns (for now, up to 5)
- Choose the period to calculate the top (7day, 1month, 3month, 6month, 12month, overall. Default: 7day)
  
## Installation

Install lastfmcollagegenerator with pip

```bash
  pip install lastfmcollagegenerator
```

## Options

Entity values
```
"album", "artist", "track"
```
Period values
```
"7day", "1month", "3month", "6month", "12month", "overall"
```


## Usage/Examples

```python
from lastfmcollagegenerator.collage_generator import CollageGenerator

collage_generator = CollageGenerator(lastfm_api_key="YOUR_API_KEY", lastfm_api_secret="YOUR_API_SECRET")

# Returns a PIL Image object
image = collage_generator.generate(entity="album", username="username", cols=5, rows=5, period="7day")
image.save("5x5 album collage.png", "png")

# Or just call the method directly
image = collage_generator.generate_top_albums_collage(username="username", cols=5, rows=5, period="7day")
image.save("5x5 album collage.png", "png")
```

  
## License

[MIT](https://choosealicense.com/licenses/mit/)

  
## Authors

- [@paurieraf](https://www.github.com/paurieraf)

