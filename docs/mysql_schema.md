## Data Schema
### users

```
CREATE TABLE `users` (
	`id` int(11) NOT NULL AUTO_INCREMENT,
	`email` varchar(64) DEFAULT NULL,
	`username` varchar(64) NOT NULL,
	`role_id` int(11) NOT NULL,
	`password_hash` varchar(128) NOT NULL,
	`confirmed` tinyint(1) NOT NULL DEFAULT '0',
	`name` varchar(64) NOT NULL,
	`location` varchar(64) DEFAULT NULL,
	`about_me` varchar(1024) DEFAULT "",
	`member_since` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
	`last_seen` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	`avatar_hash` varchar(32) DEFAULT NULL,
	PRIMARY KEY (`id`),
	UNIQUE `unique_index`(`username`, `password_hash`, `role_id`)
)
```