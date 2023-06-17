import openai
import os

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

