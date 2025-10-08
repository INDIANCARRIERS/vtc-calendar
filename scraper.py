import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

MONTHS = {
    "Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,
    "Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12
}

def parse_date(date_str):
    # Example: "Fri, Oct 10, 2025 21:30"
    parts = date_str.replace(",", "").split()
    month = MONTHS[parts[1]]
    day = int(parts[2])
    year = int(parts[3])
    hour, minute = map(int, parts[4].split(":"))
    return datetime(year, month, day, hour, minute)

def scrape_events():
    base_url = "https://truckersmp.com/vtc/64218/events/attending"
    page = 1
    events = []

    while True:
        url = f"{base_url}?page={page}"
        html = requests.get(url).text
        soup = BeautifulSoup(html, "html.parser")

        cards = soup.select("div.h-100.bg-color-light")
        if not cards:
            break

        for card in cards:
            title_el = card.select_one("h4 a")
            date_el = card.select_one("p.mb-2 b")
            if not title_el or not date_el:
                continue

            title = title_el.get_text(strip=True)
            link = title_el["href"]
            date_str = date_el.get_text(strip=True)
            departure = parse_date(date_str)

            # Adjust: meet-up starts 1 hour before departure
            meetup = departure - timedelta(hours=1)

            events.append({
                "title": title,
                "start": meetup,
                "end": departure,
                "url": link
            })

        page += 1

    return events

def to_ics(events):
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//VTC Calendar//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH"
    ]
    for i, ev in enumerate(events):
        uid = f"{i}-{ev['start'].strftime('%Y%m%dT%H%M%S')}@vtc-calendar"
        lines.append("BEGIN:VEVENT")
        lines.append(f"UID:{uid}")
        lines.append(f"DTSTAMP:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}")
        lines.append(f"DTSTART:{ev['start'].strftime('%Y%m%dT%H%M%SZ')}")
        lines.append(f"DTEND:{ev['end'].strftime('%Y%m%dT%H%M%SZ')}")
        lines.append(f"SUMMARY:{ev['title']}")
        if ev.get("url"):
            lines.append(f"URL:{ev['url']}")
        lines.append("END:VEVENT")
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines)

if __name__ == "__main__":
    events = scrape_events()
    print(f"Scraped {len(events)} events")
    ics = to_ics(events)
    with open("vtc-events.ics", "w", encoding="utf-8") as f:
        f.write(ics)
