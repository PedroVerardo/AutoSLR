CREATE TABLE "article" (
  "id" integer PRIMARY KEY,
  "title" varchar[1024] UNIQUE NOT NULL,
  "upload_date" date,
  "article_text" text
);

CREATE TABLE "segment" (
  "id" integer PRIMARY KEY,
  "article_id" integer,
  "segment_title" varchar[1024],
  "segment_text" text
);

ALTER TABLE "segment" ADD FOREIGN KEY ("article_id") REFERENCES "article" ("id");

CREATE INDEX idx_article_upload_date ON article(upload_date);
