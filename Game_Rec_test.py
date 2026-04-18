import tkinter as tk          # tkinter is Python's built-in GUI library — lets you build windows, buttons, labels, etc.
import requests               # lets you make HTTP requests (like calling a web API)
from dotenv import load_dotenv  # loads variables from a .env file so you can keep secrets out of your code
import os                     # lets you access environment variables and interact with the operating system
import random                 # gives you tools for randomness (used here to randomly pick a greeting)
from tkinter import ttk       # extended/themed widget set from tkinter — imported but not actively used yet
import json                   # lets you convert Python objects to/from JSON (used to save/load data files)
from tkinter import messagebox  # provides pop-up dialog boxes for warnings, confirmations, and info messages
import webbrowser             # lets you open URLs in the user's default browser
import re                     # gives you tools for regular expressions (used here to strip HTML tags)

# __file__ is the path to this script — os.path.abspath resolves it to a full absolute path,
# and os.path.dirname strips the filename, leaving just the folder it lives in.
# Storing BASE_DIR means all our data files save next to this script no matter where it's run from.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, "played_games.json")   # where we persist the "played" list between sessions

load_dotenv()                         # reads your .env file and loads its key=value pairs into the environment
api_key = os.getenv("RAWG_KEY")       # grabs the API key from the environment (safer than hardcoding it in the source)

# Sets are like lists but automatically deduplicate — perfect for tracking game names where duplicates are meaningless.
# They're also faster than lists for "is this item in here?" checks, which we do a lot.
played_games = set()

favorites = set()
FAVORITES_PATH = os.path.join(BASE_DIR, "favorites.json")

# Maps the human-readable genre names shown in the dropdown to the "slug" values the RAWG API expects.
# Some entries combine multiple slugs with commas — RAWG accepts that and treats it as an OR filter.
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

# RAWG identifies platforms by numeric ID, not by name — this maps our dropdown labels to those IDs.
platform_map = {
    "PC": "4",
    "Playstation 4": "18",
    "Playstation 5": "187",
    "Xbox One": "1",
    "Xbox Series S": "186",
    "Xbox Series X": "186",
    "Nintendo Switch": "7"
}

# RAWG uses "tags" to filter by things like camera perspective. These are the tag slugs for each option.
perspective_map = {
    "First Person": "first-person",
    "Isometric": "isometric",
    "Side Scrolling/2D": "2d",
    "Third Person": "third-person",
    "Top-Down": "top-down",
    "Virtual Reality": "vr"
}

# Maps difficulty labels to RAWG tag slugs. "Moderate" maps to an empty string,
# which means we simply won't add a difficulty tag for that choice — it acts as a wildcard.
difficulty_map = {
    "Easy": "relaxing",
    "Moderate": "",
    "Hard": "difficult",
    "Brutal": "hardcore"
}

def strip_html(text):
    # RAWG descriptions often contain raw HTML tags like <p>, <br>, <strong>, etc.
    # This regex matches anything between < and > (non-greedy) and replaces it with nothing,
    # leaving just the plain text content.
    clean = re.sub(r'<[^>]+>', '', text)
    return clean

