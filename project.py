# encoding: utf-8
import tkinter as tk
from tkinter import *
from tkinter import ttk
import DatabaseConnection
import MusicPlayer

user = {}
song_buttons = []
stats_buttons = []
playlist_buttons = []
playlist_song_buttons = []
playlist_selection_buttons = []
editing_buttons = []
album_buttons = []

last_song = []
editing_id = []

db = DatabaseConnection.DatabaseConnection()
music = MusicPlayer.MusicPlayer()

SONG_GENRES = db.get_available_genres()
BG_COLOR = "#000000"
BUTTON_COLOR = "#9fcc2e"


def validate_login():
    valid, user_data = db.login(t_uname_login.get(), t_password_login.get())
    if valid:
        login_error_code['text'] = ""
        t_uname_login.delete(0, END)
        t_password_login.delete(0, END)
        user['username'] = user_data[0]
        user['name'] = user_data[1]
        user['email'] = user_data[2]
        user['available_songs'] = user_data[4]
        user['type'] = user_data[6]
        user['subscribed'] = user_data[7]
        set_buttons_for_user_type()
        show_frame(search_menu)
    else:
        login_error_code['text'] = user_data


def restore_login_buttons():

    search_type.place(x=130, y=50, anchor="center")

    search_field.place(x=300, y=50, anchor="center")

    log_off_button.place(x=550, y=20, anchor="center")

    search_button.place(x=450, y=50, anchor="center")

    edit_mode_check.place(x=300, y=80, anchor="center")

    stats_button.place(x=300, y=150, anchor="center")

    add_album_button.place(x=300, y=200, anchor="center")

    become_artist_button.place(x=300, y=225, anchor="center")

    add_song_button.place(x=300, y=250, anchor="center")

    subscribe_button.place(x=300, y=300, anchor="center")

    create_playlist_button.place(x=300, y=300, anchor="center")

    cancel_subscription_button.place(x=450, y=350, anchor="center")

    view_playlists_button.place(x=300, y=350, anchor="center")

    add_to_playlist_button_nice.place(x=0, y=50)


def set_buttons_for_user_type():

    user_type = user['type']
    subscribed = user['subscribed']
    edit_mode_check.option_clear()

    if user_type == "free":
        view_playlists_button.place_forget()
        stats_button.place_forget()
        edit_mode_check.place_forget()
        add_album_button.place_forget()
        add_song_button.place_forget()
        create_playlist_button.place_forget()
        cancel_subscription_button.place_forget()
        add_to_playlist_button_nice.place_forget()

    elif user_type == "admin":
        view_playlists_button.place_forget()
        add_album_button.place_forget()
        become_artist_button.place_forget()
        add_song_button.place_forget()
        subscribe_button.place_forget()
        create_playlist_button.place_forget()
        cancel_subscription_button.place_forget()
        add_to_playlist_button_nice.place_forget()

    elif user_type == "artist/manager":
        stats_button.place_forget()
        edit_mode_check.place_forget()
        become_artist_button.place_forget()

        if subscribed:
            subscribe_button.place_forget()
        else:
            view_playlists_button.place_forget()
            cancel_subscription_button.place_forget()
            create_playlist_button.place_forget()
            add_to_playlist_button_nice.place_forget()

    elif user_type == "sub":
        stats_button.place_forget()
        edit_mode_check.place_forget()
        add_album_button.place_forget()
        add_song_button.place_forget()
        subscribe_button.place_forget()


def log_off():
    restore_login_buttons()
    show_frame(login)
    music.stop()


def register_on_database():
    valid, message = db.register(t_uname_register.get(), t_name_register.get(), t_email_register.get(),
                                 t_password_register.get())
    if valid:

        t_uname_register.delete(0, END)
        t_password_register.delete(0, END)
        t_name_register.delete(0, END)
        t_email_register.delete(0, END)
        user['username'] = t_uname_register.get()
        user['name'] = t_name_register.get()
        user['email'] = t_email_register.get()
        user['available_songs'] = 3
        user['type'] = "free"
        user['subscribed'] = False
        set_buttons_for_user_type()
        show_frame(login)
    else:
        t_error_register['text'] = message


def subscribe():
    subscribing_user = user['username']
    valid, message = db.add_subscription(subscribing_user, subscribe_credit_field.get(), subscribe_cvv_field.get(),
                                         subscribe_name_field.get())
    if valid:
        log_off()
    else:
        subscription_error_message['text'] = message


def enter_search(event):
    search_for_songs()


