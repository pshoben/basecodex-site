# House ads

Adverts for our own products, shown in our free apps
(https://basecodex.com/ads/).

- `library/`: every video, once. The Podyglot ones are made as
  `docs/HOUSE_ADS.md` in the Podyglot repository describes.
- `<target>/manifest.json`: what one app shows. The app fetches it, then the
  videos it names. `<target>/index.html` shows the same list to a person.
- `catalogue.json`: the source of all of it. Edit it, run
  `python3 ads/build.py`, commit and push. Never edit a manifest or a page by
  hand.

## The manifest (schema 1)

```json
{
  "schema": 1,
  "app": {"id": "quicksilver", "name": "Quicksilver", "bundleId": "com.pshoben.quicksilver"},
  "ads": [{
    "id": "podyglot-14-days",
    "product": "Podyglot",
    "title": "14 days free for all your household",
    "video": {"url": "https://basecodex.com/ads/library/podyglot-14-days-iphone.mp4",
              "device": "iphone", "width": 1080, "height": 2348, "seconds": 19.5, "bytes": 11417596},
    "tapUrl": "https://apps.apple.com/app/id6775258823?ct=quicksilver-podyglot-14-days",
    "weight": 1
  }],
  "version": "…"
}
```

- `version` changes exactly when what the app should show changes, so an app
  can keep its downloaded videos until it does.
- `weight`: pick an ad with probability weight / total weight.
- `tapUrl` opens the product's App Store page. Its `ct` says which app and
  which ad sent the install; App Store Connect counts it only once the
  provider token (`pt`, from App Analytics, Campaigns) is added to the link.
- The videos stream (`video/mp4`, range requests, the index at the front of
  the file), so `AVPlayer(url:)` plays one directly.
