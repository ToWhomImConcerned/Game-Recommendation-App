import tkinter as tk          # tkinter is Python's built-in GUI library — lets you build windows, buttons, labels, etc.
import requests               # lets you make HTTP requests (like calling an API)
from dotenv import load_dotenv  # loads variables from a .env file so you can keep secrets out of your code
import os                     # lets you access environment variables and interact with the operating system
import random                 # gives you tools for randomness (used to randomly pick a greeting here)
from tkinter import ttk       # an extended/themed widget set that comes with tkinter (imported but not used here yet)
import json
from tkinter import messagebox
import webbrowser
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, "played_games.json")

load_dotenv()                         # reads your .env file and loads its contents into the environment
api_key = os.getenv("RAWG_KEY")       # grabs your secret API key from the environment (not hardcoded, which is safer)

played_games = set()

favorites = set()
FAVORITES_PATH = os.path.join(BASE_DIR, "favorites.json")

# A dictionary that maps readable genre names to the API's expected slug values
# When the user picks "Role-Playing(RPG)", the API actually needs "role-playing-games" — this handles that translation
genre_map = {
    "Action": "action",
    "Adventure": "adventure",
    "Horror": "horror",
    "Puzzle": "puzzle",
    "Role-Playing(RPG)": "role-playing-games",
    "Shooter/FPS": "shooter",
    "Simulation": "simulation",
    "Sports": "sports",
    "Strategy": "strategy"
}

# Same idea — maps friendly platform names to the numeric IDs the RAWG API uses to filter by platform
platform_map = {
    "PC": "4",
    "Playstation 4": "18",
    "Playstation 5": "187",
    "Xbox One": "1",
    "Xbox Series S": "186",
    "Xbox Series X": "186",
    "Nintendo Switch": "7"
}

perspective_map = {
    "First Person": "first-person",
    "Isometric": "isometric",
    "Side Scrolling/2D": "2d",
    "Third Person": "third-person",
    "Top-Down": "top-down",
    "Virtual Reality": "vr"
}

difficulty_map = {
    "Casual": "casual",
    "Easy": "relaxing",
    "Moderate": "",
    "Hard": "difficult",
    "Brutal": "hardcore"
}

def strip_html(text):
    clean = re.sub(r'<[^>]+>', '', text)
    return clean

def show_details(game_id):
    url = f"https://api.rawg.io/api/games/{game_id}?key={api_key}"
    response = requests.get(url)
    data = response.json()

    win = tk.Toplevel(window)
    win.title(data.get('name', 'Game Details'))
    win.geometry("500x400")
    win.configure(bg="darkorange")

    tk.Label(win, text=data.get('name', 'Unknown'), font=("Helvetica", 16, "bold"),
             bg="darkorange").pack(pady=10)
    
    details_frame = tk.Frame(win, bg="darkorange")
    details_frame.pack(padx=20, pady=5, fill="x")

    def add_row(label, value):
        tk.Label(details_frame, text=f"{label}:", font=("Helvetica", 10, "bold"),
                 bg="darkorange", anchor="w").grid(row=add_row.counter, column=0, sticky="w", pady=3)
        tk.Label(details_frame, text=value, font=("Helvetica", 10),
                 bg="darkorange", anchor="w", wraplength=350).grid(row=add_row.counter, column=1, sticky="w", padx=10)
        add_row.counter +=1

    add_row.counter = 0

    release_date = data.get('released', 'Unknown')
    year = release_date[:4] if release_date != 'Unknown' else 'Unknown'

    rating = data.get('rating', 0)
    rating_display = f"{rating} / 5.0" if rating else "Not yet rated"

    genres = ", ".join([g['name'] for g in data.get('genres', [])])
    developers = ", ".join([d['name'] for d in data.get('developers', [])])

    description = strip_html(data.get('description', ''))
    snippet = description[:350].rsplit(' ', 1)[0] + "..." if len(description) > 350 else description

    add_row("Released", year)
    add_row("Rating", rating_display)
    add_row("Genres", genres or "Unknown")
    add_row("Developers", developers or "Unknown")
    add_row("Description", snippet)

    website = data.get('website', '')
    if website:
        link = tk.Label(win, text="Official Website", fg="blue", bg="darkorange",
                        cursor="hand2", font=("Helvetica", 10, "underline"))
        link.pack(pady=10)
        link.bind("<Button-1>", lambda e: webbrowser.open(website))

def save_played():
    with open(FILE_PATH, "w") as f:
        json.dump(list(played_games), f)