def search_for_songs():
    editing = edit_mode.get() == 1
    selected_type = selected_search.get()
    forget_previous_button_state(editing_buttons)
    forget_previous_button_state(song_buttons)

    if not editing:

        if selected_type == "cancion":
            songs_found = db.get_songs(search_field.get())
        elif selected_type == "album":
            songs_found = db.get_album_songs(search_field.get())
        elif selected_type == "genero":
            songs_found = db.get_genre_songs(search_field.get())
        else:
            songs_found = db.get_artist_songs(search_field.get())

        if len(songs_found) > 0:
            current_row = 0
            for song in songs_found:
                song_button = Button(second_frame, bg=BUTTON_COLOR, text=f"{song[1]} | {song[2]}",
                                     command=lambda x=(song[0], song[1], song[2]): press_song(x))
                song_buttons.append(song_button)
                song_button.grid(row=current_row, column=0, pady=0, padx=200)

                current_row += 1
    else:

        current_row = 0
        if selected_type == "cancion":
            editing_field = db.get_songs(search_field.get())
            if len(editing_field) > 0:

                for edit_field in editing_field:
                    song_button = Button(second_frame, bg=BUTTON_COLOR, text=f"{edit_field[1]} | {edit_field[2]}",
                                         command=lambda x=(edit_field[0], edit_field[1], edit_field[4]): edit_song(x))
                    editing_buttons.append(song_button)
                    song_button.grid(row=current_row, column=0, pady=0, padx=100)

                    current_row += 1

        elif selected_type == "album":
            editing_field = db.get_album_by_name(search_field.get())
            if len(editing_field) > 0:
                for edit_field in editing_field:
                    song_button = Button(second_frame, bg=BUTTON_COLOR, text=f"{edit_field[1]} | {edit_field[2]}",
                                         command=lambda x=(edit_field[0], edit_field[1]): edit_album(x))
                    editing_buttons.append(song_button)
                    song_button.grid(row=current_row, column=0, pady=0, padx=100)

                    current_row += 1

        elif selected_type == "genero":
            editing_field = db.get_genre_songs(search_field.get())
            if len(editing_field) > 0:
                for edit_field in editing_field:
                    song_button = Button(second_frame, bg=BUTTON_COLOR, text=f"{edit_field[1]} | {edit_field[2]}",
                                         command=lambda x=(edit_field[0], edit_field[1], edit_field[4]): edit_song(x))
                    editing_buttons.append(song_button)
                    song_button.grid(row=current_row, column=0, pady=0, padx=100)

                    current_row += 1
        else:

            editing_field = db.get_artist_by_name(search_field.get())
            if len(editing_field) > 0:
                for edit_field in editing_field:
                    song_button = Button(second_frame, bg=BUTTON_COLOR, text=f"{edit_field[0]} | {edit_field[1]}",
                                         command=lambda x=(
                                         edit_field[0], edit_field[1], edit_field[2], edit_field[3]): edit_artist(x))
                    editing_buttons.append(song_button)
                    song_button.grid(row=current_row, column=0, pady=0, padx=100)

                    current_row += 1
    show_frame(song_list)


def edit_artist(artist_data):
    editing_id.clear()
    editing_id.append(artist_data[0])
    artist_edit_title['text'] = f"Editando al artista con usuario {artist_data[0]}"

    artist_name_edit.delete(0, END)
    artist_name_edit.insert(0, artist_data[1])

    artist_email_edit.delete(0, END)
    artist_email_edit.insert(0, artist_data[2])

    show_frame(edit_artist_screen)


def update_artist():
    if len(editing_id) > 0:
        db.update_artist(editing_id[0], artist_name_edit.get(), artist_email_edit.get(), artist_edit_type.get())
        editing_id.clear()
    show_frame(search_menu)


def delete_artist():
    if len(editing_id) > 0:
        db.delete_artist(editing_id[0])
        editing_id.clear()
    show_frame(search_menu)


def edit_album(album_data):
    editing_id.clear()
    editing_id.append(album_data[0])

    album_name_edit.delete(0, END)
    album_name_edit.insert(0, album_data[1])

    show_frame(edit_album_screen)


def update_album():
    if len(editing_id) > 0:
        db.update_album(editing_id[0], album_name_edit.get())
        editing_id.clear()
        show_frame(search_menu)


def delete_album():
    if len(editing_id) > 0:
        db.delete_album(editing_id[0])
        editing_id.clear()
        show_frame(search_menu)


def edit_song(song_data):
    editing_id.clear()
    editing_id.append(song_data[0])

    song_name_edit.delete(0, END)
    song_genre_edit.delete(0, END)

    song_name_edit.insert(0, song_data[1])
    song_genre_edit.insert(0, song_data[2])

    show_frame(edit_song_screen)


def update_song():
    if len(editing_id) > 0:
        db.update_song(editing_id[0], song_name_edit.get(), song_genre_edit.get())
        editing_id.clear()
        show_frame(search_menu)


def delete_song():
    if len(editing_id) > 0:
        db.delete_song(editing_id[0])
        editing_id.clear()
        show_frame(search_menu)


def deactivate_song():
    if len(editing_id) > 0:
        db.deactivate_song(editing_id[0])
        editing_id.clear()
        show_frame(search_menu)


def press_song(song):
    valid, message = db.can_listen_to_song(user['username'], song[0])
    if valid:
        last_song.clear()
        last_song.append(song[0])
        music.play_song(song[2], song[1])
    else:
        scroll_error_message['text'] = message


def show_stats():
    show_most_recent_albums()
    show_frame(stats_screen)


def show_most_recent_albums():
    current_albums = db.get_most_recent_albums()
    forget_previous_button_state(stats_buttons)

    if len(current_albums) > 0:
        current_row = 0
        for album in current_albums:
            song_button = Button(stats_second_frame, bg=BUTTON_COLOR,
                                 text=f"Nombre: {album[0]} | Artista: {album[1]} | Usuario: {album[2]}")
            stats_buttons.append(song_button)
            song_button.grid(row=current_row, column=0, pady=0, padx=100)

            current_row += 1


def show_growing_artists():
    growing_artists = db.get_most_popular_artists()
    forget_previous_button_state(stats_buttons)
    if len(growing_artists) > 0:
        current_row = 0
        for artist in growing_artists:
            song_button = Button(stats_second_frame, bg=BUTTON_COLOR,
                                 text=f"Nombre: {artist[0]} | Usuario: {artist[1]} | Escuchado {artist[2]}")
            stats_buttons.append(song_button)
            song_button.grid(row=current_row, column=0, pady=0, padx=100)

            current_row += 1


def show_subscription_amount():
    subscription_count = db.get_new_subscriptions()
    forget_previous_button_state(stats_buttons)

    button = Button(stats_second_frame, bg=BUTTON_COLOR, text=f"{subscription_count} suscripciones en los últimos 6 meses")
    stats_buttons.append(button)
    button.grid(row=0, column=0, pady=0, padx=100)


