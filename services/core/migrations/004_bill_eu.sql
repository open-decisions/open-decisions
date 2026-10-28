create table staged.bill_eu (
  bill_id text primary key references staged.bill (id) on delete cascade,
  kind text not null,
  kinds jsonb not null default '[]',
  goes_beyond boolean not null default false,
  statements jsonb not null default '[]',
  acts jsonb not null default '[]',
  extracted_at timestamptz not null default now()
);
