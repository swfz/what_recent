import json
import requests
import sys

from what_recent import EventFactory, activities_summary

def main():
    user = sys.argv[1]
    url = f"https://api.github.com/users/{user}/events?per_page=100&page=1"
    res = requests.get(url)
    data = res.json()
    factory = EventFactory()

    events = [factory.create_event(event) for event in data]
    activities = [e.transform() for e in events if e.available()]
    dummy = [e for e in events if e.__class__.__name__ == 'DummyEvent']
    bot_activities = [e for e in events if e.bot_event()]

    # print(set([e.event_name for e in dummy]))
    # print(json.dumps([e.data for e in dummy if e.event_name == 'ForkEvent'], indent=2))

    print(f"{len(activities)}件のサマリー対象Activityがありました")
    print(f"{len(dummy)}件の未対応Activityがありました")
    print(f"{len(bot_activities)}件のbotによるActivityがありました")

    activities_summary(activities)

