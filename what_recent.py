import json
import openai
import requests
import sys
import os

BOT_USER_NAMES=['renovate[bot]', 'dependabot[bot]', 'github-actions[bot]']

class EventFactory:
    def create_event(self, event):
        if event['type'] in globals():
            return globals()[event['type']](event)
        else:
            return DummyEvent(event)

class Event:
    def __init__(self, event):
        self.event_name = event['type']
        self.data = event

class DummyEvent(Event):
    def __init__(self, event):
        super().__init__(event)

    def bot_event(self):
        return False

    def available(self):
        return False

class PushEvent(Event):
    def __init__(self, event):
        super().__init__(event)

    def transform(self):
        return {
            "repository": self.data['repo']['name'],
            "changes": "下記のコミットをしています" + "\n".join([c['message'] for c in self.data['payload']['commits']])
        }

    def bot_event(self):
        return all([c['author']['name'].find('users.noreply.github.com') for c in self.data['payload']['commits']])

    def available(self):
        return not self.bot_event()

class PullRequestEvent(Event):
    def __init__(self, event):
        super().__init__(event)

    def transform(self):
        body = self.data['payload']['pull_request']['body'] or ''

        return {
            "repository": self.data['repo']['name'],
            "changes": self.data['payload']['pull_request']['title'] + f"というタイトルで下記内容のPullRequestを{self.data['payload']['action']}しています\n" + body
        }

    def bot_event(self):
        return self.data['payload']['pull_request']['user']['login'] in BOT_USER_NAMES

    def available(self):
        return not self.bot_event()

class IssuesEvent(Event):
    def __init__(self, event):
        super().__init__(event)

    def transform(self):
        body = self.data['payload']['issue']['body'] or ''
        action = '作成' if self.data['payload']['action'] == 'created' else 'Close'

        return {
            "repository": self.data['repo']['name'],
            "changes": self.data['payload']['issue']['title'] + f"というタイトルで下記内容のIssueを{action}しました\n" + body
        }

    def bot_event(self):
        return self.data['payload']['issue']['user']['login'] in BOT_USER_NAMES

    def available(self):
        return not self.bot_event()

class IssueCommentEvent(Event):
    def __init__(self, event):
        super().__init__(event)

    def transform(self):
        body = self.data['payload']['comment']['body'] or ''

        return {
            "repository": self.data['repo']['name'],
            "changes": self.data['payload']['issue']['title'] + f"というIssueに対し下記内容のコメントをしています\n" + body
        }

    def bot_event(self):
        return False

    def available(self):
        return True

class CreateEvent(Event):
    def __init__(self, event):
        super().__init__(event)

    def transform(self):

        return {
            "repository": self.data['repo']['name'],
            "changes": "{self.data['payload']['ref']}という{self.data['payload']['ref_type']}を作成しました"
        }

    def bot_event(self):
        return False

    def available(self):
        return True

class PullRequestReviewCommentEvent(Event):
    def __init__(self, event):
        super().__init__(event)

    def transform(self):

        return {
            "repository": self.data['repo']['name'],
            "changes": "{self.data['payload']['pull_request']['title'}というPullRequestに{self.data['payload']['comment']['body']}というレビューコメントをしています"
        }

    def bot_event(self):
        return False

    def available(self):
        return True

class ForkEvent(Event):
    def __init__(self, event):
        super().__init__(event)

    def transform(self):

        return {
            "repository": self.data['repo']['name'],
            "changes": "Forkしました"
        }

    def bot_event(self):
        return False

    def available(self):
        return True


def read_json(filename):
    with open(filename) as f:
        return json.load(f)

def activities_summary(activities):
    model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
    system_content = """
これからGitHubでのリポジトリとどんなことをしたかのテキストを渡します
これらをまとめて、最近の活動についてまとめてください
どういう技術に興味がありそうなのか、取り組みの難易度もわかれば教えてほしいです
同じようなことをたくさんしている場合はその旨も要約に入れてください
"""

    text = "\n".join(list(map(lambda a: f"リポジトリ:{a['repository']}\n{a['changes']}", activities)))

    # print("input ==================================================")
    # print(text)
    # print("input ==================================================")

    system_prompt = {"role": "system", "content": system_content}

    res = openai.ChatCompletion.create(
        model=model,
        temperature=0.9,
        messages=[
            system_prompt,
            {"role": "user", "content": text }
        ])

    role = res.choices[0]["message"]["role"]
    content = res.choices[0]["message"]["content"]

    print(f"{role}: {content}")

    return content


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

