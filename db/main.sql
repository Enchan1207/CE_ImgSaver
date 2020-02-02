-- ユーザーテーブル
CREATE table userTable(
    id INT,
    TwitterID TEXT, -- Twitter ID
    modified INTEGER, -- 最終更新日時
    lastid INTEGER, -- 過去ツイ探索用起点
    sinceid INTEGER, -- 新規ツイ探索用起点
    followers INT -- フォロワー数
);

-- 画像管理テーブル
CREATE table imageTable(
    id INT,
    TwitterID TEXT, -- Twitter ID
    likes INT, -- いいね数
    post INTEGER, -- ツイート日時
    content TEXT, -- ツイートされたテキスト
    imgPath TEXT, -- 画像のパス
    localPath TEXT -- 画像のローカルパス
);