def show_details(game_id):
    # Fetches detailed info for a single game from RAWG using its unique ID,
    # then displays it in a new pop-up window (Toplevel) on top of the main window.
    url = f"https://api.rawg.io/api/games/{game_id}?key={api_key}"
    response = requests.get(url)
    data = response.json()

    # tk.Toplevel creates a secondary window that stays on top of the main one.
    # It's independent — closing it doesn't close the main window.
    win = tk.Toplevel(window)
    win.title(data.get('name', 'Game Details'))
    win.geometry("500x400")
    win.configure(bg="darkorange")

    tk.Label(win, text=data.get('name', 'Unknown'), font=("Helvetica", 16, "bold"),
             bg="darkorange").pack(pady=10)
    
    details_frame = tk.Frame(win, bg="darkorange")
    details_frame.pack(padx=20, pady=5, fill="x")

    # add_row is a helper defined inside show_details so it can close over (share) details_frame and add_row.counter.
    # Each call adds a label-value pair to the next row of the grid.
    def add_row(label, value):
        tk.Label(details_frame, text=f"{label}:", font=("Helvetica", 10, "bold"),
                 bg="darkorange", anchor="w").grid(row=add_row.counter, column=0, sticky="w", pady=3)
        tk.Label(details_frame, text=value, font=("Helvetica", 10),
                 bg="darkorange", anchor="w", wraplength=350).grid(row=add_row.counter, column=1, sticky="w", padx=10)
        add_row.counter += 1

    # Python functions don't have static local variables, but we can attach attributes directly to the function object.
    # add_row.counter acts like a persistent row counter that increments with each call.
    add_row.counter = 0

    release_date = data.get('released') or 'Unknown'
    year = release_date[:4] if release_date != 'Unknown' else 'Unknown'  # slice the 4-digit year from "YYYY-MM-DD"

    rating = data.get('rating', 0)
    rating_display = f"{rating} / 5.0" if rating else "Not yet rated"

    # data.get('genres', []) safely returns an empty list if 'genres' is missing.
    # The list comprehension extracts each genre's name, then ", ".join() combines them into one string.
    genres = ", ".join([g['name'] for g in data.get('genres', [])])
    developers = ", ".join([d['name'] for d in data.get('developers', [])])

    description = strip_html(data.get('description', ''))
    # Truncate the description to ~350 chars, then cut back to the last full word to avoid splitting mid-word.
    snippet = description[:350].rsplit(' ', 1)[0] + "..." if len(description) > 350 else description

    add_row("Released", year)
    add_row("Rating", rating_display)
    add_row("Genres", genres or "Unknown")
    add_row("Developers", developers or "Unknown")
    add_row("Description", snippet)

    # Not every game has an official website — only show the link if RAWG returned one.
    website = data.get('website', '')
    if website:
        # fg="blue" and cursor="hand2" give it the look and feel of a hyperlink.
        # The <Button-1> event fires when the user left-clicks the label.
        link = tk.Label(win, text="Official Website", fg="blue", bg="darkorange",
                        cursor="hand2", font=("Helvetica", 10, "underline"))
        link.pack(pady=10)
        link.bind("<Button-1>", lambda e: webbrowser.open(website))

def save_played():
    # Converts the set to a list before writing — JSON doesn't support sets natively.
    # "w" mode creates the file if it doesn't exist, or overwrites it if it does.
    with open(FILE_PATH, "w") as f:
        json.dump(list(played_games), f)

def load_played():
    # global tells Python we want to reassign the module-level played_games variable,
    # not create a new local one that shadows it.
    global played_games
    try:
        with open(FILE_PATH, "r") as f:
            # json.load reads the file and returns a list; we convert it back to a set
            # so duplicate-checking stays fast throughout the rest of the program.
            played_games = set(json.load(f))
    except FileNotFoundError:
        # First run — no save file yet, so we just start with an empty set.
        played_games = set()

load_played()  # run once at startup so the set is populated before the UI appears

def clear_played_games():
    global played_games

    # messagebox.askyesno shows a Yes/No dialog — it returns True if the user clicks Yes.
    # Asking for confirmation before destructive actions is good UX.
    confirm = messagebox.askyesno("Confirm reset", "Are you sure you want to clear all played games?")
    if not confirm:
        return

    played_games.clear()  # empties the in-memory set immediately

    # Also delete the file so the cleared state persists after the app is closed and reopened.
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

load_favorites()  # run once at startup, same pattern as load_played()

def show_favorites():
    # Opens a separate window listing all favorited game names.
    win = tk.Toplevel(window)
    win.title("My Favorites")
    win.geometry("400x300")
    win.configure(bg="darkorange")

    tk.Label(win, text="My favorite games", font=("helvetica", 16, "bold"),
             bg="darkorange").pack(pady=10)
    
    # content_frame holds the list of names and gets rebuilt from scratch by refresh()
    # whenever favorites change, keeping the displayed list in sync with the data.
    content_frame = tk.Frame(win, bg="darkorange")
    content_frame.pack()

    def refresh():
        # Destroy all existing child widgets so we can redraw from the current state of favorites.
        for widget in content_frame.winfo_children():
            widget.destroy()

        if not favorites:
            tk.Label(content_frame, text="No favorites yet!", bg="darkorange", font=("Helvetica", 12)).pack(pady=3)
        else:
            for name in favorites:
                tk.Label(content_frame, text=name, bg="darkorange", font=("Helvetica", 12)).pack(pady=3)

    def clear_favorites():
        global favorites

        # parent=win anchors the dialog to the favorites window instead of the main window.
        confirm = messagebox.askyesno("confirm reset", "Are you sure you want to clear all favorites?", parent=win)
        if not confirm:
            return
        
        favorites.clear()

        if os.path.exists(FAVORITES_PATH):
            os.remove(FAVORITES_PATH)

        refresh()  # redraw the list immediately so the window shows "No favorites yet!"

        messagebox.showinfo("Reset", "Favorites cleared!", parent=win)
    
    tk.Button(win, text="Clear Favorites", command=clear_favorites, fg="white", bg="red").pack(pady=5)

    refresh()  # draw the initial list when the window first opens

