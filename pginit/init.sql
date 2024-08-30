CREATE TABLE IF NOT EXISTS users (
  id SERIAL,
  username varchar(255) NOT NULL,
  password varchar(255) NOT NULL,
  created_at timestamp NOT NULL,
  PRIMARY KEY (id)
) ;

CREATE TABLE IF NOT EXISTS notes (
  id SERIAL,
  title varchar(255) NOT NULL,
  content text NOT NULL,
  user_id integer NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  is_public boolean DEFAULT false NOT NULL,
  is_deleted boolean DEFAULT false NOT NULL,
  created_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
  PRIMARY KEY (id)
) ;

