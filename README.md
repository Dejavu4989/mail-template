# JCI Mongolia appointment email maker

A static site (plain HTML, no build step, no backend). Staff fill in a form, click **Имэйл хуулах**,
and paste the finished email into Gmail.

## Files

| File | Purpose |
|---|---|
| `index.html` | The maker page: form, live preview, copy button. Default content is in `DEFAULTS` at the top of the script |
| `jci-appointment-email.html` | The email layout, filled in through `{{tokens}}` |
| `banners/` | Animated banners to choose from (1120x448, about 200 KB each, no year in the image) |
| `hero.gif` | Original banner with 2027 in the image. Keep it: emails already sent load it |
| `tools/make-banners.py` | Creates the GIFs in `banners/` |
| `vercel.json` | Caching and CORS headers for the banners |
| `.vercelignore` | Keeps `.claude/`, `tools/` and this README off the public site |

## What can be changed

- **Per email:** recipient name and region.
- **In the form, saved on that device:** year, role, deadline, phone, signature, banner choice, and every sentence.
- **For everyone:** edit `DEFAULTS` in `index.html` and redeploy. Form settings are stored per browser,
  so staff do not see each other's changes. **Анхны утгаар сэргээх** returns to `DEFAULTS`.
- **Not editable in the form:** the text drawn inside the banner images. To change it, see below.

In the sentences, `{нэр}`, `{албан тушаал}`, `{он}`, `{огноо}` and `{утас}` are filled in automatically.
The deadline is written in Mongolian from the date picker, for example `2026 оны 11 дүгээр сарын 06-ны`.

## Making new banners

Text in a GIF is part of the image, so changing it means creating a new file. On Windows:

```bash
pip install pillow
python tools/make-banners.py
```

Edit `TITLE`, `EYEBROW` or `THEMES` at the top of the script first, then add each new file to `BANNERS` in `index.html`.
**Use a new theme name for a changed design.** Never overwrite a banner that has been used: sent emails keep
loading it, and it is cached for a year.

## Run locally

```bash
python -m http.server 8787
```

Then open http://localhost:8787. Opening `index.html` directly from disk does not work.
Without HTTPS the copied email embeds the GIF instead of linking it, so send real emails from the deployed site.

## Deploy to Vercel

**Dashboard:** drag this folder onto vercel.com/new (or push it to GitHub and import it).
Framework Preset: **Other**. Leave Build Command and Output Directory empty.

**CLI:**
```bash
npx vercel --prod
```

## Important

- **`hero.gif` and `banners/` must stay publicly reachable forever.** Sent emails load the banner from
  `https://<your-domain>/banners/blue.gif` (or whichever was chosen). If the deployment is deleted, protected, or the domain changes,
  the banner disappears from emails already sent.
- **Copy from the production domain only.** The email links the GIF on whichever domain you copied from,
  and Vercel preview URLs are not permanent.
- **Turn off Vercel Deployment Protection** for the production domain (Project > Settings > Deployment Protection).
  Otherwise mail apps cannot load the image.
- Preferably assign a stable custom domain (for example `email.jci.mn`) before sending real emails.

## Editing the email layout

Keep these rules in `jci-appointment-email.html`, or iPhone dark mode will break again:

- All styles stay **inline**. Gmail removes `<style>` blocks when pasting.
- **No background colors, and no color on normal text.** Text then inherits the mail app color and adapts
  to light and dark mode by itself.
- Use only `#0A7CC2` (accent) and `#7C7C80` (secondary text). Both are readable on white and on black.