def get_recommendation():
    # This is the main search function — it runs when the user clicks "Search" or hits Enter.
    # It builds a RAWG API URL from the current dropdown selections, fetches results,
    # filters out already-played games, and renders up to 3 results in the results frame.
    global results_frame

    # Clear out any previous results before drawing new ones.
    for widget in results_frame.winfo_children():
        widget.destroy()

    # Genre and platform are required — the API won't return useful results without them.
    if genre_var.get() == "Select Genre" or platform_var.get() == "Select Platform":
        messagebox.showwarning("Missing info", "Please select at least a genre and platform.")
        return

    # genre_overrides holds the primary genre slug(s) for the genres= param.
    # tag_list holds extra refinements (perspective, difficulty) that go in the tags= param.
    genre_overrides = []
    tag_list = []

    # Horror isn't a RAWG genre — it's actually a tag. We fake it by using "action" as the genre
    # and adding "horror" to tags, which gets us horror action games as a reasonable approximation.
    if genre_var.get() == "Horror":
        genre_overrides.append("action")
        tag_list.append("horror")
    else:
        genre_overrides.append(genre_map.get(genre_var.get(), "action"))

    # Side Scrolling/2D maps better to the "platformer" genre than to a perspective tag.
    if perspective_var.get() == "Side Scrolling/2D":
        genre_overrides.append("platformer")
    else:
        perspective = perspective_map.get(perspective_var.get(), "")
        # Only add the tag if the user actually picked something (not the default placeholder).
        if perspective and perspective_var.get() != "Select View Style":
            tag_list.append(perspective)

    # Casual doesn't have a slug in difficulty_map because it lives outside the "difficulty" concept —
    # it's handled separately here and appended directly as a tag.
    if difficulty_var.get() == "Casual":
        tag_list.append("casual")
    else:
        difficulty_tag = difficulty_map.get(difficulty_var.get(), "")
        if difficulty_tag:  # skip "Moderate" since its value is an empty string
            tag_list.append(difficulty_tag)

    genre = ",".join(genre_overrides)       # RAWG accepts multiple genres as a comma-separated string
    platform = platform_map.get(platform_var.get())
    keyword = keyword_entry.get()           # whatever the user typed in the free-text box (can be empty)
    tags_param = f"&tags={','.join(tag_list)}" if tag_list else ""  # only include the tags param if we have tags
    url = f"https://api.rawg.io/api/games?key={api_key}&genres={genre}&platforms={platform}{tags_param}&search={keyword}&page_size=10"

    response = requests.get(url)   # sends the GET request to the RAWG API
    data = response.json()         # parses the JSON response body into a Python dictionary

    if not data["results"]:
        # Show a temporary error message that auto-destroys itself after 3 seconds.
        msg = tk.Label(results_frame, text="No games found! Try different selections.", bg="darkorange", fg="black")
        msg.pack()
        window.after(3000, msg.destroy)  # window.after(ms, callback) schedules a call after a delay
        return

    games = data["results"]   # the list of game objects returned by the API

    # Remove any games the user has already marked as played, so we only surface new suggestions.
    filtered_games = [game for game in games if game['name'] not in played_games]

    if not filtered_games:
        msg = tk.Label(results_frame, text="You've played all these! Try different filters.", bg="darkorange", fg="black")
        msg.pack()
        window.after(3000, msg.destroy)
        return

    # Show at most 3 results — enough variety without overwhelming the UI.
    for game in filtered_games[:3]:

        # Each result gets its own frame so the rows stay visually grouped and independently laid out.
        game_frame = tk.Frame(results_frame, bg="darkorange")
        game_frame.pack(fill="x", pady=5)

        top_row = tk.Frame(game_frame, bg="darkorange")   # holds the game name and favorite button
        top_row.pack()

        bottom_row = tk.Frame(game_frame, bg="darkorange")  # holds the action buttons
        bottom_row.pack()

        game_label = tk.Label(top_row, text=game['name'], bg="darkorange",
                            fg="black", font=("Helvetica", 13, "bold"))
        game_label.pack(side="left", padx=10)

        # Show a filled heart if already favorited, hollow if not.
        fav_text = "♥" if game['name'] in favorites else "♡"
        fav_btn = tk.Button(top_row, text=fav_text, font=("Helvetica", 14),
                            bg="darkorange", relief="flat")
        # The lambda captures game['name'] and fav_btn by name at definition time.
        # Without "name=game['name']", all lambdas in the loop would share the same (last) value of game['name'].
        fav_btn.config(command=lambda name=game['name'], b=fav_btn: toggle_favorite(name, b))
        fav_btn.pack(side="left", padx=5)

        btn = tk.Button(bottom_row, text="Mark as Played",
                        command=lambda name=game['name']: mark_as_played(name))
        btn.pack(side="left", padx=10)

        details_btn = tk.Button(bottom_row, text="More Details",
                                command=lambda gid=game['id']: show_details(gid))
        details_btn.pack(side="left", padx=10)

