-- ユーザーテーブル
CREATE table userTable(
    id INT,
    userID VARCHAR(30) UNIQUE, -- userID
    modified BIGINT unsigned, -- 最終更新日時
    lastid BIGINT unsigned, -- 過去ツイ探索用起点
    sinceid BIGINT unsigned, -- 新規ツイ探索用起点
    followers INT, -- フォロワー数
    TwitterID VARCHAR(30), -- Twitter ID
    AccountName TEXT -- アカウント名
);

-- 画像管理テーブル
CREATE table imageTable(
    id INT,
    userID VARCHAR(30), -- userID(≠TwitterID)
    likes INT, -- いいね数
    post BIGINT unsigned, -- ツイート日時
    content VARCHAR(200), -- ツイートされたテキスト
    imgPath VARCHAR(190) UNIQUE, -- 画像のパス
    localPath VARCHAR(200) -- 画像のローカルパス
);