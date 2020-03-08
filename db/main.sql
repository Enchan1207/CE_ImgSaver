-- ユーザーテーブル
CREATE table userTable(
    id INT,
    TwitterID VARCHAR(30) UNIQUE, -- Twitter ID
    modified BIGINT unsigned, -- 最終更新日時
    lastid BIGINT unsigned, -- 過去ツイ探索用起点
    sinceid BIGINT unsigned, -- 新規ツイ探索用起点
    followers INT -- フォロワー数
);

-- 画像管理テーブル
CREATE table imageTable(
    id INT,
    TwitterID VARCHAR(30), -- Twitter ID
    likes INT, -- いいね数
    post BIGINT unsigned, -- ツイート日時
    content VARCHAR(200), -- ツイートされたテキスト
    imgPath VARCHAR(190) UNIQUE, -- 画像のパス
    localPath VARCHAR(200) -- 画像のローカルパス
);