def show_artists_with_most_music():
    artists = db.get_artists_with_most_songs()
    forget_previous_button_state(stats_buttons)

    if len(artists) > 0:
        current_row = 0
        for artist in artists:
            song_button = Button(stats_second_frame, bg=BUTTON_COLOR,
                                 text=f"Nombre: {artist[0]} | Usuario: {artist[1]} | Canciones: {artist[2]}")
            stats_buttons.append(song_button)
            song_button.grid(row=current_row, column=0, pady=0, padx=100)

            current_row += 1


def show_popular_genres():
    genres = db.get_most_popular_genres()
    forget_previous_button_state(stats_buttons)

    if len(genres) > 0:
        current_row = 0
        for genre in genres:
            song_button = Button(stats_second_frame, bg=BUTTON_COLOR, text=f"Género: {genre[0]} | Escuchado: {genre[1]}")
            stats_buttons.append(song_button)
            song_button.grid(row=current_row, column=0, pady=0, padx=100)

            current_row += 1


def show_most_active_users():
    users = db.get_most_active_users()
    forget_previous_button_state(stats_buttons)

    if len(users) > 0:
        current_row = 0
        for found_user in users:
            song_button = Button(stats_second_frame, bg=BUTTON_COLOR,
                                 text=f"Usuario: {found_user[0]} | Canciones escuchadas: {found_user[1]}")
            stats_buttons.append(song_button)
            song_button.grid(row=current_row, column=0, pady=0, padx=100)

            current_row += 1


def create_playlist():
    current_user = user['username']

    valid, message = db.make_new_playlist(current_user, playlist_name_field.get())
    if valid:
        show_frame(search_menu)
    else:
        new_playlist_error_message['text'] = message


def show_playlists():
    current_user = user['username']
    user_playlists = db.get_user_playlists(current_user)
    forget_previous_button_state(playlist_buttons)
    if len(user_playlists) > 0:
        current_row = 0
        for playlist in user_playlists:
            song_button = Button(second_playlist_frame, bg=BUTTON_COLOR, text=f"{playlist[0]}",
                                 command=lambda x=(playlist[0], current_user): expand_playlist(x))
            playlist_buttons.append(song_button)
            song_button.grid(row=current_row, column=0, pady=0, padx=100)

            current_row += 1
        show_frame(playlist_screen)


def expand_playlist(fetch_data):
    songs_in_playlist = db.get_playlist_songs(fetch_data[1], fetch_data[0])
    forget_previous_button_state(playlist_song_buttons)
    if len(songs_in_playlist) > 0:
        current_row = 0
        for song in songs_in_playlist:
            song_button = Button(song_playlist_frame, bg=BUTTON_COLOR, text=f"{song[1]} | {song[2]}",
                                 command=lambda x=(song[0], song[1], song[2]): press_song(x))
            playlist_song_buttons.append(song_button)
            song_button.grid(row=current_row, column=0, pady=0, padx=100)

            current_row += 1

    show_frame(playlist_song_screen)


def insert_song_into_playlist():
    current_user = user['username']
    user_playlists = db.get_user_playlists(current_user)
    forget_previous_button_state(playlist_selection_buttons)

    if len(user_playlists) > 0:
        current_row = 0
        for playlist in user_playlists:
            song_button = Button(playlist_selection_frame, bg=BUTTON_COLOR, text=f"{playlist[0]}",
                                 command=lambda x=playlist[1]: playlist_insert_song(x))
            playlist_selection_buttons.append(song_button)
            song_button.grid(row=current_row, column=0, pady=0, padx=100)

            current_row += 1
    show_frame(add_to_playlist_screen)


def playlist_insert_song(playlist_id):
    if len(last_song) > 0:
        db.add_playlist_song(playlist_id, last_song[0])
        last_song.clear()
    show_frame(search_menu)


def become_artist():
    username = user['username']
    artistic_name = artistic_name_edit.get()
    if len(artistic_name) <= 0:
        artistic_name = None
    valid, message = db.update_user_type(username, name=artistic_name)
    print(message)
    log_off()


def add_album():
    username = user['username']
    if len(new_album_name.get()) > 0:
        db.add_album(username, new_album_name.get())
    show_frame(search_menu)


def add_song():
    username = user['username']
    song_name = new_song_name.get()
    song_genre = selected_song_genre.get()
    if len(song_name) > 0:
        albums = db.get_albums(username)
        if len(albums) > 0:
            current_row = 0
            for album in albums:
                song_button = Button(album_selection_frame, bg=BUTTON_COLOR, text=f"{album[0]} | {album[1]}",
                                     command=lambda x=(song_name, song_genre, album[0]): add_song_with_album(x))
                album_buttons.append(song_button)
                song_button.grid(row=current_row, column=0, pady=0, padx=100)

                current_row += 1
        show_frame(album_selection_screen)


def add_song_with_album(query_data):
    db.add_track(query_data[0], query_data[1], query_data[2])
    show_frame(search_menu)


def add_song_without_album():
    username = user['username']
    song_name = new_song_name.get()
    song_genre = selected_song_genre.get()
    album_name = f"{song_name} (single)"
    db.add_album(username, album_name)
    most_recent_album_id = db.get_albums(username)[0][0]
    db.add_track(song_name, song_genre, most_recent_album_id)
    show_frame(search_menu)


def cancel_sub():
    username = r_t_uname_login.get()
    password = r_password_login.get()
    valid, data = db.login(username, password)
    if valid:
        db.remove_subscription(username)
        show_frame(search_menu)
        r_error_code['text'] = ""
    else:
        r_error_code['text'] = data