def mark_as_played(game_name):
    # Adds the game to the in-memory set, persists it to disk, then refreshes the search results
    # so the newly played game disappears from the list without the user having to re-search.
    played_games.add(game_name)
    save_played()
    get_recommendation()

def toggle_favorite(game_name, btn):
    # discard() is like remove() but won't raise an error if the item isn't in the set.
    if game_name in favorites:
        favorites.discard(game_name)
        btn.config(text="♡")   # update the button icon to match the new state
    else:
        favorites.add(game_name)
        btn.config(text="♥")
    save_favorites()   # persist the updated favorites to disk immediately


# ─── UI SETUP ────────────────────────────────────────────────────────────────
# Everything below this point builds the window and its widgets.
# None of this code produces visible output until window.mainloop() starts the event loop at the bottom.

window = tk.Tk()                  # creates the main application window (there can only be one Tk() per app)
window.title("Game Recommender")  # sets the text shown in the OS title bar
window.geometry("800x600")        # sets the initial window size in pixels: widthxheight
window.configure(bg="darkorange") # sets the window's background color

# random.choice picks one string at random from the list each time the app opens.
title_label = tk.Label(window, text=random.choice(["What's up! Let's find you a game!", "Welcome, looking for a new game?", "What a day for a new game!"]), font=("Helvetica", 20, "bold"), fg="black", bg="darkorange")
title_label.pack()   # .pack() places the widget in the window, stacking top to bottom by default

# A container frame that holds all four dropdowns in a single horizontal row.
# Using a frame + .grid() inside it gives us precise column control that .pack() alone can't.
dropdowns_frame = tk.Frame(window, bg="darkorange")
dropdowns_frame.pack(pady=10)

# tk.StringVar is a special observable string — OptionMenu watches it and updates automatically when it changes.
# .set() puts a default placeholder in the dropdown before the user makes a selection.
genre_var = tk.StringVar()
genre_var.set("Select Genre")
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

# A free-text entry for optional keywords like "open world" or "stealth".
# insertbackground sets the color of the blinking text cursor inside the box.
keyword_entry = tk.Entry(window, width=40, fg="white", bg="black", insertbackground="white")
keyword_entry.pack(pady=10)

# command= wires a function to the button — it's called with no arguments when the button is clicked.
search_button = tk.Button(window, text="Search", command=get_recommendation, fg="white", bg="black")
search_button.pack(pady=10)

clear_button = tk.Button(window, text="Reset played games", command=clear_played_games, fg="white", bg="red")
clear_button.pack(pady=5)

favorites_button = tk.Button(window, text="♥ My Favorites ♥", command=show_favorites, fg="white", bg="hotpink")
favorites_button.pack(pady=5)

# results_frame is a container that get_recommendation() populates with game widgets after each search.
# Declared at the top level so get_recommendation() can access it as a global.
results_frame = tk.Frame(window, bg="darkorange")
results_frame.pack(pady=20)

# Binds the Return/Enter key to the search function so the user doesn't have to click the button.
# The lambda accepts the event object that tkinter passes automatically, then ignores it.
window.bind("<Return>", lambda event: get_recommendation())

# Starts the event loop — this hands control to tkinter, which listens for user actions
# (clicks, keypresses, window resizes) and calls the appropriate handlers.
# The program stays here until the window is closed.
window.mainloop()