## Installation
PS4 Remote Play app needed for PS4 scraper.
```
https://remoteplay.dl.playstation.net/remoteplay/lang/en/index.html
```
Imports
```
$ pip install -r requirements.txt
```

## Overview

Written and updated from 2018 - 2020

- Connects to a PS4 via the Remote Play app.
- Saves image files of storefront using internal filename conventions.
- Checks for new / already-active ads using image hashing comparisons.
- Uses command line arguments to perform a scrape run, or ad-hoc execution of image de-duper / exclusivity checker functions.