def forget_previous_button_state(buttons):
    for button in buttons:
        button.grid_forget()

    buttons.clear()


def show_frame(frame):
    frame.tkraise()


window = Tk()
window.geometry("600x500")


window.rowconfigure(0, weight=1)
window.columnconfigure(0, weight=1)

"""
Frames
"""

login = tk.Frame(window, bg=BG_COLOR)

register = tk.Frame(window, bg=BG_COLOR)

search_menu = tk.Frame(window, bg=BG_COLOR)

song_list = tk.Frame(window, bg=BG_COLOR)

songs = tk.Frame(window, bg=BG_COLOR)

stats_screen = tk.Frame(window, bg=BG_COLOR)

subscribe_screen = tk.Frame(window, bg=BG_COLOR)

make_playlist_screen = tk.Frame(window, bg=BG_COLOR)

playlist_screen = tk.Frame(window, bg=BG_COLOR)

playlist_song_screen = tk.Frame(window, bg=BG_COLOR)

add_to_playlist_screen = tk.Frame(window, bg=BG_COLOR)

edit_song_screen = tk.Frame(window, bg=BG_COLOR)

edit_album_screen = tk.Frame(window, bg=BG_COLOR)

edit_artist_screen = tk.Frame(window, bg=BG_COLOR)

become_artist_screen = tk.Frame(window, bg=BG_COLOR)

add_album_screen = tk.Frame(window, bg=BG_COLOR)

add_song_screen = tk.Frame(window, bg=BG_COLOR)

album_selection_screen = tk.Frame(window, bg=BG_COLOR)

remove_subscription_screen = tk.Frame(window, bg=BG_COLOR)

for frame in (login, register, song_list, songs, search_menu, stats_screen, subscribe_screen, make_playlist_screen,
              playlist_screen, playlist_song_screen, add_to_playlist_screen, edit_song_screen, edit_album_screen,
              edit_artist_screen, become_artist_screen, add_album_screen, add_song_screen, album_selection_screen,
              remove_subscription_screen):
    frame.grid(row=0, column=0, sticky='nsew')

"""
LOGIN
"""
title_login = Label(login, text="Music.AI", fg="white", bg=BG_COLOR, font=("bold", 30))
title_login.place(x=170, y=1)

uname_login = Label(login, text="Usuario: ", fg="white", bg=BG_COLOR, font=("bold", 15))
uname_login.place(x=100, y=100)

password_login = Label(login, text="Password: ", fg="white", bg=BG_COLOR, font=("bold", 15))
password_login.place(x=100, y=150)

login_error_code = Label(login, text="", fg="red", bg=BG_COLOR, font=("bold", 15))
login_error_code.place(x=300, y=250, anchor="center")

t_uname_login = tk.Entry(login, font=('bold', 15), width=22)
t_uname_login.place(x=210, y=100)

t_password_login = tk.Entry(login, font=('bold', 15), width=22)
t_password_login.place(x=210, y=150)

login_button = tk.Button(login, bg=BUTTON_COLOR, text="Iniciar Sesión", command=lambda: validate_login())
login_button.place(x=150, y=200)

go_register_button = tk.Button(login, bg=BUTTON_COLOR, text="Registrarse", command=lambda: show_frame(register))
go_register_button.place(x=280, y=200)




"""
Register
"""
title = Label(register, text="Music.AI Register ", fg="white", bg=BG_COLOR, font=("bold", 30))
title.place(x=200, y=1)

uname_register = Label(register, text="Usuario: ", fg="white", bg=BG_COLOR, font=("bold", 15))
uname_register.place(x=100, y=100)

password_register = Label(register, text="Contraseña: ", fg="white", bg=BG_COLOR, font=("bold", 15))
password_register.place(x=100, y=150)

name_register = Label(register, text="Nombre: ", fg="white", bg=BG_COLOR, font=("bold", 15))
name_register.place(x=100, y=200)

name_register = Label(register, text="Correo: ", fg="white", bg=BG_COLOR, font=("bold", 15))
name_register.place(x=100, y=250)

t_uname_register = tk.Entry(register, font=('bold', 15), width=22)
t_uname_register.place(x=250, y=100)

t_password_register = tk.Entry(register, font=('bold', 15), width=22)
t_password_register.place(x=250, y=150)

t_name_register = tk.Entry(register, font=('bold', 15), width=22)
t_name_register.place(x=250, y=200)

t_email_register = tk.Entry(register, font=('bold', 15), width=22)
t_email_register.place(x=250, y=250)

t_error_register = Label(register, text="", fg="red", bg=BG_COLOR, font=("bold", 15))
t_error_register.place(x=300, y=300, anchor="center")

register_button = Button(register, bg=BUTTON_COLOR, text="Enter", command=lambda: register_on_database())
register_button.place(x=280, y=350)

back_button = Button(register, bg=BUTTON_COLOR, text="Regresar", command=lambda: show_frame(login))
back_button.place(x=200, y=350)

"""
Remove subscription
"""
r_title_login = Label(remove_subscription_screen, text="Music.AI", fg="white", bg=BG_COLOR, font=("bold", 30))
r_title_login.place(x=170, y=1)

r_uname_login = Label(remove_subscription_screen, text="Usuario: ", fg="white", bg=BG_COLOR, font=("bold", 15))
r_uname_login.place(x=100, y=100)

r_password_login = Label(remove_subscription_screen, text="Password: ", fg="white", bg=BG_COLOR, font=("bold", 15))
r_password_login.place(x=100, y=150)

r_login_error_code = Label(remove_subscription_screen, text="", fg="red", bg=BG_COLOR, font=("bold", 15))
r_login_error_code.place(x=300, y=250, anchor="center")

