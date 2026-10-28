alter table staged.bill add column summary jsonb not null default '[]';
alter table staged.bill add column press jsonb not null default '[]';
