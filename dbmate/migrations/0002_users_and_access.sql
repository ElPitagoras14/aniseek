-- migrate:up
ALTER TABLE role_types ADD CONSTRAINT uq_role_types_name UNIQUE (name);
INSERT INTO role_types (name) VALUES ('owner');

UPDATE users SET role_id = (SELECT id FROM role_types WHERE name = 'member')
WHERE role_id = (SELECT id FROM role_types WHERE name = 'guest');
DELETE FROM role_types WHERE name = 'guest';

-- A lo sumo un owner: indice unico parcial sobre una expresion constante.
-- El id del rol se resuelve aca porque un indice parcial no admite subconsultas.
DO $$
BEGIN
  EXECUTE format(
    'CREATE UNIQUE INDEX uq_users_single_owner ON users ((true)) WHERE role_id = %s',
    (SELECT id FROM role_types WHERE name = 'owner')
  );
END $$;

ALTER TABLE users ADD COLUMN credentials_changed_at TIMESTAMP WITH TIME ZONE;

CREATE TABLE instance_settings (
  id BOOLEAN PRIMARY KEY DEFAULT TRUE CHECK (id),
  registration_policy TEXT NOT NULL DEFAULT 'invite'
    CHECK (registration_policy IN ('invite', 'open')),
  updated_by UUID REFERENCES users(id) ON DELETE SET NULL,
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO instance_settings DEFAULT VALUES;

CREATE TABLE invitations (
  id UUID PRIMARY KEY,
  token_hash CHAR(64) UNIQUE NOT NULL,
  role_id INTEGER NOT NULL REFERENCES role_types(id) ON DELETE RESTRICT,
  created_by UUID REFERENCES users(id) ON DELETE SET NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
  used_at TIMESTAMP WITH TIME ZONE,
  used_by UUID REFERENCES users(id) ON DELETE SET NULL,
  revoked_at TIMESTAMP WITH TIME ZONE,
  CHECK (used_at IS NULL OR revoked_at IS NULL)
);
CREATE INDEX idx_invitations_pending ON invitations (expires_at)
  WHERE used_at IS NULL AND revoked_at IS NULL;

-- migrate:down
DROP TABLE invitations;
DROP TABLE instance_settings;

ALTER TABLE users DROP COLUMN credentials_changed_at;
DROP INDEX uq_users_single_owner;

-- Los usuarios que eran guest no se pueden reconstruir: quedan como member.
INSERT INTO role_types (name) VALUES ('guest');
UPDATE users SET role_id = (SELECT id FROM role_types WHERE name = 'admin')
WHERE role_id = (SELECT id FROM role_types WHERE name = 'owner');
DELETE FROM role_types WHERE name = 'owner';

ALTER TABLE role_types DROP CONSTRAINT uq_role_types_name;