r_t_uname_login = tk.Entry(remove_subscription_screen, font=('bold', 15), width=22)
r_t_uname_login.place(x=210, y=100)

r_password_login = tk.Entry(remove_subscription_screen, font=('bold', 15), width=22)
r_password_login.place(x=210, y=150)

r_login_button = tk.Button(remove_subscription_screen, bg="red", text="Terminar suscripción", command=lambda: cancel_sub())
r_login_button.place(x=150, y=200)

r_error_code = Label(remove_subscription_screen, text="", fg="red", bg=BG_COLOR, font=("bold", 10))
r_error_code.place(x=170, y=300)

back_button = Button(remove_subscription_screen, bg=BUTTON_COLOR, text="Regresar", command=lambda: show_frame(search_menu))
back_button.place(x=50, y=20, anchor="center")


"""
Main screen
"""

selected_search = StringVar(search_menu)
selected_search.set("cancion")

search_type = OptionMenu(search_menu, selected_search, "cancion", "album", "artista", "genero")
search_type.place(x=130, y=50, anchor="center")

search_field = tk.Entry(search_menu, font=('bold', 15), width=22)
search_field.place(x=300, y=50, anchor="center")

log_off_button = Button(search_menu, bg=BUTTON_COLOR, text="Cerrar sesión", command=lambda: log_off())
log_off_button.place(x=550, y=20, anchor="center")

search_button = Button(search_menu, bg=BUTTON_COLOR, text="Buscar", command=lambda: search_for_songs())
search_button.place(x=450, y=50, anchor="center")

edit_mode = tk.IntVar()
edit_mode_check = Checkbutton(search_menu, bg=BUTTON_COLOR, text="Modo edición", variable=edit_mode)
edit_mode_check.place(x=300, y=80, anchor="center")

stats_button = Button(search_menu, bg=BUTTON_COLOR, text="Estadísticas", command=lambda: show_stats())
stats_button.place(x=300, y=150, anchor="center")

add_album_button = Button(search_menu, bg=BUTTON_COLOR, text="Nuevo álbum", command=lambda: show_frame(add_album_screen))
add_album_button.place(x=300, y=200, anchor="center")

become_artist_button = Button(search_menu, bg=BUTTON_COLOR, text="Volverme artista", command=lambda: show_frame(become_artist_screen))
become_artist_button.place(x=300, y=225, anchor="center")

add_song_button = Button(search_menu, bg=BUTTON_COLOR, text="Nueva canción", command=lambda: show_frame(add_song_screen))
add_song_button.place(x=300, y=250, anchor="center")

subscribe_button = Button(search_menu, bg=BUTTON_COLOR, text="Suscribirse", command=lambda: show_frame(subscribe_screen))
subscribe_button.place(x=300, y=300, anchor="center")

create_playlist_button = Button(search_menu, bg=BUTTON_COLOR, text="Crear lista", command=lambda: show_frame(make_playlist_screen))
create_playlist_button.place(x=300, y=300, anchor="center")

cancel_subscription_button = Button(search_menu, bg=BUTTON_COLOR, text="Cancelar subscripción", command=lambda: show_frame(remove_subscription_screen))
cancel_subscription_button.place(x=450, y=350, anchor="center")

view_playlists_button = Button(search_menu, bg=BUTTON_COLOR, text="Mis listas", command=lambda: show_playlists())
view_playlists_button.place(x=300, y=350, anchor="center")

search_field.bind('<Return>', enter_search)

"""
Edit artist screen
"""
artist_edit_title = Label(edit_artist_screen, text="Editar artista", fg="white", bg=BG_COLOR, font=("bold", 15))
artist_edit_title.place(x=300, y=50, anchor="center")

back_button = Button(edit_artist_screen, bg=BUTTON_COLOR, text="Regresar", command=lambda: show_frame(song_list))
back_button.place(x=50, y=20, anchor="center")

name_title = Label(edit_artist_screen, text="Nuevo nombre artístico", fg="white", bg=BG_COLOR, font=("bold", 15))
name_title.place(x=126, y=80)

artist_name_edit = tk.Entry(edit_artist_screen, font=('bold', 15), width=30)
artist_name_edit.place(x=300, y=130, anchor="center")

name_title = Label(edit_artist_screen, text="Nuevo correo electrónico", fg="white", bg=BG_COLOR, font=("bold", 15))
name_title.place(x=126, y=170)

artist_email_edit = tk.Entry(edit_artist_screen, font=('bold', 15), width=30)
artist_email_edit.place(x=300, y=220, anchor="center")

name_title = Label(edit_artist_screen, text="Nuevo tipo de usuario", fg="white", bg=BG_COLOR, font=("bold", 15))
name_title.place(x=126, y=250)

artist_edit_type = StringVar(search_menu)
artist_edit_type.set("artist/manager")

search_type = OptionMenu(edit_artist_screen, artist_edit_type, "artist/manager", "free")
search_type.place(x=300, y=300, anchor="center")

confirm_song_edit_button = Button(edit_artist_screen, bg=BUTTON_COLOR, text="Confirmar", command=lambda: update_artist())
confirm_song_edit_button.place(x=300, y=400, anchor="center")

confirm_song_edit_button = Button(edit_artist_screen, bg=BUTTON_COLOR, text="Borrar artista", command=lambda: delete_artist())
confirm_song_edit_button.place(x=540, y=20, anchor="center")

"""
Add album screen
"""
title = Label(add_album_screen, text="Añadir álbum", fg="white", bg=BG_COLOR, font=("bold", 30))
title.place(x=300, y=20, anchor="center")

name_title = Label(add_album_screen, text="Nombre del álbum", fg="white", bg=BG_COLOR, font=("bold", 15))
name_title.place(x=126, y=80)

