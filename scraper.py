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
    url = "https://truckersmp.com/vtc/64218/events/attending"
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")

    events = []
    for card in soup.select(".event, .event-card, .col-md-6"):
        title = card.get_text(strip=True)
        date_el = card.find("time")
        if not date_el: continue
        date_str = date_el.get_text(strip=True)
        dt = parse_date(date_str)
        events.append({
            "title": title,
            "start": dt,
            "end": dt + timedelta(hours=3)
        })
    return events

def to_ics(events):
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//VTC Calendar//EN"]
    for ev in events:
        uid = f"{hash(ev['title']+str(ev['start']))}@vtc"
        lines.append("BEGIN:VEVENT")
        lines.append(f"UID:{uid}")
        lines.append(f"DTSTAMP:{ev['start'].strftime('%Y%m%dT%H%M%S')}")
        lines.append(f"DTSTART:{ev['start'].strftime('%Y%m%dT%H%M%S')}")
        lines.append(f"DTEND:{ev['end'].strftime('%Y%m%dT%H%M%S')}")
        lines.append(f"SUMMARY:{ev['title']}")
        lines.append("END:VEVENT")
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines)

if __name__ == "__main__":
    events = scrape_events()
    ics = to_ics(events)
    with open("vtc-events.ics", "w", encoding="utf-8") as f:
        f.write(ics)
