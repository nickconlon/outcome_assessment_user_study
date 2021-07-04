DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_counter INTEGER NOT NULL DEFAULT 0,
  first_color INTEGER,
  second_color INTEGER,
  third_color INTEGER,
  accuracy INTEGER,
  competency INTEGER,
  username TEXT UNIQUE NOT NULL,
  first_trust INTEGER,
  second_trust INTEGER,
  third_trust INTEGER,
  open_question TEXT,
  code INTEGER,
  time_start timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  prescreen TEXT,
  age TEXT,
  gender TEXT,
  education TEXT,
  games TEXT,
  password TEXT NOT NULL
);

CREATE TABLE post (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    FOREIGN KEY (author_id) REFERENCES user (id)
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
    h_score TEXT NOT NULL,
    a_score TEXT NOT NULL,
    outcome TEXT NOT NULL,
    tot_mission_time_s INTEGER NOT NULL,
    tot_mission_steps INTEGER NOT NULL,
    num_interventions INTEGER NOT NULL,
    num_steps_interventions INTEGER NOT NULL,
    intervention_locations TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user (id)
);