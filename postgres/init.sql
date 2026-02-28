-- ========================================
-- SCHEMA: Anime Database
-- ========================================
CREATE TABLE franchises (
  id VARCHAR(255) PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE animes (
  id VARCHAR(255) PRIMARY KEY,
  franchise_id VARCHAR(255) REFERENCES franchises(id) ON DELETE SET NULL,
  season INTEGER DEFAULT 1,
  title VARCHAR(255),
  description TEXT,
  type TEXT,
  poster TEXT,
  is_finished BOOLEAN,
  week_day TEXT,
  last_scraped_at TIMESTAMP WITH TIME ZONE,
  last_forced_update TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE other_titles (
  anime_id VARCHAR(255) NOT NULL REFERENCES animes(id) ON DELETE CASCADE,
  name VARCHAR NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (anime_id, name)
);

CREATE TABLE genres (
  anime_id VARCHAR(255) NOT NULL REFERENCES animes(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (anime_id, name)
);

CREATE TABLE related_types (
  id SERIAL PRIMARY KEY,
  name VARCHAR NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE anime_relations (
  anime_id VARCHAR(255) NOT NULL REFERENCES animes(id) ON DELETE CASCADE,
  related_anime_id VARCHAR(255) NOT NULL REFERENCES animes(id) ON DELETE CASCADE,
  type_related_id INTEGER NOT NULL REFERENCES related_types(id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (anime_id, related_anime_id, type_related_id),
  CONSTRAINT chk_not_self_relation CHECK (anime_id <> related_anime_id)
);

CREATE TABLE episodes (
  id SERIAL PRIMARY KEY,
  anime_id VARCHAR(255) NOT NULL REFERENCES animes(id) ON DELETE CASCADE,
  ep_number INTEGER NOT NULL,
  url TEXT NOT NULL,
  preview TEXT,
  job_id VARCHAR,
  status TEXT,
  size INTEGER,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT uq_episode_anime_number UNIQUE (anime_id, ep_number)
);

CREATE TABLE role_types (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE avatars (
  id SERIAL PRIMARY KEY,
  label VARCHAR(255) NOT NULL,
  url VARCHAR(255) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE users (
  id UUID PRIMARY KEY,
  username VARCHAR(64) UNIQUE NOT NULL,
  password VARCHAR(60) NOT NULL,
  avatar_id INTEGER REFERENCES avatars(id) ON DELETE
  SET
    NULL,
    role_id INTEGER NOT NULL REFERENCES role_types(id) ON DELETE RESTRICT,
    is_active BOOLEAN DEFAULT TRUE,
    timezone VARCHAR(50) DEFAULT 'UTC',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_save_anime (
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  anime_id VARCHAR(255) NOT NULL REFERENCES animes(id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (user_id, anime_id)
);

CREATE TABLE user_download_episode (
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  episode_id INTEGER NOT NULL REFERENCES episodes(id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (user_id, episode_id)
);

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

CREATE INDEX idx_animes_created_at ON animes(created_at);

CREATE INDEX idx_animes_last_scraped ON animes(last_scraped_at);

CREATE INDEX idx_episodes_created_at ON episodes(created_at);

CREATE INDEX idx_users_created_at ON users(created_at);

CREATE INDEX idx_api_keys_expired ON api_keys(expired_at);

CREATE INDEX idx_user_save_anime_created ON user_save_anime(created_at);

CREATE INDEX idx_user_download_episode_created ON user_download_episode(created_at);

INSERT INTO
  role_types (name)
VALUES
  ('admin'),
  ('member'),
  ('guest');

INSERT INTO
  related_types (name)
VALUES
  ('prequel'),
  ('sequel'),
  ('alternative'),
  ('spin_off');

INSERT INTO
  avatars (label, url)
VALUES
  ('girl-2', 'https://i.ibb.co/cKDLPYf9/girl-2.png'),
  ('girl-3', 'https://i.ibb.co/TDMhQNKZ/girl-3.png'),
  (
    'girl-flower',
    'https://i.ibb.co/TBGwDmFr/girl-flower.png'
  ),
  (
    'magician',
    'https://i.ibb.co/kVN40QY0/magician.png'
  ),
  (
    'monster',
    'https://i.ibb.co/6RLvMs8V/monster.png'
  ),
  (
    'penguin',
    'https://i.ibb.co/9HJ9mKkY/penguin.png'
  ),
  ('pirate', 'https://i.ibb.co/fzC3bMXL/pirate.png'),
  (
    'princess',
    'https://i.ibb.co/1GX3T46j/princess.png'
  ),
  (
    'prisioner',
    'https://i.ibb.co/NdJXVsTW/prisioner.png'
  ),
  ('rat', 'https://i.ibb.co/b5NLtkrp/rat.png'),
  ('robot', 'https://i.ibb.co/pBpts8s5/robot.png'),
  (
    'serial-guy',
    'https://i.ibb.co/9mvfC8hH/serial-guy.png'
  ),
  (
    'vampire',
    'https://i.ibb.co/4n4mNywr/vampire.png'
  ),
  (
    'birthday',
    'https://i.ibb.co/N6xF1zqP/birthday.png'
  ),
  (
    'boy-plant',
    'https://i.ibb.co/xqnKXX7Y/boy-plant.png'
  ),
  (
    'boy-umbrella',
    'https://i.ibb.co/23cXBmv5/boy-umbrella.png'
  ),
  ('cat-1', 'https://i.ibb.co/Q7k50vP5/cat-1.png'),
  ('cat-2', 'https://i.ibb.co/HDxp48yK/cat-2.png'),
  ('clown', 'https://i.ibb.co/QFT55sKM/clown.png'),
  ('cowboy', 'https://i.ibb.co/8gTpjQz7/cowboy.png'),
  ('elf', 'https://i.ibb.co/2YtP7gXY/elf.png'),
  (
    'frankestein',
    'https://i.ibb.co/Z6HXS7yC/frankestein.png'
  ),
  ('girl-1', 'https://i.ibb.co/vxccn7n6/girl-1.png');