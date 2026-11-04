# Museum of Outages 🏛️

A permanent exhibition of the days the internet fell over — eleven famous
tech outages preserved as museum exhibits: what happened, how much it
cost, and the lesson each one taught. Curated by **Bishow Pandey**, a
senior platform engineer (Kubernetes, cloud, application security) who is
professionally invested in keeping new exhibits out of this building.

- Live museum: https://bishowpratap7.github.io/museumofoutages/
- Curator on X: https://x.com/bishowppandey

## The wings
- **Wing I — The Deployment Wing:** Knight Capital (2012), Cloudflare's
  regex rule (2019), and the centerpiece — CrowdStrike (2024)
- **Wing II — The Hall of Configuration:** Fastly (2021), Facebook's BGP
  disappearance (2021), AWS US-EAST-1 (2021)
- **Wing III — The Typo Room:** the AWS S3 typo (2017)
- **Wing IV — Fire, Power & Malice:** the Dyn webcam-army DDoS (2016),
  British Airways' power incident (2017), the OVHcloud fire (2021)
- **Wing V — The Partition Gallery:** GitHub's 43-second partition (2018)

Every exhibit is summarized in the museum's own words from the company's
public postmortem or official statement, with the date, the damage, and a
one-line lesson. Each carries a "Pandey Scale" rating — the curator's
subjective score for scale, story and teaching value.

## The Emergency Room
A small live wing: `tools/scan.py` watches the public status pages of
GitHub, Cloudflare, npm and Vercel for incidents from the last 14 days —
future exhibits, admitted around the clock by a self-running GitHub
Actions loop, exactly like the other desks in the network.

## Sister desks
The Dev Desk · Scroll Patrol · The World Desk · The Stock Desk ·
The Shopping Desk · The Cozy Desk · The Foodie Desk · The Style Desk

## Repos
- `museumofoutages` (public) — the live museum, served by GitHub Pages
- `the-museum-of-outages` (private) — the archive twin
