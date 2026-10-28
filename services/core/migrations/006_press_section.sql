create table staged.press_section (
  url text primary key,
  release_url text not null,
  release_title text,
  heading text,
  extracted_at timestamptz not null default now()
);
