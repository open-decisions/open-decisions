create schema if not exists raw;

create table raw.parliament_list_item (
  jurisdiction text not null,
  gp text not null,
  ityp text not null,
  inr text not null,
  payload jsonb not null,
  hash text not null,
  first_seen timestamptz not null default now(),
  last_seen timestamptz not null default now(),
  changed_at timestamptz not null default now(),
  primary key (jurisdiction, gp, ityp, inr)
);

create table raw.parliament_item (
  jurisdiction text not null,
  gp text not null,
  ityp text not null,
  inr text not null,
  payload jsonb not null,
  hash text not null,
  fetched_at timestamptz not null default now(),
  changed_at timestamptz not null default now(),
  primary key (jurisdiction, gp, ityp, inr)
);

create table raw.document (
  url text primary key,
  content bytea not null,
  content_type text,
  sha256 text not null,
  fetched_at timestamptz not null default now()
);
