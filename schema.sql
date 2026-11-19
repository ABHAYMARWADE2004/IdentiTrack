-- IdentiTrack database schema.
-- Running `python -c "from database import init_db; init_db()"` (or the
-- dashboard's "Initialize database" button) does the same thing and also
-- upgrades an older table that only had person_name + detected_at.

CREATE DATABASE IF NOT EXISTS identitrack_db;
USE identitrack_db;

CREATE TABLE IF NOT EXISTS detections (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    person_name      VARCHAR(100) NOT NULL,
    detected_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    match_distance   FLOAT        NULL,                 -- face distance of the match (lower = closer)
    source           VARCHAR(10)  NOT NULL DEFAULT 'live',  -- 'live' or 'video'
    source_name      VARCHAR(255) NULL,                 -- camera name or video file name
    video_offset_sec FLOAT        NULL,                 -- position inside the video (video rows only)
    INDEX idx_person_time (person_name, detected_at),
    INDEX idx_source (source, source_name)
);
