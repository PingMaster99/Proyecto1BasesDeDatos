CREATE TABLE users(username VARCHAR(50) PRIMARY KEY, personal_name VARCHAR(100) NOT NULL, 
					  email VARCHAR(100) CONSTRAINT proper_email CHECK (email ~* '^[A-Za-z0-9._%-]+@[A-Za-z0-9.-]+[.][A-Za-z]+$'), user_password VARCHAR(50) NOT NULL, 
				      available_songs SMALLINT DEFAULT 3, last_login DATE NOT NULL DEFAULT CURRENT_DATE, 
					  user_type VARCHAR(20) NOT NULL DEFAULT 'free');
				  
CREATE TABLE playlist(playlist_id BIGSERIAL PRIMARY KEY, playlist_name VARCHAR(100) NOT NULL, owner_username VARCHAR(50) NOT NULL, UNIQUE(playlist_name, username),
					 FOREIGN KEY (username)
					 REFERENCES users(username)
					 ON DELETE CASCADE
					 ON UPDATE CASCADE);

CREATE TABLE album(album_id BIGSERIAL PRIMARY KEY, album_name VARCHAR(100) NOT NULL, album_date DATE NOT NULL DEFAULT CURRENT_DATE, published_time TIME NOT NULL DEFAULT NOW(), 
				     artist_username VARCHAR(50) NOT NULL, 
				     UNIQUE(album_name, artist_username),
				     FOREIGN KEY (artist_username)
				     REFERENCES users(username)
				     ON DELETE CASCADE
				     ON UPDATE CASCADE);
					  
CREATE TABLE song(song_id BIGSERIAL PRIMARY KEY, album_parent_id BIGINT, song_name VARCHAR(100), genre VARCHAR(50), 
				    song_date DATE NOT NULL DEFAULT CURRENT_DATE, active BOOL DEFAULT True, song_added_time TIME NOT NULL DEFAULT NOW(),
				    UNIQUE(album_parent_id, song_name),
				    FOREIGN KEY (album_parent_id)
			 	    REFERENCES album(album_id)
				    ON DELETE CASCADE
				    ON UPDATE CASCADE);

CREATE TABLE playlist_association(parent_playlist BIGINT NOT NULL, playlist_song BIGINT NOT NULL, date_added DATE NOT NULL DEFAULT CURRENT_DATE, 
					time_added TIME NOT NULL DEFAULT NOW(),
				    FOREIGN KEY (parent_playlist) 
				    REFERENCES playlist(playlist_id)
				    ON DELETE CASCADE
					ON UPDATE CASCADE,

					FOREIGN KEY (playlist_song)
					REFERENCES song(song_id)
					ON DELETE CASCADE
					ON UPDATE CASCADE);

CREATE TABLE subscriptions(username_id VARCHAR(50) PRIMARY KEY, subscription_end DATE NOT NULL DEFAULT CURRENT_DATE + INTERVAL '1 mon', 
	  credit_card VARCHAR(19) NOT NULL CHECK (char_length(credit_card) >= 13), cvv VARCHAR(4) NOT NULL CHECK (char_length(cvv) >= 3),
	  billing_name VARCHAR(200) NOT NULL, renewing BOOL DEFAULT True, 
	  FOREIGN KEY (username_id)
	  REFERENCES users(username)
	  ON DELETE CASCADE
	  ON UPDATE CASCADE);
	  
CREATE TABLE song_listen(listening_user VARCHAR(50) NOT NULL, song_listened BIGINT NOT NULL, date_listened DATE NOT NULL DEFAULT CURRENT_DATE,
						FOREIGN KEY (listening_user)
						REFERENCES users(username)
						ON DELETE SET NULL
						ON UPDATE CASCADE,
						
						FOREIGN KEY (song_listened)
						REFERENCES song(song_id)
						ON DELETE CASCADE
						ON UPDATE CASCADE);
						
CREATE TABLE financial_transaction(transaction_id BIGSERIAL PRIMARY KEY, transaction_username VARCHAR(50), transaction_type VARCHAR(20) DEFAULT 'subscription',
						transaction_date DATE DEFAULT CURRENT_DATE,
						FOREIGN KEY (transaction_username)
						REFERENCES users(username)
						ON DELETE SET NULL
						ON UPDATE CASCADE);