new_album_name = tk.Entry(add_album_screen, font=('bold', 15), width=30)
new_album_name.place(x=300, y=130, anchor="center")

confirm_album_edit_button = Button(add_album_screen, bg=BUTTON_COLOR, text="Confirmar", command=lambda: add_album())
confirm_album_edit_button.place(x=300, y=300, anchor="center")

back_button = Button(add_album_screen, bg=BUTTON_COLOR, text="Regresar", command=lambda: show_frame(search_menu))
back_button.place(x=50, y=20, anchor="center")

"""
Add song screen
"""

title = Label(add_song_screen, text="Añadir canción", fg="white", bg=BG_COLOR, font=("bold", 30))
title.place(x=300, y=20, anchor="center")

name_title = Label(add_song_screen, text="Nombre de la canción", fg="white", bg=BG_COLOR, font=("bold", 15))
name_title.place(x=126, y=80)

new_song_name = tk.Entry(add_song_screen, font=('bold', 15), width=30)
new_song_name.place(x=300, y=130, anchor="center")

name_title = Label(add_song_screen, text="Género de la canción", fg="white", bg=BG_COLOR, font=("bold", 15))
name_title.place(x=126, y=170)

selected_song_genre = StringVar(add_song_screen)
selected_song_genre.set(SONG_GENRES[0])
search_type = ttk.Combobox(add_song_screen, textvariable=selected_song_genre, values=[*SONG_GENRES], state="readonly")
search_type.place(x=300, y=220, anchor="center")

confirm_album_edit_button = Button(add_song_screen, bg=BUTTON_COLOR, text="Confirmar", command=lambda: add_song())
confirm_album_edit_button.place(x=300, y=300, anchor="center")

back_button = Button(add_song_screen, bg=BUTTON_COLOR, text="Regresar", command=lambda: show_frame(search_menu))
back_button.place(x=50, y=20, anchor="center")


"""
Album selection screen
"""
# Frame
album_selection = Frame(album_selection_screen)
album_selection.pack(fill=BOTH, expand=1)

# Canvas
album_canvas = Canvas(album_selection)
album_canvas.pack(side=LEFT, fill=BOTH, expand=1)

# Scrollbar
my_scrollbar = ttk.Scrollbar(album_selection, orient=VERTICAL, command=album_canvas.yview)
my_scrollbar.pack(side=RIGHT, fill=Y)

back_button = Button(album_selection, bg=BUTTON_COLOR, text="Regresar", command=lambda: show_frame(add_song_screen))
back_button.place(x=0, y=0)

back_button = Button(album_selection, bg=BUTTON_COLOR, text="Añadir\nsin \nálbum", command=lambda: add_song_without_album())
back_button.place(x=10, y=50)

scroll_error_message = Label(album_selection, text="", fg="red", bg="#000000", font=("bold", 15))
scroll_error_message.place(x=0, y=50)

# Canvas Config
album_canvas.configure(yscrollcommand=my_scrollbar.set)
album_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion=my_canvas.bbox("all")))

# 2nd Frame (inside Canvas)
album_selection_frame = Frame(album_canvas)

# Second Frame to Window
album_canvas.create_window((100, 100), window=album_selection_frame, anchor="nw")


"""
Edit song screen
"""
title = Label(edit_song_screen, text="Editar canción", fg="white", bg="#000000", font=("bold", 30))
title.place(x=300, y=20, anchor="center")

back_button = Button(edit_song_screen, bg=BUTTON_COLOR, text="Regresar", command=lambda: show_frame(song_list))
back_button.place(x=50, y=20, anchor="center")

name_title = Label(edit_song_screen, text="Nuevo nombre de la canción", fg="white", bg="#000000", font=("bold", 15))
name_title.place(x=126, y=80)

song_name_edit = tk.Entry(edit_song_screen, font=('bold', 15), width=30)
song_name_edit.place(x=300, y=130, anchor="center")

name_title = Label(edit_song_screen, text="Nuevo género de la canción", fg="white", bg="#000000", font=("bold", 15))
name_title.place(x=126, y=170)

song_genre_edit = tk.Entry(edit_song_screen, font=('bold', 15), width=30)
song_genre_edit.place(x=300, y=220, anchor="center")

confirm_song_edit_button = Button(edit_song_screen, bg=BUTTON_COLOR, text="Confirmar", command=lambda: update_song())
confirm_song_edit_button.place(x=300, y=300, anchor="center")

confirm_song_edit_button = Button(edit_song_screen, bg=BUTTON_COLOR, text="Borrar canción", command=lambda: delete_song())
confirm_song_edit_button.place(x=540, y=20, anchor="center")

confirm_song_edit_button = Button(edit_song_screen, bg=BUTTON_COLOR, text="Desactivar canción", command=lambda: deactivate_song())
confirm_song_edit_button.place(x=540, y=70, anchor="center")

"""
Edit album screen
"""
title = Label(edit_album_screen, text="Editar álbum", fg="white", bg="#000000", font=("bold", 30))
title.place(x=300, y=20, anchor="center")

back_button = Button(edit_album_screen, bg=BUTTON_COLOR, text="Regresar", command=lambda: show_frame(song_list))
back_button.place(x=50, y=20, anchor="center")

name_title = Label(edit_album_screen, text="Nuevo nombre del álbum", fg="white", bg="#000000", font=("bold", 15))
name_title.place(x=126, y=80)

album_name_edit = tk.Entry(edit_album_screen, font=('bold', 15), width=30)
album_name_edit.place(x=300, y=130, anchor="center")

confirm_album_edit_button = Button(edit_album_screen, bg=BUTTON_COLOR, text="Confirmar", command=lambda: update_album())
confirm_album_edit_button.place(x=300, y=300, anchor="center")

