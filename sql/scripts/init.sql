-- sensor-types
insert into sensor_type (id, type, unit) VALUES (1, 'Luminosity', 'lux');
insert into sensor_type (id, type, unit) VALUES (2, 'Humidity', '');

-- admin
insert into user (id, username, email, password_hash, last_seen, created_on)
VALUES (1, 'admin', null, 'pbkdf2:sha256:600000$tlAcerLe4udzCpfi$cb60d0aedfb1a00618a2f377abb302a335fb3a9fa7220025719153d0afbdda74', null, CURRENT_DATE);

-- plants TODO check what are normal humidity levels, what are normal light levels, check harvest time spans
insert into plant (id, name, description_1, description_2, description_3, water_min, water_max, light_min, light_max, harvest_begin, harvest_end, created_on, edited_on)
VALUES (1, 'Tomate', 'Die Tomate ist cool', null, null, 20, 50, 0, 6000, null, null, CURRENT_DATE, CURRENT_DATE);
insert into plant (id, name, description_1, description_2, description_3, water_min, water_max, light_min, light_max, harvest_begin, harvest_end, created_on, edited_on)
VALUES (2, 'Chili', 'Chili ist chillig', null, null, 20, 50, 0, 5000, null, null, CURRENT_DATE, CURRENT_DATE);
insert into plant (id, name, description_1, description_2, description_3, water_min, water_max, light_min, light_max, harvest_begin, harvest_end, created_on, edited_on)
VALUES (3, 'Aloe Vera', 'Miau!', null, null, 20, 50, 0, 4000, null, null, CURRENT_DATE, CURRENT_DATE);