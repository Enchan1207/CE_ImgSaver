-- ユーザーテーブル
CREATE table userTable(
    id INT,
    TwitterID STRING, -- Twitter ID
    modified INTEGER, -- 最終更新日時
    lastid INTEGER, -- 過去ツイ探索用起点
    sinceid INTEGER -- 新規ツイ探索用起点
);

-- 画像管理テーブル
CREATE table imageTable(
    id INT,
    TwitterID STRING, -- Twitter ID
    post INTEGER, -- ツイート日時
    content STRING, -- ツイートされたテキスト
    imgPath STRING, -- 画像のパス
    localPath STRING -- 画像のローカルパス
);

-- エラーログテーブル
CREATE table errorTable(
    id INT,
    errorTime INTEGER,
    errorText STRING
);