def load_played():
    global played_games
    try:
        with open(FILE_PATH, "r") as f:
            played_games = set(json.load(f))
    except FileNotFoundError:
        played_games = set()

load_played()

def clear_played_games():
    global played_games

    confirm = messagebox.askyesno("Confirm reset", "Are you sure you want to clear all played games?")
    if not confirm:
        return

    played_games.clear()

    # delete the file if it exists
    if os.path.exists(FILE_PATH):
        os.remove(FILE_PATH)

    messagebox.showinfo("Reset", "Played games cleared!")

def save_favorites():
    with open(FAVORITES_PATH, "w") as f:
        json.dump(list(favorites), f)

def load_favorites():
    global favorites
    try:
        with open(FAVORITES_PATH, "r") as f:
            favorites = set(json.load(f))
    except FileNotFoundError:
        favorites = set()

load_favorites()

def show_favorites():
    win = tk.Toplevel(window)
    win.title("My Favorites")
    win.geometry("400x300")
    win.configure(bg="darkorange")

    tk.Label(win, text="My favorite games", font=("helvetica", 16, "bold"),
             bg="darkorange").pack(pady=10)
    
    content_frame = tk.Frame(win, bg="darkorange")
    content_frame.pack()

    def refresh():
        for widget in content_frame.winfo_children():
            widget.destroy()

        if not favorites:
            tk.Label(content_frame, text="No favorites yet!", bg="darkorange", font=("Helvetica", 12)).pack(pady=3)
        else:
            for name in favorites:
                tk.Label(content_frame, text=name, bg="darkorange", font=("Helvetica", 12)).pack(pady=3)

    def clear_favorites():
        global favorites

        confirm = messagebox.askyesno("confirm reset", "Are you sure you want to clear all favorites?", parent=win)
        if not confirm:
            return
        
        favorites.clear()

        if os.path.exists(FAVORITES_PATH):
            os.remove(FAVORITES_PATH)

        refresh()

        messagebox.showinfo("Reset", "Favorites cleared!", parent=win)
    
    tk.Button(win, text="Clear Favorites", command=clear_favorites, fg="white", bg="red").pack(pady=5)

    refresh()

def get_recommendation():   # this function runs when the user clicks "Search"
    global results_frame

    for widget in results_frame.winfo_children():
        widget.destroy()

    if genre_var.get() == "Select Genre" or platform_var.get() == "Select Platform":

        messagebox.showwarning("Missing info", "Please select at least a genre and platform.")
        return

    genre = genre_map.get(genre_var.get())          # .get() on the StringVar reads the current dropdown value, then looks it up in the dict
    selected_perspective = perspective_var.get()
    perspective = perspective_map.get(selected_perspective, "") if selected_perspective != "Select View Style" else ""             # reads the selected perspective (e.g. "First Person")
    difficulty = difficulty_var.get()               # reads the selected difficulty
    difficulty_tag = difficulty_map.get(difficulty, "")
    platform = platform_map.get(platform_var.get()) # same pattern — reads the platform dropdown and translates it to an API ID
    keyword = keyword_entry.get()                   # reads whatever the user typed in the text box

    tags = []
    if perspective:
        tags.append(perspective)

    if difficulty_tag:
        tags.append(difficulty_tag)

    tags_param = f"&tags={','.join(tags)}" if tags else ""
    url = f"https://api.rawg.io/api/games?key={api_key}&genres={genre}&platforms={platform}{tags_param}&search={keyword}&page_size=10"
    
    response = requests.get(url)   # sends the GET request to the RAWG API
    data = response.json()     # parses the JSON response into a Python dictionary

    if not data["results"]:                                       # if the results list is empty, no games matched
        msg = tk.Label(results_frame, text="No games found! Try different selections.", bg="darkorange", fg="black")  # updates the label text with an error message
        msg.pack()
        window.after(3000, msg.destroy)
        return                                                      # exits the function early so nothing else runs

    games = data["results"]                          # the list of game objects returned by the API

    filtered_games = [game for game in games if game['name'] not in played_games]

    if not filtered_games:
        msg = tk.Label(results_frame, text="You've played all these! Try different filters.", bg="darkorange", fg="black")
        msg.pack()
        window.after(3000, msg.destroy)
        return

    for game in filtered_games[:3]:   # loops over up to the first 3 results; enumerate gives you both the index (i) and the item

        game_frame = tk.Frame(results_frame, bg="darkorange")
        game_frame.pack(fill="x", pady=5)

        game_label = tk.Label(game_frame,
                              text=game['name'],
                              bg="darkorange",
                              fg="black",
                              font=("Helvetica", 12))
        game_label.grid(row=0, column=0, padx=10)

        btn = tk.Button(game_frame,
                        text="Mark as Played",
                        command=lambda name=game['name']: mark_as_played(name))
        btn.grid(row=0, column=1, padx=10)

        fav_text = "♥" if game['name'] in favorites else "♡"
        fav_btn = tk.Button(game_frame, text=fav_text, font=("Helvetica", 14),
                            bg="darkorange", relief="flat")
        fav_btn.config(command=lambda name=game['name'], b=fav_btn: toggle_favorite(name, b))
        fav_btn.grid(row=0, column=2, padx=5)

        details_btn = tk.Button(game_frame, text="More Details",
                                command=lambda gid=game['id']: show_details(gid))
        details_btn.grid(row=1, column=0, columnspan=3, pady=5)

