alter table raw.document add column size_bytes integer not null default 0;
alter table raw.document add column http_status integer;

create table staged.document_text (
  url text primary key references raw.document (url) on delete cascade,
  text text not null,
  pages integer,
  extractor text not null,
  extracted_at timestamptz not null default now()
);

create index document_text_fts on staged.document_text using gin (to_tsvector('german', text));
