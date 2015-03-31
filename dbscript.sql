DELETE FROM Authors;

INSERT INTO Authors(author_uuid, name, username, email, image, location, status) VALUES(‘36f6d0150b644bafa9ab0d8c3e3d18e7’, ’Daniel’, ‘daniel’, ‘daniel@ualberta.ca’, ‘/main/static/frog.jpg‘, thought-bubble.herokuapp.com’, ‘True’);

INSERT INTO Authors (author_uuid, name, username, email, location, status) VALUES(‘1dbe1b3ee7e44999b6241cd3f394e778’, ’Brian’, ‘brian’, ‘brian@ualberta.ca’, ‘thought-bubble.herokuapp.com’, ‘True’);

INSERT INTO Authors(author_uuid, name, username, email, image, location, status) VALUES(‘58e8a03086034335967634e1df387238’, ‘Ana', 'ana', 'ana@ualberta.ca', ‘/main/static/frog.jpg‘, ‘thought-bubble.herokuapp.com’, ‘True’);

INSERT INTO Authors (author_uuid, name, username, email, location, status) VALUES(‘cc72b0113df247939c121ed2a28a895a’, ’Cameron’, ‘cameron’, ‘cameron@ualberta.ca’, ‘thought-bubble.herokuapp.com’, ‘True’);


INSERT INTO Friends (inviter_id, invitee_id, status) SELECT one.author_id, two.author_id, “True” FROM Authors one, Authors two WHERE one.username=‘daniel’ AND two.username=‘brian’;

INSERT INTO Friends (inviter_id, invitee_id, status) SELECT one.author_id, two.author_id, “True” FROM Authors one, Authors two WHERE one.username=‘brian’ AND two.username=‘cameron’;

INSERT INTO Posts (post_uuid, author_id, title, content, privacy) SELECT “b3cf34c4fb7944a0a7784958eb43aa5a”, author_id, “Daniel’s public post”, “Daniel’s thoughts here”, “public” FROM Authors WHERE username=‘daniel’;
INSERT INTO Posts (post_uuid, author_id, title, content, image, privacy) SELECT “6a0d7a3571e346b0b53697ff187d4821”, author_id, “Daniel’s public post with picture”, “Daniel’s thoughts here..and a pic”, “/main/static/frog.jpg”, “public” FROM Authors WHERE username=‘daniel’;
INSERT INTO Posts (post_uuid, author_id, title, content, privacy) SELECT “f572f76d727f492b811a44d68049be6b”, author_id, “Daniel’s private post”, “Daniel’s private post here”, “private” FROM Authors WHERE username=‘daniel’;
INSERT INTO Posts (post_uuid, author_id, title, content, privacy) SELECT “9130762761e74befab99ad99a53fcff5” ,author_id, “Ana’s public post”, “Ana’s thoughts here”, “public” FROM Authors WHERE username=‘ana’;
INSERT INTO Posts (post_uuid, author_id, title, content, privacy) SELECT “9130762761e74befab99d99a53fcff5”, author_id, “Cameron’s public post”, “Cameron’s thoughts here”, “public” FROM Authors WHERE username=‘cameron’;
INSERT INTO Posts (post_uuid, author_id, title, content, image, privacy) SELECT “65aefdeeb0544024a006a688bce50d7d”, author_id, “Cameron’s private post”, “Cameron’s post with a picture”, “/main/static/frog.jpg”, “private” FROM Authors WHERE username=‘cameron’;
INSERT INTO Posts (post_uuid, author_id, title, content, privacy) SELECT “ac65aa35840f43f39f650dcb89c05aeb”, author_id, “Brian’s public post”, “Brian’s thoughts here with a picture”, “public” FROM Authors WHERE username=‘brian’;
INSERT INTO Posts (post_uuid, author_id, title, content, image, privacy) SELECT “d46ac21b078c4f8eb6232769c91d75d5”, author_id, “Brian’s private post”, “Brian’s private post with a picture”, “/main/static/frog.jpg”, “private” FROM Authors WHERE username=‘brian’;
