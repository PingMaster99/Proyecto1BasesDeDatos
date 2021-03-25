# encoding: utf-8
import psycopg2 as psy
import datetime


class DatabaseConnection:
    def __init__(self):
        self.connection = psy.connect(
            database="music_test",
            user="postgres",
            password="1234"
        )
        self.cursor = self.connection.cursor()
        self.date = datetime.date.today().strftime('%Y-%m-%d')
        self.public_user_types = ["free", "artist/manager"]
        self.song_genres = ["a capella", "clasica", "country", "cristiana", "deep house", "electrónica", "edm",
                            "experimental", "house", "metal", "punk", "pop", "rock", "ranchera", "tropical"]

    # Database info

    def get_user_types(self):
        return self.public_user_types

    def get_available_genres(self):
        return self.song_genres

    # Login and registry

    def login(self, username, password):
        self.cursor.execute(f"SELECT * FROM users WHERE username = '{username}' AND user_password = '{password}'")
        user_data = self.cursor.fetchall()
        if len(user_data) > 0:
            user_data = list(user_data[0])
            last_login = str(user_data[5])
            user_type = user_data[6]

            # Free users
            if user_type == 'free':
                if last_login != self.date:
                    self.cursor.execute(f"UPDATE users SET available_songs = 3, last_login = '{self.date}'"
                                        f" WHERE username = '{username}'")
                    self.connection.commit()
                    user_data[5] = 3            # 3 available songs every day
                user_data.append(False)     # subscription status

            # Admins, subscribers, artists, and managers
            else:
                if last_login != self.date:
                    self.cursor.execute(f"UPDATE users SET last_login = '{self.date}'"
                                        f" WHERE username = '{username}'")
                if self.is_subscriber(username) or user_type == "admin":
                    user_data.append(True)
                else:
                    self.cursor.execute(f"UPDATE users SET available_songs = 3 WHERE username = '{username}'")
                    user_data[4] = 3
                    if user_type == "sub":
                        user_data[6] = "free"
                    user_data.append(False)

                self.connection.commit()

            return True, user_data

        return False, "La combinación usuario - contraseña no es correcta"

    def register(self, username, name, email, password, user_type="free"):

        if not self.validate_unique_username(username):
            return False, "El nombre de usuario ya existe"

        if not self.validate_unique_email(email):
            return False, "Ya hay un usuario asociado a ese correo"

        if len(password) < 8:
            return False, "Contraseña debe tener al menos 8 caracteres"

        try:
            self.cursor.execute(f"INSERT INTO users(username, personal_name, email, user_password, user_type) "
                                f"VALUES('{username}', '{name}', '{email}', '{password}', '{user_type}')")
            self.connection.commit()
            return True, "Se ha completado el registro"
        except Exception:
            return False, "Debe utilizar un correo válido"

    def validate_unique_username(self, username):
        try:
            self.cursor.execute(f"SELECT COUNT(*) FROM users WHERE username = '{username}'")
            username_count = self.cursor.fetchall()[0][0]
            return True if username_count == 0 else False
        except Exception:
            return False

    def validate_unique_email(self, email):
        self.cursor.execute(f"SELECT COUNT(*) FROM users WHERE email = '{email}'")
        email_count = self.cursor.fetchall()[0][0]
        return True if email_count == 0 else False

    # Song listening

    def can_listen_to_song(self, username, song):
        if self.is_subscriber(username) or self.is_admin(username):
            self.cursor.execute(f"""
            INSERT INTO song_listen(listening_user, song_listened) VALUES('{username}', {song})
            """)
            self.connection.commit()
            return True, "Reproduciendo canción"
        self.cursor.execute(f"""
        SELECT available_songs FROM users
        WHERE username = '{username}'
        """)
        songs_available = self.cursor.fetchall()[0][0]

        if songs_available <= 0:
            return False, "Ya ha llegado al límite de canciones por hoy con el plan gratuito"
        else:
            songs_available -= 1
            self.cursor.execute(f"""
            UPDATE users
            SET available_songs = {songs_available}
            WHERE username = '{username}'
            """)
            self.cursor.execute(f"""
            INSERT INTO song_listen(listening_user, song_listened) VALUES('{username}', {song})
            """)
            self.connection.commit()
            return True, "Reproduciendo canción"

    # Subscription

    def add_subscription(self, username, credit_card, cvv, billing_name, renewing=True):
        credit_card = credit_card.replace(' ', '')
        if self.validate_unique_username(username):
            return False, "No existe el usuario"
        if 13 > len(credit_card) or len(credit_card) > 19:
            return False, "Tarjeta de crédito errónea"
        if 3 > len(cvv) or len(cvv) > 4:
            return False, "Código cvv incorrecto"
        if billing_name is None or len(billing_name) == 0:
            return False, "Nombre incorrecto"

        try:
            self.cursor.execute(f"INSERT INTO subscriptions(username_id, credit_card, cvv, billing_name, renewing)"
                                f"VALUES('{username}', '{credit_card}', '{cvv}', '{billing_name}', {renewing})")

            self.cursor.execute(f"UPDATE users SET user_type = 'sub' WHERE username = '{username}' "
                                f"AND user_type = 'free'")

            self.cursor.execute(f"""
            UPDATE users SET available_songs = 3 WHERE username = '{username}'
            """)

            self.cursor.execute(f"""
            INSERT INTO financial_transaction(transaction_username) VALUES('{username}')
            """)

            self.connection.commit()

            return True, "Se ha añadido la suscripción"

        except Exception:
            return False, "Ya tiene una suscripción activa"

    def remove_subscription(self, username):

        try:
            self.cursor.execute(f"""UPDATE subscriptions SET renewing = False WHERE username_id='{username}'""")
            self.connection.commit()
            return True, "Se ha actualizado la suscripcion"
        except Exception:
            return False, "Revise sus credenciales"

    def is_subscriber(self, username):

        self.cursor.execute(f"SELECT subscription_end, renewing FROM subscriptions WHERE username_id = '{username}'")
        subscription = self.cursor.fetchall()

        if len(subscription) == 0:
            return False

        subscription = subscription[0]
        date_of_expiration = str(subscription[0])
        renewing = subscription[1]
        current_date = datetime.datetime.strptime(self.date, '%Y-%m-%d')

        if datetime.datetime.strptime(date_of_expiration, '%Y-%m-%d') < current_date:
            if not renewing:
                self.cursor.execute(f"DELETE FROM subscriptions WHERE username_id = '{username}'")
                self.cursor.execute(f"UPDATE users SET user_type = 'free' WHERE user_type = 'sub' AND username = '{username}'")
                self.connection.commit()
                return False
            else:
                current_date_format = self.date.split('-')
                day_of_expiration = date_of_expiration.split('-')[2]
                end_date = datetime.datetime.strptime(f"{current_date_format[0]}-{current_date_format[1]}-{day_of_expiration}", '%Y-%m-%d')
                self.cursor.execute(f"UPDATE subscriptions SET subscription_end = {end_date} WHERE username_id = '{username}'")
                self.connection.commit()
                return True
        else:
            return True

    def is_admin(self, username):
        self.cursor.execute(f"""
        SELECT * FROM users WHERE username = '{username}' AND user_type = 'admin'
        """)

        return len(self.cursor.fetchall()) != 0

    # Playlists

    def make_new_playlist(self, username, playlist_name):
        if len(playlist_name) <= 0:
            return False, "Debe introducir un nombre"
        try:
            self.cursor.execute(f"""
            INSERT INTO playlist(playlist_name, owner_username) VALUES('{playlist_name}', '{username}')
            """)
            self.connection.commit()
            return True, "Lista de reproducción creada con éxito"
        except Exception:
            return False, "Ya tienes una lista con ese nombre"

    def get_user_playlists(self, username):
        self.cursor.execute(f"""
        SELECT playlist_name, playlist_id 
        FROM playlist
        WHERE owner_username = '{username}'
        """)
        return self.cursor.fetchall()

    def get_playlist_songs(self, username, playlist_name):
        self.cursor.execute(f"""
        SELECT song_id, song_name, personal_name AS artist
        FROM users INNER JOIN 
        (album INNER JOIN (song INNER JOIN (playlist INNER JOIN playlist_association ON playlist_id = parent_playlist) 
		ON playlist_song = song_id) ON album_id = album_parent_id) ON username = artist_username
		WHERE owner_username = '{username}' AND playlist_name = '{playlist_name}'
		ORDER BY date_added, time_added 
        """)
        return self.cursor.fetchall()

    def add_playlist_song(self, playlist_id, song_id):
        try:
            self.cursor.execute(f"""
            INSERT INTO playlist_association(parent_playlist, playlist_song) VALUES({playlist_id}, {song_id})
            """)
            self.connection.commit()
            return True, "Se ha añadido la canción"
        except Exception:
            return False, "No ha sido posible actualizar"

    # Artist / manager additions

    def add_track(self, song_name, genre, album_id):

        try:
            self.cursor.execute(f"""
            INSERT INTO song(album_parent_id, song_name, genre) VALUES({album_id}, '{song_name}', '{genre}')
            """)
            self.connection.commit()
            return True, "Se ha añadido la canción"
        except Exception:
            return False, "La canción añadida tiene el mismo nombre que una anterior"

    def add_album(self, username, album_name):
        try:
            self.cursor.execute(f"""
            INSERT INTO album(album_name, artist_username) VALUES('{album_name}', '{username}')
            """)
            self.connection.commit()
            return True, "Se ha añadido el álbum"
        except Exception:
            return False, "No ha sido posible añadir el álbum"

    # Song search

    def get_albums(self, username):
        self.cursor.execute(f"""
        SELECT album_id, album_name
        FROM album
        WHERE artist_username = '{username}'
        ORDER BY album_date, published_time DESC
        """)
        return self.cursor.fetchall()

    def get_album_songs(self, album_name):
        self.cursor.execute(f"""
        SELECT song_id, song_name, personal_name AS artist, song_date 
        FROM (song INNER JOIN (album INNER JOIN users ON username = artist_username) ON album_id = album_parent_id) 
        INNER JOIN (
            SELECT song_listened AS song, COUNT(song_listened) AS listeners
            FROM song_listen 
            WHERE date_listened >= (CURRENT_DATE - INTERVAL '3 mon')
            GROUP BY song_listened
        )AS listened_songs ON song = song_id
        WHERE album_name ~* '({album_name}|{album_name[0: len(album_name) // 2]})' AND active = True
        UNION
        SELECT song_id, song_name, personal_name AS artist, song_date 
        FROM (song INNER JOIN (album INNER JOIN users ON username = artist_username) ON album_id = album_parent_id)
        WHERE album_name ~* '({album_name}|{album_name[0: len(album_name) // 2]})' AND active = True
        LIMIT 100;
        """)
        return self.cursor.fetchall()

    def get_songs(self, song_name):
        self.cursor.execute(f"""
        SELECT song_id, song_name, personal_name AS artist, song_date, genre
        FROM (song INNER JOIN (album INNER JOIN users ON username = artist_username) ON album_id = album_parent_id) 
        INNER JOIN (
            SELECT song_listened AS song, COUNT(song_listened) AS listeners
            FROM song_listen 
            WHERE date_listened >= (CURRENT_DATE - INTERVAL '3 mon')
            GROUP BY song_listened
        )AS listened_songs ON song = song_id
        WHERE song_name ~* '({song_name}|{song_name[0: len(song_name) // 2]})' AND active = True
        UNION
        SELECT song_id, song_name, personal_name AS artist, song_date, genre
        FROM (song INNER JOIN (album INNER JOIN users ON username = artist_username) ON album_id = album_parent_id)
        WHERE song_name ~* '({song_name}|{song_name[0: len(song_name) // 2]})' AND active = True
        LIMIT 100;
        """)
        return self.cursor.fetchall()

    def get_artist_songs(self, artist_name):
        self.cursor.execute(f"""
        SELECT song_id, song_name, personal_name AS artist, song_date 
        FROM (song INNER JOIN (album INNER JOIN users ON username = artist_username) ON album_id = album_parent_id) 
        INNER JOIN (
            SELECT song_listened AS song, COUNT(song_listened) AS listeners
            FROM song_listen 
            WHERE date_listened >= (CURRENT_DATE - INTERVAL '3 mon')
            GROUP BY song_listened
        )AS listened_songs ON song = song_id
        WHERE personal_name ~* '({artist_name}|{artist_name[0: len(artist_name) // 2]})' AND active = True
        UNION
        SELECT song_id, song_name, personal_name AS artist, song_date 
        FROM (song INNER JOIN (album INNER JOIN users ON username = artist_username) ON album_id = album_parent_id)
        WHERE personal_name ~* '({artist_name}|{artist_name[0: len(artist_name) // 2]})' AND active = True
        LIMIT 100;
        """)
        return self.cursor.fetchall()

    def get_genre_songs(self, genre_name):

        self.cursor.execute(f"""
        SELECT song_id, song_name, personal_name AS artist, song_date, genre 
        FROM (song INNER JOIN (album INNER JOIN users ON username = artist_username) ON album_id = album_parent_id) 
        INNER JOIN (
            SELECT song_listened AS song, COUNT(song_listened) AS listeners
            FROM song_listen 
            WHERE date_listened >= (CURRENT_DATE - INTERVAL '3 mon')
            GROUP BY song_listened
        )AS listened_songs ON song = song_id
        WHERE genre ~* '({genre_name}|{genre_name[0: len(genre_name) // 2]})' AND active = True
        UNION
        SELECT song_id, song_name, personal_name AS artist, song_date, genre
        FROM (song INNER JOIN (album INNER JOIN users ON username = artist_username) ON album_id = album_parent_id)
        WHERE genre ~* '({genre_name}|{genre_name[0: len(genre_name) // 2]})' AND active = True
        LIMIT 100
        """)
        return self.cursor.fetchall()

    # Album and artist search

    def get_artist_by_name(self, name):
        try:
            self.cursor.execute(f"""
            SELECT username, personal_name, email, user_type
            FROM users
            WHERE personal_name ~* '({name}|{name[0: len(name) // 2]})'
            AND user_type = 'artist/manager'
            """)

            return self.cursor.fetchall()
        except Exception:
            return []

    def get_album_by_name(self, album_name):
        self.cursor.execute(f"""
        SELECT album_id, album_name, personal_name, username
        FROM album INNER JOIN users ON username = artist_username
        WHERE album_name ~* '({album_name}|{album_name[0: len(album_name) // 2]})'
        """)

        return self.cursor.fetchall()

    # Deactivation

    def deactivate_song(self, song_id, active=False):
        try:
            self.cursor.execute(f"""
            UPDATE song SET active = {active}
            WHERE song_id = {song_id}
            """)
            self.connection.commit()
            return True, "Se ha cambiado la canción"
        except Exception:
            return False, "No se ha podido actualizar"

    # Deletions

    def delete_song(self, song_id):
        try:
            self.cursor.execute(f"""
            DELETE FROM song WHERE song_id = {song_id}
            """)
            self.connection.commit()
            return True, "Se ha borrado la canción"
        except Exception:
            return False, "No se ha borrado la canción"

    def delete_artist(self, artist_username):
        try:
            self.cursor.execute(f"""
            DELETE FROM users WHERE username = {artist_username}
            """)
            self.connection.commit()
            return True, "Se ha borrado el artista"
        except Exception:
            return False, "No se ha borrado el artista"

    def delete_album(self, album_id):
        try:
            self.cursor.execute(f"""
            DELETE FROM album WHERE album_id = {album_id}
            """)
            self.connection.commit()
            return True, "Se ha borrado el álbum"
        except Exception:
            return False, "No se ha borrado el álbum"

    # Updates

    def update_user_type(self, username, new_type="artist/manager", name=None):
        if self.validate_unique_username(username):
            return False, f"No existe el usuario {username}"
        try:
            if name is not None:
                self.cursor.execute(f"""
                UPDATE users 
                SET personal_name = '{name}', user_type = '{new_type}'
                WHERE username = '{username}'
                """)
            else:
                self.cursor.execute(f"""
                UPDATE users 
                SET user_type = '{new_type}'
                WHERE username = '{username}'
                """)
            self.connection.commit()
            return True, "Se ha actualizado el usuario"
        except Exception:
            return False, "Ha ocurrido un error"

    def update_artist(self, username, artist_name, email, user_type="artist/manager"):
        if user_type == "admin":
            return False, "No se puede asignar a un artista como administrador"

        try:
            self.cursor.execute(f"""
            UPDATE users 
            SET personal_name = '{artist_name}', 
            email = '{email}',
            user_type = '{user_type}'
            WHERE username = '{username}'
            """)
            self.connection.commit()
            return True, "Se ha actualizado al artista"
        except Exception:
            return False, "No se ha podido actualizar. Revise que los campos sean correctos"

    def update_album(self, album_id, album_name):
        try:
            self.cursor.execute(f"""
            UPDATE album
            SET album_name = '{album_name}'
            WHERE album_id = {album_id}
            """)
            self.connection.commit()
            return True, "Se ha actualizado el álbum"
        except Exception:
            return False, "No se ha podido actualizar. Revise que el álbum no sea repetido"

    def update_song(self, song_id, song_name, genre, active=True):
        try:
            self.cursor.execute(f"""
            UPDATE song 
            SET song_name = '{song_name}',
            genre = '{genre}',
            active = {active}
            WHERE song_id = {song_id}
            """)
            self.connection.commit()
            return True, "Se ha actualizado la canción"
        except Exception:
            return False, "No se ha podido actualizar"

    # Direct query !! WARNING DON'T USE IF NOT TRAINED !!

    def direct_database_query(self, query):
        try:
            self.cursor.execute(query)
            return True
        except Exception:
            return False

    # Analytics

    def get_most_recent_albums(self):
        self.cursor.execute(f"""
        SELECT album_name, personal_name, username 
        FROM users INNER JOIN album
        ON username = artist_username
        WHERE album_date >= (CURRENT_DATE - INTERVAL '7 days')
        ORDER BY album_date DESC, published_time DESC
        LIMIT 100
        """)
        return self.cursor.fetchall()

    def get_most_popular_artists(self):
        self.cursor.execute(f"""
        SELECT personal_name AS artist, username, listeners 
        FROM users INNER JOIN (
            SELECT username u2 , COUNT(song_listened) AS listeners 
            FROM users INNER JOIN (album INNER JOIN (song_listen INNER JOIN song ON song_id = song_listened) 
            ON album_parent_id = album_id) 
            ON artist_username = username WHERE date_listened >= (CURRENT_DATE - INTERVAL '3 mon') 
            GROUP BY username
        ) AS song_count ON username = u2 
        ORDER BY listeners DESC
        LIMIT 100	
        """)
        return self.cursor.fetchall()

    def get_new_subscriptions(self):
        self.cursor.execute(f"""
        SELECT COUNT(*)
        FROM financial_transaction
        WHERE transaction_date >= (CURRENT_DATE - INTERVAL '6 mon')
        """)
        return self.cursor.fetchall()[0][0]

    def get_artists_with_most_songs(self):
        self.cursor.execute(f"""
        SELECT personal_name, username, number_of_songs 
        FROM users INNER JOIN (
            SELECT username u2, COUNT(*) AS number_of_songs
            FROM users INNER JOIN (song INNER JOIN album ON album_parent_id = album_id) ON artist_username = username
            GROUP BY username
        ) AS music_production ON username = u2
        ORDER BY number_of_songs DESC
        LIMIT 100
        """)
        return self.cursor.fetchall()

    def get_most_popular_genres(self):
        self.cursor.execute(f"""
        SELECT genre, listeners 
        FROM (
            SELECT genre, COUNT(song_listened) AS listeners 
            FROM users INNER JOIN (album INNER JOIN (song_listen INNER JOIN song ON song_id = song_listened) 
            ON album_parent_id = album_id) 
            ON artist_username = username WHERE date_listened >= (CURRENT_DATE - INTERVAL '6 mon') 
            GROUP BY genre
        ) AS listener_table 
        ORDER BY listeners DESC
        LIMIT 100
        """)
        return self.cursor.fetchall()

    def get_most_active_users(self):
        self.cursor.execute(f"""
        SELECT username, COUNT(username) AS listened_songs
        FROM users INNER JOIN song_listen
        ON listening_user = username
        WHERE date_listened >= (CURRENT_DATE - INTERVAL '1 mon')
        GROUP BY username
        ORDER BY listened_songs DESC
        LIMIT 100
        """)
        return self.cursor.fetchall()

    # Closing the database

    def close(self):
        self.connection.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


