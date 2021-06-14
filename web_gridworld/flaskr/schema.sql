DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_counter INTEGER NOT NULL DEFAULT 0,
  username TEXT UNIQUE NOT NULL,
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
    run_number INTEGER NOT NULL,
    level_number INTEGER NOT NULL,
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