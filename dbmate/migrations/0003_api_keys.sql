-- migrate:up
-- Las tablas de 0001 nunca se usaron desde el codigo: se reemplazan sin migrar datos.
DROP TABLE api_keys;
DROP TABLE api_scopes;

-- Una key por usuario: user_id es la clave primaria. Solo se guarda el hash.
CREATE TABLE api_keys (
  user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  prefix VARCHAR(16) NOT NULL,
  key_hash CHAR(64) UNIQUE NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
  last_used_at TIMESTAMP WITH TIME ZONE
);

-- migrate:down
DROP TABLE api_keys;

CREATE TABLE api_scopes (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE api_keys (
  id SERIAL PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  key VARCHAR(255) UNIQUE NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  expired_at TIMESTAMP WITH TIME ZONE,
  last_used_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_api_keys_expired ON api_keys(expired_at);
