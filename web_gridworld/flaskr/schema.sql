DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_counter INTEGER NOT NULL DEFAULT 0,
  accuracy INTEGER,
  competency INTEGER,
  username TEXT UNIQUE NOT NULL,
  first_trust INTEGER,
  second_trust INTEGER,
  third_trust INTEGER,
  open_question TEXT,
  code TEXT,
  time_start timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  prescreen TEXT,
  age TEXT,
  gender TEXT,
  education TEXT,
  games TEXT,
  latest_score INTEGER,
  client_ip TEXT,
  password TEXT NOT NULL
);

CREATE TABLE results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    map_number INTEGER NOT NULL,
    accuracy_level INTEGER NOT NULL,
    competency_level INTEGER NOT NULL,
    confidence TEXT NOT NULL,
    report_level INTEGER NOT NULL,
    run_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    tot_mission_time_s INTEGER NOT NULL,
    tot_mission_steps INTEGER NOT NULL,
    path TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user (id)
);