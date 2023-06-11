insert into sensor_type (id, type, unit) VALUES (1, 'Luminosity', 'lux');
insert into sensor_type (id, type, unit) VALUES (2, 'Humidity', '');

insert into user (id, username, email, password_hash, last_seen, created_on) VALUES (1, 'admin', null, 'pbkdf2:sha256:600000$tlAcerLe4udzCpfi$cb60d0aedfb1a00618a2f377abb302a335fb3a9fa7220025719153d0afbdda74', null, null);