-- migrate:up
-- Switch de instancia del MCP. Desactivado por defecto, tambien al actualizar.
ALTER TABLE instance_settings
  ADD COLUMN mcp_enabled BOOLEAN NOT NULL DEFAULT false;

-- migrate:down
ALTER TABLE instance_settings DROP COLUMN mcp_enabled;
