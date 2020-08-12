import os

import sqlite3  
from sqlite3 import Error

from flask import Flask, flash, jsonify, redirect, render_template, request, session, Response
from markupsafe import escape

import mimetypes
from collections import Counter

from urllib import parse

app = Flask(__name__)

app.secret_key = 'oinqiobntoiunbqt'

def convertToBinaryData(filename):
    #Convert digital data to binary format
    with open(filename, 'rb') as file:
        blobData = file.read()
    return blobData

def apology(message):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", bottom=escape(message))

def apology_choose(message):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology_choose.html", bottom=escape(message))


@app.route("/")
def welcome():
    return render_template("welcome.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    conn = sqlite3.connect('MyWardrobe.db', check_same_thread=False)
    c = conn.cursor()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        username=request.form.get("username")
        password=request.form.get("confirmation")

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Must provide password")

        # Ensure password confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("Must provide password confirmation")

        # Ensure password confirmation matches password
        elif not request.form.get("confirmation") == request.form.get("password"):
            return apology("Password confirmation must match password")

        # Check username does not already exist and if not add username to database
        result = c.execute("INSERT INTO users(username, password) VALUES(?,?)", (username, password))
        conn.commit()

        if not result:
            return apology("That username has already been taken")

        # Direct user to select page
        return render_template("/select.html")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

    return apology("Please register")

@app.route("/login", methods=["GET", "POST"])
def login():

    conn = sqlite3.connect('MyWardrobe.db', check_same_thread=False)
    c = conn.cursor()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        username=request.form.get("username")
        password=request.form.get("password")

        # Ensure username was submitted
        if not username:
            return apology("Must provide username")

        # Ensure password was submitted
        elif not password:
            return apology("Must provide password")

        # Query database for username
        rows = c.execute("SELECT * FROM users WHERE username=?", (username,))
        rows = c.fetchall()

        for row in rows:

            # Ensure username exists and password is correct
            if len(rows) != 1 or not password:
                return apology("Invalid username and/or password")

        # Remember which user has logged in
        session['username'] = request.form['username']

        # Redirect user to selection page
        return redirect("/choose")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/choose")
def choose():
    return render_template("choose.html")

@app.route("/select", methods=["GET"])
def select():
    return render_template("select.html")

@app.route("/select", methods=["POST"])
def select_items():

    conn = sqlite3.connect('MyWardrobe.db', check_same_thread=False)
    c = conn.cursor()

    # Get data from 'Select' form
    if request.method == 'POST':

        season = request.form.get('season')
        if not season:
            return apology_choose("Please select a season")
        clothes = []

        

        if request.form.getlist('topsdresses'):

            ctype = 'Top/Dress'
            season = request.form.get('season')
            topsdresses_colors = request.form.getlist('topsdresses_colors')
            topsdresses_patterns = request.form.getlist('topsdresses_patterns')
            topsdresses_styles = request.form.getlist('topsdresses_styles')
        
            # Join all tags into one list
            season = season.split()
            ctype = ctype.split()
            alltags = season + topsdresses_colors + topsdresses_patterns + topsdresses_styles + ctype

            # Get a list of all relevant items
            selected = c.execute("SELECT items.itemid FROM items JOIN mapping ON items.itemid = mapping.item JOIN tags ON tags.tagid = mapping.tag WHERE tagname IN (" + ",".join("?"*len(alltags)) + ")", alltags).fetchall()
            selected = [ item[0] for item in selected ]

            n = len(selected) 

            data = Counter(selected) 
            get_mode = dict(data) 
            topsdresses = [k for k, v in get_mode.items() if v == max(list(data.values()))]
            clothes.append(topsdresses)

        if request.form.get('bottoms'):

            ctype = 'Bottom'
            season = request.form.get('season')
            bottoms_colors = request.form.getlist('bottoms_colors')
            bottoms_patterns = request.form.getlist('bottoms_patterns')
            bottoms_styles = request.form.getlist('bottoms_styles')
        
            # Join all tags into one list
            season = season.split()
            ctype = ctype.split()
            alltags = bottoms_colors + bottoms_patterns + bottoms_styles + ctype + season

            # Get a list of all relevant items
            selected = c.execute("SELECT items.itemid FROM items JOIN mapping ON items.itemid = mapping.item JOIN tags ON tags.tagid = mapping.tag WHERE tagname IN (" + ",".join("?"*len(alltags)) + ")", alltags).fetchall()
            selected = [ item[0] for item in selected ]

            n = len(selected) 

            data = Counter(selected) 
            get_mode = dict(data) 
            bottoms = [k for k, v in get_mode.items() if v == max(list(data.values()))]
            clothes.append(bottoms)

        if request.form.get('shoes'):

            ctype = 'Shoes'
            season = request.form.get('season')
            shoes_colors = request.form.getlist('shoes_colors')
            shoes_patterns = request.form.getlist('shoes_patterns')
            shoes_styles = request.form.getlist('shoes_styles')
        
            # Join all tags into one list
            season = season.split()
            ctype = ctype.split()
            alltags = season + shoes_colors + shoes_patterns + shoes_styles + ctype

            # Get a list of all relevant items
            selected = c.execute("SELECT items.itemid FROM items JOIN mapping ON items.itemid = mapping.item JOIN tags ON tags.tagid = mapping.tag WHERE tagname IN (" + ",".join("?"*len(alltags)) + ")", alltags).fetchall()
            selected = [ item[0] for item in selected ]

            n = len(selected) 

            data = Counter(selected) 
            get_mode = dict(data) 
            shoes = [k for k, v in get_mode.items() if v == max(list(data.values()))]
            clothes.append(shoes)

        if request.form.get('scarves'):

            ctype = 'Scarf'
            season = request.form.get('season')
            scarves_colors = request.form.getlist('scarves_colors')
            scarves_patterns = request.form.getlist('scarves_patterns')
            scarves_styles = request.form.getlist('scarves_styles')
        
            # Join all tags into one list
            season = season.split()
            ctype = ctype.split()
            alltags = season + scarves_colors + scarves_patterns + scarves_styles + ctype

            # Get a list of all relevant items
            selected = c.execute("SELECT items.itemid FROM items JOIN mapping ON items.itemid = mapping.item JOIN tags ON tags.tagid = mapping.tag WHERE tagname IN (" + ",".join("?"*len(alltags)) + ")", alltags).fetchall()
            selected = [ item[0] for item in selected ]

            n = len(selected) 

            data = Counter(selected) 
            get_mode = dict(data) 
            scarves = [k for k, v in get_mode.items() if v == max(list(data.values()))]
            clothes.append(scarves)

        if request.form.get('hats'):

            ctype = 'Hat'
            season = request.form.get('season')
            hats_colors = request.form.getlist('hats_colors')
            hats_patterns = request.form.getlist('hats_patterns')
            hats_styles = request.form.getlist('hats_styles')
        
            # Join all tags into one list
            season = season.split()
            ctype = ctype.split()
            alltags = season + hats_colors + hats_patterns + hats_styles + ctype

            # Get a list of all relevant items
            selected = c.execute("SELECT items.itemid FROM items JOIN mapping ON items.itemid = mapping.item JOIN tags ON tags.tagid = mapping.tag WHERE tagname IN (" + ",".join("?"*len(alltags)) + ")", alltags).fetchall()
            selected = [ item[0] for item in selected ]

            n = len(selected) 

            data = Counter(selected) 
            get_mode = dict(data) 
            hats = [k for k, v in get_mode.items() if v == max(list(data.values()))]
            clothes.append(hats)

        if request.form.get('jewellery'):

            ctype = 'Jewellery'
            season = request.form.get('season')
            jewellery_colors = request.form.getlist('jewellery_colors')
            jewellery_patterns = request.form.getlist('jewellery_patterns')
            jewellery_styles = request.form.getlist('jewellery_styles')
        
            # Join all tags into one list
            season = season.split()
            ctype = ctype.split()
            alltags = jewellery_colors + jewellery_patterns + jewellery_styles + ctype + season

            # Get a list of all relevant items
            selected = c.execute("SELECT items.itemid FROM items JOIN mapping ON items.itemid = mapping.item JOIN tags ON tags.tagid = mapping.tag WHERE tagname IN (" + ",".join("?"*len(alltags)) + ")", alltags).fetchall()
            selected = [ item[0] for item in selected ]

            n = len(selected) 

            data = Counter(selected) 
            get_mode = dict(data) 
            jewellery = [k for k, v in get_mode.items() if v == max(list(data.values()))]
            clothes.append(jewellery)

        if request.form.get('jacketscoats'):

            ctype = 'Jacket/Coat'
            season = request.form.get('season')
            jacketscoats_colors = request.form.getlist('jacketscoats_colors')
            jacketscoats_patterns = request.form.getlist('jacketscoats_patterns')
            jacketscoats_styles = request.form.getlist('jacketscoats_styles')
        
            # Join all tags into one list
            season = season.split()
            ctype = ctype.split()
            alltags = season + jacketscoats_colors + jacketscoats_patterns + jacketscoats_styles + ctype

            # Get a list of all relevant items
            selected = c.execute("SELECT items.itemid FROM items JOIN mapping ON items.itemid = mapping.item JOIN tags ON tags.tagid = mapping.tag WHERE tagname IN (" + ",".join("?"*len(alltags)) + ")", alltags).fetchall()
            selected = [ item[0] for item in selected ]

            n = len(selected) 

            data = Counter(selected) 
            get_mode = dict(data) 
            jacketscoats = [k for k, v in get_mode.items() if v == max(list(data.values()))]
            clothes.append(jacketscoats)

        if request.form.get('bags'):

            ctype = 'Bag'
            season = request.form.get('season')
            bags_colors = request.form.getlist('bags_colors')
            bags_patterns = request.form.getlist('bags_patterns')
            bags_styles = request.form.getlist('bags_styles')
        
            # Join all tags into one list
            season = season.split()
            ctype = ctype.split()
            alltags = season + bags_colors + bags_patterns + bags_styles + ctype

            # Get a list of all relevant items
            selected = c.execute("SELECT items.itemid FROM items JOIN mapping ON items.itemid = mapping.item JOIN tags ON tags.tagid = mapping.tag WHERE tagname IN (" + ",".join("?"*len(alltags)) + ")", alltags).fetchall()
            selected = [ item[0] for item in selected ]

            n = len(selected) 

            data = Counter(selected) 
            get_mode = dict(data) 
            bags = [k for k, v in get_mode.items() if v == max(list(data.values()))]
            clothes.append(bags)

            print(clothes)

    return render_template("view.html", clothes=clothes)

            
@app.route("/add", methods=["GET"])
def addition():
    return render_template("addition.html")

@app.route("/add", methods=["POST"])
def addItem():

    conn = sqlite3.connect('MyWardrobe.db', check_same_thread=False)
    c = conn.cursor()

    # Get data from 'Addition' form
    if request.method == 'POST':

        season = request.form.get('season')
        ctype = request.form.get('type')
        colors = request.form.getlist('colors')
        patterns = request.form.getlist('patterns')
        styles = request.form.getlist('styles')
        uf = request.files['file']
            
        if season is None or ctype is None or colors is None or patterns is None or styles is None or uf is None:
            return apology_choose("Please complete the form")

        # Get user id
        username = session.get("username")
        user_id = c.execute("SELECT id FROM users WHERE username=?", (username,))
        user_id = c.fetchall()
        user_id = (user_id[0])
        user_id = (user_id[0])

        # Enter item into 'items' table
        c.execute("INSERT INTO items (id, itempic) VALUES (?,?)", (user_id, memoryview(uf.read())))
        conn.commit()

        # Get item_id
        item_id = c.execute("SELECT itemid FROM items ORDER BY itemid DESC limit 1")
        item_id = c.fetchall()
        item_id = (item_id[0])
        item_id = (item_id[0])

        # Get season tag_id and enter into mapping table
        season_id = c.execute("SELECT tagid FROM tags WHERE tagname=?", (season,))
        season_id = c.fetchall()
        season_id = (season_id[0])
        season_id = (season_id[0])
        c.execute("INSERT INTO mapping VALUES (?, ?)", (item_id, season_id,))
        conn.commit()

        # Get type tag_id and enter into mapping table
        ctype_id = c.execute("SELECT tagid FROM tags WHERE tagname=?", (ctype,))
        ctype_id = c.fetchall()
        ctype_id = (ctype_id[0])
        ctype_id = (ctype_id[0])
        c.execute("INSERT INTO mapping VALUES (?, ?)", (item_id, ctype_id,))
        conn.commit()

        # Get color tag_ids and enter into mapping table
        for color in colors:
            color_id = c.execute("SELECT tagid FROM tags WHERE tagname=?", (color,))
            color_id = c.fetchall()
            color_id = (color_id[0])
            color_id = (color_id[0])
            c.execute("INSERT INTO mapping VALUES (?, ?)", (item_id, color_id,))
            conn.commit()

        # Get pattern tag_ids and enter into mapping table
        for pattern in patterns:
            pattern_id = c.execute("SELECT tagid FROM tags WHERE tagname=?", (pattern,))
            pattern_id = c.fetchall()
            pattern_id = (pattern_id[0])
            pattern_id = (pattern_id[0])
            c.execute("INSERT INTO mapping VALUES (?, ?)", (item_id, pattern_id,))
            conn.commit()

        # Get style tag_ids and enter into mapping table
        for style in styles:
            style_id = c.execute("SELECT tagid FROM tags WHERE tagname=?", (style,))
            style_id = c.fetchall()
            style_id = (style_id[0])
            style_id = (style_id[0])
            c.execute("INSERT INTO mapping VALUES (?, ?)", (item_id, style_id,))
            conn.commit()

        return render_template("addSuccess.html")

@app.route("/image")
def image():

    conn = sqlite3.connect('MyWardrobe.db', check_same_thread=False)
    c = conn.cursor()

    itemid = request.args.get('itemid')

    image = c.execute("SELECT itempic FROM items WHERE itemid=?", [itemid]) 
    image = c.fetchall()
    image = (image[0])
    image = (image[0])

    return Response(response=image, mimetype='image/jpeg')



@app.route("/donate", methods=["GET"])
def donation():
    return render_template("donation.html")

@app.route("/donate", methods=["POST"])
def donateItem():

    conn = sqlite3.connect('MyWardrobe.db', check_same_thread=False)
    c = conn.cursor()

    if request.method == 'POST':

        if request.form['submit'] == 'select':

            season = request.form.get('season')

            ctype = request.form.get('type')
            colors = request.form.getlist('colors')
            patterns = request.form.getlist('patterns')
            styles = request.form.getlist('styles')

            if not season: 
                return apology_choose("Please select a season")

            if not ctype:
                return apology_choose("Please select a type of item")


            # Join all tags into one list
            season = season.split()
            ctype = ctype.split()
            alltags = season + colors + patterns + styles + ctype

            # Get a list of all relevant items
            selected = c.execute("SELECT items.itemid FROM items JOIN mapping ON items.itemid = mapping.item JOIN tags ON tags.tagid = mapping.tag WHERE tagname IN (" + ",".join("?"*len(alltags)) + ")", alltags)
            selected = [ item[0] for item in selected ]

            n = len(selected) 

            data = Counter(selected) 
            get_mode = dict(data) 
            donations = [k for k, v in get_mode.items() if v == max(list(data.values()))]

            return render_template("donation.html", donations=donations)

        if request.form['submit'] == 'enterno':

            itemno = request.form.getlist('itemno')

            return render_template("sure_donate.html", itemno=itemno)
    


@app.route("/sure_donate", methods=["POST"])
def sure_donate():

    conn = sqlite3.connect('MyWardrobe.db', check_same_thread=False)
    c = conn.cursor()

    if request.method == 'POST':

        itemid = request.form.get("itemid")

        if request.form.get('sure') == 'yes':
            c.execute('DELETE FROM items WHERE itemid=?', (itemid,))
            conn.commit()
        else:
            return render_template("donation.html")

        return render_template("deleteSuccess.html")


if __name__ == "__main__":
    app.run(debug=True)



    