confirm_album_edit_button = Button(edit_album_screen, bg=BUTTON_COLOR, text="Borrar álbum", command=lambda: delete_album())
confirm_album_edit_button.place(x=500, y=50, anchor="center")

"""
Become artist screen
"""
title = Label(become_artist_screen, text="Ser artista / manager", fg="white", bg="#000000", font=("bold", 30))
title.place(x=300, y=20, anchor="center")

name_title = Label(become_artist_screen, text="Nombre artístico", fg="white", bg="#000000", font=("bold", 15))
name_title.place(x=126, y=80)

artistic_name_edit = tk.Entry(become_artist_screen, font=('bold', 15), width=30)
artistic_name_edit.place(x=300, y=130, anchor="center")

confirm_album_edit_button = Button(become_artist_screen, bg=BUTTON_COLOR, text="Confirmar", command=lambda: become_artist())
confirm_album_edit_button.place(x=300, y=300, anchor="center")

back_button = Button(become_artist_screen, bg=BUTTON_COLOR, text="Regresar", command=lambda: show_frame(search_menu))
back_button.place(x=50, y=20, anchor="center")


"""
Subscribe screen
"""
subscribe_title = Label(subscribe_screen, text="Suscribirse a Music.AI", fg="white", bg="#000000", font=("bold", 25))
subscribe_title.place(x=300, y=20, anchor="center")

back_button = Button(subscribe_screen, bg=BUTTON_COLOR, text="Regresar", command=lambda: show_frame(search_menu))
back_button.place(x=50, y=20, anchor="center")

name_title = Label(subscribe_screen, text="Nombre en la tarjeta", fg="white", bg="#000000", font=("bold", 15))
name_title.place(x=126, y=80)

subscribe_name_field = tk.Entry(subscribe_screen, font=('bold', 15), width=30)
subscribe_name_field.place(x=300, y=130, anchor="center")

name_title = Label(subscribe_screen, text="Número de tarjeta", fg="white", bg="#000000", font=("bold", 15))
name_title.place(x=126, y=170)

subscribe_credit_field = tk.Entry(subscribe_screen, font=('bold', 15), width=30)
subscribe_credit_field.place(x=300, y=220, anchor="center")

name_title = Label(subscribe_screen, text="CVV", fg="white", bg="#000000", font=("bold", 15))
name_title.place(x=126, y=260)

subscribe_cvv_field = tk.Entry(subscribe_screen, font=('bold', 15), width=30)
subscribe_cvv_field.place(x=300, y=310, anchor="center")

validate_subscription_button = Button(subscribe_screen, bg=BUTTON_COLOR, text="Suscribirse", command=lambda: subscribe())
validate_subscription_button.place(x=300, y=360, anchor="center")

subscription_error_message = Label(subscribe_screen, text="", fg="red", bg="#000000", font=("bold", 15))
subscription_error_message.place(x=126, y=380)

"""
Make playlist screen
"""
new_playlist_title = Label(make_playlist_screen, text="Introduzca el nombre para la nueva lista",
                           fg="white", bg="#000000", font=('bold', 20), width=50)

new_playlist_title.place(x=300, y=100, anchor="center")

playlist_name_field = tk.Entry(make_playlist_screen, font=('bold', 15), width=30)
playlist_name_field.place(x=300, y=200, anchor="center")

new_playlist_button = Button(make_playlist_screen, bg=BUTTON_COLOR, text="Confirmar", command=lambda: create_playlist())
new_playlist_button.place(x=300, y=300, anchor="center")

new_playlist_return = Button(make_playlist_screen, bg=BUTTON_COLOR, text="Regresar", command=lambda: show_frame(search_menu))
new_playlist_return.place(x=300, y=350, anchor="center")

new_playlist_error_message = Label(make_playlist_screen, text="", fg="red", bg="#000000", font=("bold", 15))
new_playlist_error_message.place(x=300, y=380, anchor="center")

"""
Stats screen
"""
# Frame
stats_main_frame = Frame(stats_screen)
stats_main_frame.pack(fill=BOTH, expand=1)

# Canvas
stats_canvas = Canvas(stats_main_frame)
stats_canvas.pack(side=LEFT, fill=BOTH, expand=1)

# Scrollbar
stats_scrollbar = ttk.Scrollbar(stats_main_frame, orient=VERTICAL, command=stats_canvas.yview)
stats_scrollbar.pack(side=RIGHT, fill=Y)

back_button = Button(stats_main_frame, bg=BUTTON_COLOR, text="Regresar", command=lambda: show_frame(search_menu))
back_button.place(x=0, y=0)

scroll_error_message = Label(stats_main_frame, text="", fg="red", bg="#000000", font=("bold", 15))
scroll_error_message.place(x=0, y=50)

# Canvas Config
stats_canvas.configure(yscrollcommand=stats_scrollbar.set)
stats_canvas.bind('<Configure>', lambda e: stats_canvas.configure(scrollregion=stats_canvas.bbox("all")))

# 2nd Frame (inside Canvas)
stats_second_frame = Frame(stats_canvas)

# Second Frame to Window
stats_canvas.create_window((100, 100), window=stats_second_frame, anchor="nw")

recent_albums_button = Button(stats_main_frame, bg=BUTTON_COLOR, text="Álbumes más recientes", command=lambda: show_most_recent_albums())
recent_albums_button.place(x=20, y=100)

popular_artists_button = Button(stats_main_frame, bg=BUTTON_COLOR, text="Artistas populares", command=lambda: show_growing_artists())
popular_artists_button.place(x=20, y=150)

