create schema if not exists staged;

create table staged.bill (
  id text primary key,
  jurisdiction text not null,
  gp text not null,
  ityp text not null,
  inr text not null,
  type text not null,
  title text not null,
  citation text,
  parliament_url text not null,
  introduced date,
  introduced_by jsonb not null default '[]',
  stage text not null,
  source_status text,
  gazette text,
  gazette_url text,
  eli text,
  eurovoc jsonb not null default '[]',
  topics jsonb not null default '[]',
  keywords jsonb not null default '[]',
  documents jsonb not null default '{}',
  pre_parliamentary jsonb not null default '[]',
  vote jsonb,
  source_updated timestamptz,
  fetched_at timestamptz not null,
  transformed_at timestamptz not null default now()
);

create table staged.bill_phase (
  bill_id text not null references staged.bill (id) on delete cascade,
  seq integer not null,
  phase text not null,
  chamber text,
  date date not null,
  text text not null,
  url text,
  primary key (bill_id, seq)
);

create index on staged.bill (jurisdiction, stage);
create index on staged.bill (introduced);
