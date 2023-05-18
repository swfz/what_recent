# what_recent

GitHubのPublicAPIとChatGPTを使ってこの人最近なにやってるの？をまとめるコマンド

## Usage

### Install

```
$ pip install git+https://github.com/swfz/what_recent.git
```

### Example

```
$ export OPENAI_API_KEY=*****
$ export OPENAI_MODEL=gpt-4
$ what_recent swfz

32件のサマリー対象Activityがありました
26件の未対応Activityがありました
42件のbotによるActivityがありました
assistant: 最近の活動について、以下のまとめができます。

1. 主にリポジトリ`swfz/til`で活動しており、Gatsby関連のプラグインや環境設定の更新や改善を行っています。特に`gatsby-plugin-algolia`のメジャーバージョンアップや、`eslint`の改善に取り組んでいます。

2. `swfz/dotfiles`ではVimのバージョンアップに対応していますが、これは難易度の低いタスクです。

3. 他のリポジトリでも活動しており、`swfz/gh-annotations`ではREADMEの更新やIssueの対応、`swfz/hatenablog_publisher`では記事修正時のURLの問題解決などを行っています。

このことから、技術的に興味を持っている可能性が高いのは、Gatsby（Webフレームワーク）やGitHubのAPI関連、Vim（エディタ）などです。また、彼の取り組みは中～高難易度のものが多いと考えられます。同じ
ような内容を繰り返し取り組んでいることが、興味のある技術分野や取り組みの難易度に影響していると言えます。
```

## Environments

| Environment | value | remark |
|:-|:-|:-|
| OPENAI_API_KEY | API KEY |  |
| OPENAI_MODEL | gpt-4 etc... | default: gpt-3.5-turbo see: [models](https://platform.openai.com/docs/models/overview)|

## Development

```
pipenv install -e .
pipenv run what_recent swfz
```
