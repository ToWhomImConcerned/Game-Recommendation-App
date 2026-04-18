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
    "Family": "family,card,board-games,educational",
    "Puzzle": "puzzle",
    "Role-Playing(RPG)": "role-playing-games-rpg",
    "Shooter/FPS": "shooter",
    "Simulation": "simulation",
    "Sports & Racing": "sports,racing,fighting",
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

    release_date = data.get('released') or 'Unknown'
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

    genre_overrides = []
    tag_list = []

    # handle genre
    if genre_var.get() == "Horror":
        genre_overrides.append("action")
        tag_list.append("horror")
    else:
        genre_overrides.append(genre_map.get(genre_var.get(), "action"))

    # handle perspective
    if perspective_var.get() == "Side Scrolling/2D":
        genre_overrides.append("platformer")
    else:
        perspective = perspective_map.get(perspective_var.get(), "")
        if perspective and perspective_var.get() != "Select View Style":
            tag_list.append(perspective)

    # handle difficulty
    if difficulty_var.get() == "Casual":
        tag_list.append("casual")
    else:
        difficulty_tag = difficulty_map.get(difficulty_var.get(), "")
        if difficulty_tag:
            tag_list.append(difficulty_tag)

    genre = ",".join(genre_overrides)
    platform = platform_map.get(platform_var.get())
    keyword = keyword_entry.get()
    tags_param = f"&tags={','.join(tag_list)}" if tag_list else ""
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

        top_row = tk.Frame(game_frame, bg="darkorange")
        top_row.pack()

        bottom_row = tk.Frame(game_frame, bg="darkorange")
        bottom_row.pack()

        game_label = tk.Label(top_row, text=game['name'], bg="darkorange",
                            fg="black", font=("Helvetica", 13, "bold"))
        game_label.pack(side="left", padx=10)

        fav_text = "♥" if game['name'] in favorites else "♡"
        fav_btn = tk.Button(top_row, text=fav_text, font=("Helvetica", 14),
                            bg="darkorange", relief="flat")
        fav_btn.config(command=lambda name=game['name'], b=fav_btn: toggle_favorite(name, b))
        fav_btn.pack(side="left", padx=5)

        btn = tk.Button(bottom_row, text="Mark as Played",
                        command=lambda name=game['name']: mark_as_played(name))
        btn.pack(side="left", padx=10)

        details_btn = tk.Button(bottom_row, text="More Details",
                                command=lambda gid=game['id']: show_details(gid))
        details_btn.pack(side="left", padx=10)

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
genre_dropdown = tk.OptionMenu(dropdowns_frame, genre_var, "Action", "Adventure", "Family", "Horror", "Puzzle", "Role-Playing(RPG)", "Shooter/FPS", "Simulation", "Sports & Racing", "Strategy")
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