def mark_as_played(game_name):
    played_games.add(game_name)
    save_played()
    get_recommendation() # refresh UI

def toggle_favorite(game_name, btn):
    if game_name in favorites:
        favorites.discard(game_name)
        btn.config(text="♡")
    else:
        favorites.add(game_name)
        btn.config(text="♥")
    save_favorites()

# --- UI SETUP BELOW ---
# Everything from here down builds the window and its widgets. None of it runs until window.mainloop() at the end.

window = tk.Tk()                  # creates the main application window
window.title("Game Recommender")  # sets the text in the title bar
window.geometry("800x600")        # sets the window size in pixels (width x height)
window.configure(bg="darkorange") # sets the background color of the window

# a label that displays a random greeting at the top — random.choice picks one string from the list
title_label = tk.Label(window, text=random.choice(["What's up! Let's find you a game!", "Welcome, looking for a new game?", "What a day for a new game!"]), font=("Helvetica", 20, "bold"), fg="black", bg="darkorange")
title_label.pack()   # .pack() places the widget into the window (top to bottom by default)

dropdowns_frame = tk.Frame(window, bg="darkorange")
dropdowns_frame.pack(pady=10)

# StringVar is a special tkinter variable that a widget can "watch" — when it changes, the widget updates automatically
genre_var = tk.StringVar()
genre_var.set("Select Genre")   # sets the default displayed value
genre_dropdown = tk.OptionMenu(dropdowns_frame, genre_var, "Action", "Adventure", "Horror", "Puzzle", "Role-Playing(RPG)", "Shooter/FPS", "Simulation", "Sports", "Strategy")
genre_dropdown.grid(row=0, column=0, padx=10, pady=10)

perspective_var = tk.StringVar()
perspective_var.set("Select View Style")
perspective_dropdown = tk.OptionMenu(dropdowns_frame, perspective_var, "First Person", "Isometric", "Side Scrolling/2D", "Third Person", "Top-Down", "Virtual Reality")
perspective_dropdown.grid(row=0, column=1, padx=10, pady=10)

difficulty_var = tk.StringVar()
difficulty_var.set("Select Difficulty")
difficulty_dropdown = tk.OptionMenu(dropdowns_frame, difficulty_var, "Casual", "Easy", "Moderate", "Hard", "Brutal")
difficulty_dropdown.grid(row=0, column=2, padx=10, pady=10)

platform_var = tk.StringVar()
platform_var.set("Select Platform")
platform_dropdown = tk.OptionMenu(dropdowns_frame, platform_var, "PC", "Playstation 4", "Playstation 5", "Xbox One", "Xbox Series S", "Xbox Series X", "Nintendo Switch")
platform_dropdown.grid(row=0, column=3, padx=10, pady=10)

# a text input box where the user can type a custom keyword (e.g. "open world" or "stealth")
keyword_entry = tk.Entry(window, width=40, fg="white", bg="black", insertbackground="white")  # insertbackground sets the cursor color
keyword_entry.pack(pady=10)

# the button that triggers get_recommendation() when clicked — command= is how you wire a function to a button
search_button = tk.Button(window, text="Search", command=get_recommendation, fg="white", bg="black")
search_button.pack(pady=10)

clear_button = tk.Button(window, text="Reset played games",command=clear_played_games, fg="white", bg="red")
clear_button.pack(pady=5)

favorites_button = tk.Button(window, text="♥ My Favorites ♥", command=show_favorites, fg="white", bg="hotpink")
favorites_button.pack(pady=5)

results_frame = tk.Frame(window, bg="darkorange")
results_frame.pack(pady=20)

window.bind("<Return>", lambda event: get_recommendation()) # binds the return key to the search button

window.mainloop()   # starts the event loop — this keeps the window open and listening for user interactions until it's closed