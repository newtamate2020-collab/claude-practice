# Kling AI Text-to-Video スクリプト

`kling_text_to_video.py` はKling AIの公式APIを使い、テキストプロンプトから動画を生成してダウンロードするCLIツールです。

## APIキーの取得方法

1. https://klingai.com (または国際版 https://app.klingai.com) のアカウントでログイン
2. コンソールの「API」または「Developer」セクションから **Access Key** と **Secret Key** を発行
3. 利用にはクレジット/課金設定が必要です(生成本数に応じた従量課金)

キーは環境変数として渡します。

```bash
export KLING_ACCESS_KEY="発行されたアクセスキー"
export KLING_SECRET_KEY="発行されたシークレットキー"
```

## セットアップ

```bash
cd kling-video
pip install -r requirements.txt
```

## 使い方

```bash
python kling_text_to_video.py "夕焼けの海で波乗りする猫" --out cat_surfing.mp4
```

オプション:

- `--duration` : `5` または `10`(秒)
- `--aspect-ratio` : `16:9` / `9:16` / `1:1`
- `--mode` : `std`(標準)または `pro`(高品質・高コスト)
- `--out` : 保存先ファイル名

## 注意

- Kling AIのAPI仕様は変更される可能性があります。エラーが出る場合は公式ドキュメント(Kling AI Developer Docs)のエンドポイント・パラメータを確認してください。
- JWT認証はHS256で `iss`(access key)・`exp`・`nbf` をクレームに含める方式です。トークンは30分で失効するため、長時間のポーリングでは必要に応じて再発行してください。
- 生成には数十秒〜数分かかることがあります(スクリプトは自動でポーリングします)。
