import tkinter as tk          # tkinter is Python's built-in GUI library — lets you build windows, buttons, labels, etc.
import requests               # lets you make HTTP requests (like calling an API)
from dotenv import load_dotenv  # loads variables from a .env file so you can keep secrets out of your code
import os                     # lets you access environment variables and interact with the operating system
import random                 # gives you tools for randomness (used to randomly pick a greeting here)
from tkinter import ttk       # an extended/themed widget set that comes with tkinter (imported but not used here yet)
import json
from tkinter import messagebox

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, "played_games.json")

load_dotenv()                         # reads your .env file and loads its contents into the environment
api_key = os.getenv("RAWG_KEY")       # grabs your secret API key from the environment (not hardcoded, which is safer)

played_games = set()

# A dictionary that maps readable genre names to the API's expected slug values
# When the user picks "Role-Playing(RPG)", the API actually needs "role-playing-games" — this handles that translation
genre_map = {
    "Action": "action",
    "Adventure": "adventure",
    "Card & Board": "card",
    "Fighting": "fighting",
    "Horror": "horror",
    "Platformer": "platformer",
    "Puzzle": "puzzle",
    "Racing": "racing",
    "Rhythm & Music": "music",
    "Role-Playing(RPG)": "role-playing-games",
    "Shooter": "shooter",
    "Simulation": "simulation",
    "Sports": "sports",
    "Strategy": "strategy",
    "Survival": "survival",
    "Party & Social": "family"
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

def get_recommendation():   # this function runs when the user clicks "Search"
    global results_frame

    if genre_var.get() == "select Genre" or platform_var.get() == "Select Platform":
        for widget in results_frame.winfo_children():
            widget.destroy()

        messagebox.showwarning("Missing info", "Please select at least a genre and platform.")
        return

    genre = genre_map.get(genre_var.get())          # .get() on the StringVar reads the current dropdown value, then looks it up in the dict
    perspective = perspective_var.get()             # reads the selected perspective (e.g. "First Person")
    difficulty = difficulty_var.get()               # reads the selected difficulty
    platform = platform_map.get(platform_var.get()) # same pattern — reads the platform dropdown and translates it to an API ID
    keyword = keyword_entry.get()                   # reads whatever the user typed in the text box

    # builds the full API URL with all the filters embedded as query parameters
    # perspective, difficulty, and keyword all go into "search" — the API treats them as freetext
    url = f"https://api.rawg.io/api/games?key={api_key}&genres={genre}&platforms={platform}&search={perspective} {difficulty} {keyword}&page_size=3"
    
    response = requests.get(url)   # sends the GET request to the RAWG API
    data = response.json()     # parses the JSON response into a Python dictionary

    if not data["results"]:                                       # if the results list is empty, no games matched
        tk.Label(results_frame, text="No games found! Try different selections.", bg="darkorange", fg="black").pack()  # updates the label text with an error message
        return                                                      # exits the function early so nothing else runs

    games = data["results"]                          # the list of game objects returned by the API

    filtered_games = []

    for game in games:
        if game['name'] not in played_games:
            filtered_games.append(game)

    if not filtered_games:
        tk.Label(results_frame, text="You've played all these! Try different filters.", bg="darkorange", fg="black").pack()
        return

    for i, game in enumerate(filtered_games[:3]):   # loops over up to the first 3 results; enumerate gives you both the index (i) and the item
        
        rating = game['rating']            # pulls the rating value out of the game object
        if rating == 0:
            rating_display = "Not yet rated"      # handles the case where a game hasn't been rated yet
        else:
            rating_display = f"{rating} / 5.0"   # formats it as a readable string

        game_frame = tk.Frame(results_frame, bg="darkorange")
        game_frame.pack(fill="x", pady=5)

        game_label = tk.Label(game_frame,
                              text=f"{game['name']} | Rating: {rating_display}",
                              bg="darkorange",
                              fg="black",
                              font=("Helvetica", 12))
        game_label.grid(row=0, column=0, padx=10)

        btn = tk.Button(game_frame,
                        text="Mark as Played",
                        command=lambda name=game['name']: mark_as_played(name))
        btn.grid(row=0, column=1, padx=10)

def mark_as_played(game_name):
    played_games.add(game_name)
    save_played()
    get_recommendation() # refresh UI
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
genre_dropdown = tk.OptionMenu(dropdowns_frame, genre_var, "Action", "Adventure", "Card & Board", "Fighting", "Horror", "Platformer", "Puzzle", "Racing", "Rhythm & Music", "Role-Playing(RPG)", "Shooter", "Simulation", "Sports", "Strategy", "Survival", "Party & Social")
genre_dropdown.grid(row=0, column=0, padx=10, pady=10)

perspective_var = tk.StringVar()
perspective_var.set("Select View Style")
perspective_dropdown = tk.OptionMenu(dropdowns_frame, perspective_var, "2.5D", "First Person", "First Person VR", "Fixed Camera", "Isometric", "Over-The-Shoulder", "Point-And-Click", "Scrolling Shooter/Shmup", "Side Scrolling/2D", "Tactical/Strategy View", "Text-Based", "Third Person", "Top-Down", "Visual Novel")
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

results_frame = tk.Frame(window, bg="darkorange")
results_frame.pack(pady=20)

window.bind("<Return>", lambda event: get_recommendation()) # binds the return key to the search button

window.mainloop()   # starts the event loop — this keeps the window open and listening for user interactions until it's closed