new_subscriptions_button = Button(stats_main_frame, bg=BUTTON_COLOR, text="Nuevas suscripciones",
                                  command=lambda: show_subscription_amount())
new_subscriptions_button.place(x=20, y=200)

artist_with_most_music_button = Button(stats_main_frame, bg=BUTTON_COLOR, text="Artistas con más música",
                                       command=lambda: show_artists_with_most_music())
artist_with_most_music_button.place(x=20, y=250)

popular_genre_button = Button(stats_main_frame, bg=BUTTON_COLOR, text="Géneros populares", command=lambda: show_popular_genres())
popular_genre_button.place(x=20, y=300)

active_users_button = Button(stats_main_frame, bg=BUTTON_COLOR, text="Usuarios más activos", command=lambda: show_most_active_users())
active_users_button.place(x=20, y=350)

"""
Add to playlist selection
"""
# Frame
album_selection = Frame(add_to_playlist_screen)
album_selection.pack(fill=BOTH, expand=1)

# Canvas
album_canvas = Canvas(album_selection)
album_canvas.pack(side=LEFT, fill=BOTH, expand=1)

# Scrollbar
my_scrollbar = ttk.Scrollbar(album_selection, orient=VERTICAL, command=album_canvas.yview)
my_scrollbar.pack(side=RIGHT, fill=Y)

back_button = Button(album_selection, bg=BUTTON_COLOR, text="Regresar", command=lambda: show_frame(song_list))
back_button.place(x=0, y=0)

scroll_error_message = Label(album_selection, text="", fg="red", bg="#000000", font=("bold", 15))
scroll_error_message.place(x=0, y=50)

# Canvas Config
album_canvas.configure(yscrollcommand=my_scrollbar.set)
album_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion=my_canvas.bbox("all")))

# 2nd Frame (inside Canvas)
playlist_selection_frame = Frame(album_canvas)

# Second Frame to Window
album_canvas.create_window((100, 100), window=playlist_selection_frame, anchor="nw")

"""
Playlist songs
"""
# Frame
playlist_songs = Frame(playlist_song_screen)
playlist_songs.pack(fill=BOTH, expand=1)

# Canvas
album_canvas = Canvas(playlist_songs)
album_canvas.pack(side=LEFT, fill=BOTH, expand=1)

# Scrollbar
my_scrollbar = ttk.Scrollbar(playlist_songs, orient=VERTICAL, command=album_canvas.yview)
my_scrollbar.pack(side=RIGHT, fill=Y)

back_button = Button(playlist_songs, bg=BUTTON_COLOR, text="Regresar", command=lambda: show_frame(playlist_screen))
back_button.place(x=0, y=0)

scroll_error_message = Label(playlist_songs, text="", fg="red", bg="#000000", font=("bold", 15))
scroll_error_message.place(x=0, y=50)

# Canvas Config
album_canvas.configure(yscrollcommand=my_scrollbar.set)
album_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion=my_canvas.bbox("all")))

# 2nd Frame (inside Canvas)
song_playlist_frame = Frame(album_canvas)

# Second Frame to Window
album_canvas.create_window((100, 100), window=song_playlist_frame, anchor="nw")

"""
Playlists
"""
# Frame
playlist_frame = Frame(playlist_screen)
playlist_frame.pack(fill=BOTH, expand=1)

# Canvas
album_canvas = Canvas(playlist_frame)
album_canvas.pack(side=LEFT, fill=BOTH, expand=1)

# Scrollbar
my_scrollbar = ttk.Scrollbar(playlist_frame, orient=VERTICAL, command=album_canvas.yview)
my_scrollbar.pack(side=RIGHT, fill=Y)

back_button = Button(playlist_frame, bg=BUTTON_COLOR, text="Regresar", command=lambda: show_frame(search_menu))
back_button.place(x=0, y=0)

scroll_error_message = Label(playlist_frame, text="", fg="red", bg="#000000", font=("bold", 15))
scroll_error_message.place(x=0, y=50)

# Canvas Config
album_canvas.configure(yscrollcommand=my_scrollbar.set)
album_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion=my_canvas.bbox("all")))

# 2nd Frame (inside Canvas)
second_playlist_frame = Frame(album_canvas)

# Second Frame to Window
album_canvas.create_window((100, 100), window=second_playlist_frame, anchor="nw")

"""
Lists of songs
"""
# Frame
main_frame = Frame(song_list)
main_frame.pack(fill=BOTH, expand=1)

# Canvas
my_canvas = Canvas(main_frame)
my_canvas.pack(side=LEFT, fill=BOTH, expand=1)

# Scrollbar
my_scrollbar = ttk.Scrollbar(main_frame, orient=VERTICAL, command=my_canvas.yview)
my_scrollbar.pack(side=RIGHT, fill=Y)

back_button = Button(main_frame, bg=BUTTON_COLOR, text="Regresar", command=lambda: show_frame(search_menu))
back_button.place(x=0, y=0)

add_to_playlist_button_nice = Button(main_frame, bg=BUTTON_COLOR, text="Añadir canción a lista", command=lambda: insert_song_into_playlist())
add_to_playlist_button_nice.place(x=0, y=100)

scroll_error_message = Label(main_frame, text="", fg="red", bg="#000000", font=("bold", 15))
scroll_error_message.place(x=0, y=50)

# Canvas Config
my_canvas.configure(yscrollcommand=my_scrollbar.set)
my_canvas.bind('<Configure>', lambda e: my_canvas.configure(scrollregion=my_canvas.bbox("all")))

# 2nd Frame (inside Canvas)
second_frame = Frame(my_canvas)

# Second Frame to Window
my_canvas.create_window((100, 100), window=second_frame, anchor="nw")

show_frame(login)
window.mainloop()
