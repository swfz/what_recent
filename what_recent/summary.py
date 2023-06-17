import openai
import json
import requests
import os

from what_recent import api_log

def fetch_diff(url):
    res = requests.get(url)
    json = res.json()

    api_log('patch', json)

    diffs = "\n".join([f"file: {f['filename']} で下記の変更 {f['patch']}" for f in json["files"] if f['changes'] > 0])

    return diffs

# 5つ以上URLがあった場合は最初の5件のみとする(GitHubのAPI制限やToken制限に引っかかりやすくなるため)
def fetch_diffs(urls):
    url_list = urls.split(',')

    responses = [fetch_diff(url) for url in url_list[0:1]]
    return "\n".join(responses)

def activities_summary(activities):
    model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
    system_content = """
これからGitHubでのリポジトリとどんなことをしたかのテキストを渡します
これらをまとめて、最近の活動についてまとめてください
また、下記制約を守った出力をしてください
- どういう技術に興味がありそうなのか
- 取り組みの難易度を記載する
- 活動の要約についてはプルリクエストではどんなことをやったのかが読みたいです、ブランチを作った、Forkしたなどは省略してください
- リポジトリ名に関しては`swfz/dotfiles`のようにスラッシュ前の文言も含めてください
- コミットについて、やっている内容が分かりづらい場合はurlを元に差分を取得してその内容からやっていることを把握してください(最大5つまで)

全体的にどんな技術に興味がありそうか
"""

    text = "\n".join(list(map(lambda a: f"リポジトリ:{a['repository']}\n{a['changes']}", activities)))

    fetch_diff_desc = {
        "name": "fetch_diffs",
        "description": "どんなことをしていたかわからない場合、より詳しく見るため、Diffを取得するAPIをCallしてコード差分を取得する",
        "parameters": {
            "type": "object",
            "properties": {
                "urls": {
                    "type": "string",
                    "description": "APIのURL、複数ある場合はカンマ区切り"
                },
            },
            "required": ["urls"]
        }
    }

    print("input ==================================================")
    print(text)
    print("input ==================================================")

    system_prompt = {"role": "system", "content": system_content}

    res = openai.ChatCompletion.create(
        model=model,
        messages=[
            system_prompt,
            {"role": "user", "content": text }
        ],
        functions=[
            fetch_diff_desc
        ],
        function_call="auto"
        )

    print(res)

    message = res.choices[0]["message"]

    print(message)
    if message.get("function_call"):
        function_name = message["function_call"]["name"]
        function_args = json.loads(message["function_call"]["arguments"])

        function_res = fetch_diffs(
            urls=function_args["urls"]
        )
        second_res = openai.ChatCompletion.create(
            model=model,
            messages=[
                system_prompt,
                message,
                {
                    "role": "function",
                    "name": function_name,
                    "content": function_res
                }
            ]
        )

        role = second_res.choices[0]["message"]["role"]
        content = second_res.choices[0]["message"]["content"]
        print(f"{role}: {content}")
    else:
        role = res.choices[0]["message"]["role"]
        content = res.choices[0]["message"]["content"]

        print(f"{role}: {content}")

    # return content

