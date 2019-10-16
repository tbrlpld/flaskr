INSERT INTO user (username, password)
VALUES
  ('test', 'pbkdf2:sha256:50000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14f3e2fa61f2d17574483f7ffbb431b4acb2f'),
  ('other', 'pbkdf2:sha256:50000$kJPKsz6N$d2d4784f1b030a9761f5ccaeeaca413f27f2ecb76d6168407af962ddce849f79');

INSERT INTO post (title, body, body_html, author_id, created)
VALUES
	('test title', 'test' || x'0a' || 'body', 'test' || x'0a' || 'body', 1, '2018-01-01 00:00:00');

INSERT INTO comment (body, author_id, post_id, created)
VALUES
	('test comment body', 2, 1, '2018-01-01 00:00:01');	

INSERT INTO like (user_id, post_id, created)
VALUES
	(2, 1, '2018-01-01 00:00:02');

INSERT INTO tag (name, created)
VALUES
	('testtag', '2018-01-01 00:00:03');

INSERT INTO post_tag (post_id, tag_id)
VALUES
	(1, 1);