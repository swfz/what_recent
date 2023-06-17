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
        # NOTE: この条件だとRenovateでビルド失敗してて手動で修正入れたパターンは含まれなくなってしまう
        return any([c['author']['email'].find('users.noreply.github.com') > 0 for c in self.data['payload']['commits']])

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

