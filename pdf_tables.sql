CREATE EXTENSION vector;
CREATE TABLE IF NOT EXISTS "article" (
  "id" integer PRIMARY KEY,
  "title" varchar[1024] UNIQUE NOT NULL,
  "upload_date" date,
  "article_text" text
);

CREATE TABLE IF NOT EXISTS "segment" (
  "id" integer PRIMARY KEY,
  "article_id" integer,
  "segment_title" varchar[1024],
  "segment_title_vector" vector(768),
  "segment_text" text,
  "segment_text_vector" vector(768)
);

ALTER TABLE "segment" ADD CONSTRAINT IF NOT EXISTS fk_article FOREIGN KEY ("article_id") REFERENCES "article" ("id");
