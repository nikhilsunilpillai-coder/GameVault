from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from pathlib import Path
from urllib.parse import urlparse

app = Flask(__name__)
app.secret_key = "gamevault-v5-dev-key"

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "database" / "gamevault.db"

REAL_IMAGES = {
    "Minecraft": "https://www.minecraft.net/content/dam/minecraftnet/games/minecraft/key-art/NewKeyArt_Header.jpg",
    "Grand Theft Auto V": "https://mightyape.co.ke/public/uploads/all/kBt4D8i7PbYQAlZUNRf37jC90nZmL5im5LpYKVuU.jpg",
    "Elden Ring": "https://rushgame.co/cdn/shop/files/elden-ring-pc-steam-cd-key-na-cover01_1200x1422.jpg?v=1756276424",
    "Valorant": "https://images.stopgame.ru/games/logos/19592/c560x560/62PEyFi2MwDpL91qF8_FsA/valorant-square_1.jpg",
    "Red Dead Redemption 2": "https://raw.githubusercontent.com/maxym11/ps5-ui-assets/master/PS5%20Covers/rdr2-cov.jpg",
    "Stardew Valley": "https://images.igdb.com/igdb/image/upload/t_1080p_2x/coa93h.webp",
    "Batman: Arkham Asylum": "https://cdn.akamai.steamstatic.com/steam/apps/35140/header.jpg",
    "Batman: Arkham City": "https://cdn.akamai.steamstatic.com/steam/apps/200260/header.jpg",
    "Batman: Arkham Origins": "https://cdn.akamai.steamstatic.com/steam/apps/209000/header.jpg",
    "Batman: Arkham Knight": "https://cdn.akamai.steamstatic.com/steam/apps/208650/header.jpg",
}

GAME_TAGS = {
    "Minecraft": "Sandbox,Survival,Building,Open World,Multiplayer,Singleplayer",
    "Grand Theft Auto V": "Action,Adventure,Open World,Singleplayer,Multiplayer,Story Rich",
    "Elden Ring": "Action RPG,RPG,Open World,Fantasy,Combat,Singleplayer",
    "Valorant": "Action,FPS,Multiplayer,Competitive,Free to Play,First-Person",
    "Red Dead Redemption 2": "Action,Adventure,Open World,Singleplayer,Story Rich,Western",
    "Stardew Valley": "Indie,Simulation,RPG,Farming,Relaxing,Pixel Graphics,Singleplayer",
    "Batman: Arkham Asylum": "Action-Adventure,Superhero,Stealth,Story Rich,Singleplayer,Combat",
    "Batman: Arkham City": "Action-Adventure,Open World,Superhero,Stealth,Story Rich,Singleplayer,Combat",
    "Batman: Arkham Origins": "Action-Adventure,Superhero,Stealth,Story Rich,Singleplayer,Combat,Prequel",
    "Batman: Arkham Knight": "Action-Adventure,Open World,Superhero,Stealth,Story Rich,Singleplayer,Combat",
}


STORE_DATA = {
    "Minecraft": [
        ("Minecraft", "https://www.minecraft.net/en-us/store/minecraft-java-bedrock-edition-pc", "PC"),
        ("Microsoft Store", "https://apps.microsoft.com/detail/9pgw18npbz6g", "PC"),
        ("PlayStation Store", "https://store.playstation.com/", "PlayStation"),
        ("Xbox", "https://www.xbox.com/games/store/minecraft/9pgw18npbz6g", "Xbox"),
        ("Nintendo eShop", "https://www.nintendo.com/store/products/minecraft-switch/", "Nintendo Switch"),
        ("Google Play", "https://play.google.com/store/apps/details?id=com.mojang.minecraftpe", "Android"),
        ("App Store", "https://apps.apple.com/app/minecraft/id479516143", "iOS"),
    ],
    "Grand Theft Auto V": [
        ("Rockstar Games", "https://www.rockstargames.com/gta-v", "PC / Console"),
        ("Steam", "https://store.steampowered.com/app/3240220/Grand_Theft_Auto_V_Enhanced/", "PC"),
        ("Epic Games Store", "https://store.epicgames.com/en-US/p/grand-theft-auto-v", "PC"),
        ("PlayStation Store", "https://store.playstation.com/", "PlayStation"),
        ("Xbox", "https://www.xbox.com/games/store/grand-theft-auto-v/", "Xbox"),
    ],
    "Elden Ring": [
        ("Bandai Namco", "https://www.bandainamcoent.com/games/elden-ring", "Official"),
        ("Steam", "https://store.steampowered.com/app/1245620/ELDEN_RING/", "PC"),
        ("PlayStation Store", "https://store.playstation.com/", "PlayStation"),
        ("Xbox", "https://www.xbox.com/games/store/elden-ring/", "Xbox"),
    ],
    "Valorant": [
        ("Riot Games", "https://playvalorant.com/en-us/", "PC"),
        ("PlayStation", "https://playvalorant.com/en-us/console/", "PlayStation 5"),
        ("Xbox", "https://playvalorant.com/en-us/console/", "Xbox Series X|S"),
    ],
    "Red Dead Redemption 2": [
        ("Rockstar Games", "https://www.rockstargames.com/reddeadredemption2", "Official"),
        ("Steam", "https://store.steampowered.com/app/1174180/Red_Dead_Redemption_2/", "PC"),
        ("Epic Games Store", "https://store.epicgames.com/en-US/p/red-dead-redemption-2", "PC"),
        ("PlayStation Store", "https://store.playstation.com/", "PlayStation"),
        ("Xbox", "https://www.xbox.com/games/store/red-dead-redemption-2/", "Xbox"),
    ],
    "Stardew Valley": [
        ("Steam", "https://store.steampowered.com/app/413150/Stardew_Valley/", "PC"),
        ("GOG", "https://www.gog.com/game/stardew_valley", "PC"),
        ("PlayStation Store", "https://store.playstation.com/", "PlayStation"),
        ("Xbox", "https://www.xbox.com/games/store/stardew-valley/", "Xbox"),
        ("Nintendo eShop", "https://www.nintendo.com/store/products/stardew-valley-switch/", "Nintendo Switch"),
        ("Google Play", "https://play.google.com/store/apps/details?id=com.chucklefish.stardewvalley", "Android"),
        ("App Store", "https://apps.apple.com/app/stardew-valley/id1406710800", "iOS"),
    ],
}

ARKHAM_STORE_DATA = {
    "Batman: Arkham Asylum": [
        ("Steam", "https://store.steampowered.com/app/35140/Batman_Arkham_Asylum_GOTY_Edition/", "PC"),
        ("PlayStation Store", "https://store.playstation.com/", "PlayStation"),
        ("Xbox", "https://www.xbox.com/", "Xbox"),
    ],
    "Batman: Arkham City": [
        ("Steam", "https://store.steampowered.com/app/200260/Batman_Arkham_City_GOTY/", "PC"),
        ("PlayStation Store", "https://store.playstation.com/", "PlayStation"),
        ("Xbox", "https://www.xbox.com/", "Xbox"),
    ],
    "Batman: Arkham Origins": [
        ("Steam", "https://store.steampowered.com/app/209000/Batman_Arkham_Origins/", "PC"),
        ("DC Games", "https://www.dc.com/games/batman-arkham-origins-2013", "Official"),
    ],
    "Batman: Arkham Knight": [
        ("Steam", "https://store.steampowered.com/app/208650/Batman_Arkham_Knight/", "PC"),
        ("PlayStation Store", "https://store.playstation.com/", "PlayStation"),
        ("Xbox", "https://www.xbox.com/", "Xbox"),
    ],
}



# Expanded demo catalogue for GameVault. Values are curated demo metadata; prices are sample/admin-maintained.
EXTRA_GAMES = [
    ("Cyberpunk 2077", "CD PROJEKT RED", "CD PROJEKT RED", "2020-12-10", "Action RPG", "M", 4.5,
     "An open-world action RPG set in Night City, a megalopolis obsessed with power, glamour and body modification.",
     "Explore Night City, complete quests, customize V, use weapons and cyberware, and make story choices.",
     "https://cdn.akamai.steamstatic.com/steam/apps/1091500/header.jpg", "RPG,Open World,Action,Story Rich,Cyberpunk,Singleplayer"),
    ("Baldur's Gate 3", "Larian Studios", "Larian Studios", "2023-08-03", "RPG", "M", 4.9,
     "A party-based role-playing game set in the Forgotten Realms.",
     "Create a character, build a party, explore, make choices and resolve encounters through turn-based combat and dialogue.",
     "https://cdn.akamai.steamstatic.com/steam/apps/1086940/header.jpg", "RPG,Turn-Based,Fantasy,Story Rich,Choices Matter,Multiplayer"),
    ("The Witcher 3: Wild Hunt", "CD PROJEKT RED", "CD PROJEKT RED", "2015-05-18", "RPG", "M", 4.8,
     "An open-world fantasy RPG following Geralt of Rivia across a war-torn continent.",
     "Explore, investigate contracts, fight monsters, develop skills and make choices that affect quests and characters.",
     "https://cdn.akamai.steamstatic.com/steam/apps/292030/header.jpg", "RPG,Open World,Fantasy,Story Rich,Singleplayer"),
    ("The Elder Scrolls V: Skyrim Special Edition", "Bethesda Game Studios", "Bethesda Softworks", "2016-10-28", "RPG", "M", 4.7,
     "An open-world fantasy RPG set in the province of Skyrim.",
     "Explore freely, complete quests, develop skills, use magic and weapons, and shape your character's journey.",
     "https://cdn.akamai.steamstatic.com/steam/apps/489830/header.jpg", "RPG,Open World,Fantasy,Adventure,Singleplayer"),
    ("Counter-Strike 2", "Valve", "Valve", "2023-09-27", "FPS", "M", 4.3,
     "A competitive tactical first-person shooter built around team-based objective play.",
     "Teams compete in rounds using weapons, economy management, tactics and precise gunplay.",
     "https://cdn.akamai.steamstatic.com/steam/apps/730/header.jpg", "FPS,Multiplayer,Competitive,Action,Team-Based,Free to Play"),
    ("Apex Legends", "Respawn Entertainment", "Electronic Arts", "2019-02-04", "FPS", "T", 4.4,
     "A free-to-play hero battle royale shooter featuring distinct Legends and squad-based combat.",
     "Choose a Legend, form a squad, loot equipment, use abilities and compete to become the last squad standing.",
     "https://cdn.akamai.steamstatic.com/steam/apps/1172470/header.jpg", "FPS,Battle Royale,Multiplayer,Free to Play,Hero Shooter"),
    ("DOOM Eternal", "id Software", "Bethesda Softworks", "2020-03-20", "FPS", "M", 4.7,
     "A fast-paced first-person shooter focused on aggressive combat against demonic enemies.",
     "Fight demons using a large arsenal, manage health and ammunition, and chain movement with combat abilities.",
     "https://cdn.akamai.steamstatic.com/steam/apps/782330/header.jpg", "FPS,Action,Demons,Fast-Paced,Singleplayer"),
    ("God of War", "Santa Monica Studio", "Sony Interactive Entertainment", "2022-01-14", "Action-Adventure", "M", 4.8,
     "An action-adventure journey following Kratos and Atreus through a Norse-inspired world.",
     "Explore, solve environmental puzzles, upgrade equipment and fight enemies with the Leviathan Axe and other abilities.",
     "https://cdn.akamai.steamstatic.com/steam/apps/1593500/header.jpg", "Action-Adventure,Story Rich,Mythology,Combat,Singleplayer"),
    ("Ghost of Tsushima", "Sucker Punch Productions", "Sony Interactive Entertainment", "2024-05-16", "Action-Adventure", "M", 4.7,
     "An open-world action adventure about a samurai defending Tsushima during a Mongol invasion.",
     "Explore the island, master sword combat, use stealth, complete quests and customize Jin's abilities.",
     "https://cdn.akamai.steamstatic.com/steam/apps/2215430/header.jpg", "Action-Adventure,Open World,Samurai,Story Rich,Singleplayer"),
    ("Devil May Cry 5", "Capcom", "Capcom", "2019-03-08", "Action", "M", 4.8,
     "A stylish character-action game featuring multiple playable demon hunters.",
     "Switch between characters, chain weapon combos, use special abilities and defeat increasingly powerful demons.",
     "https://cdn.akamai.steamstatic.com/steam/apps/601150/header.jpg", "Action,Combat,Hack and Slash,Stylish,Singleplayer"),
    ("Resident Evil 4", "CAPCOM", "CAPCOM", "2023-03-24", "Survival Horror", "M", 4.8,
     "A survival-horror action game following Leon S. Kennedy on a rescue mission in rural Europe.",
     "Explore, manage resources, solve puzzles and fight hostile enemies using firearms, knives and other equipment.",
     "https://cdn.akamai.steamstatic.com/steam/apps/2050650/header.jpg", "Horror,Survival Horror,Action,Story Rich,Singleplayer"),
    ("Silent Hill 2", "Bloober Team", "KONAMI", "2024-10-07", "Survival Horror", "M", 4.5,
     "A psychological survival-horror game centered on James Sunderland's journey through the fog-shrouded town.",
     "Explore, solve puzzles, manage resources and confront creatures while uncovering the story of Silent Hill.",
     "https://cdn.akamai.steamstatic.com/steam/apps/2124490/header.jpg", "Horror,Survival Horror,Psychological,Story Rich,Singleplayer"),
    ("Phasmophobia", "Kinetic Games", "Kinetic Games", "2020-09-18", "Horror", "M", 4.5,
     "A cooperative paranormal investigation game where players identify ghosts and gather evidence.",
     "Investigate haunted locations with equipment, collect evidence and identify the ghost type while managing risk.",
     "https://cdn.akamai.steamstatic.com/steam/apps/739630/header.jpg", "Horror,Co-op,Multiplayer,Investigation,Supernatural"),
    ("Hogwarts Legacy", "Avalanche Software", "Warner Bros. Games", "2023-02-10", "Action RPG", "T", 4.5,
     "An open-world action RPG set in the wizarding world of Hogwarts.",
     "Attend classes, explore the world, learn spells, customize equipment and complete quests.",
     "https://cdn.akamai.steamstatic.com/steam/apps/990080/header.jpg", "RPG,Open World,Fantasy,Magic,Story Rich,Singleplayer"),
    ("Terraria", "Re-Logic", "Re-Logic", "2011-05-16", "Sandbox", "T", 4.8,
     "A sandbox adventure focused on exploration, crafting, building and combat.",
     "Dig, gather resources, craft equipment, build structures, explore biomes and fight bosses.",
     "https://cdn.akamai.steamstatic.com/steam/apps/105600/header.jpg", "Sandbox,Adventure,Building,Survival,Indie,Multiplayer"),
    ("The Sims 4", "Maxis", "Electronic Arts", "2014-09-02", "Simulation", "T", 4.2,
     "A life simulation game where players create Sims, build homes and manage everyday lives.",
     "Create characters, build houses, choose careers, manage relationships and guide Sims through life.",
     "https://cdn.akamai.steamstatic.com/steam/apps/1222670/header.jpg", "Simulation,Life,Building,Character Customization,Free to Play"),
    ("Forza Horizon 5", "Playground Games", "Xbox Game Studios", "2021-11-09", "Racing", "E", 4.7,
     "An open-world racing game set across a fictionalized Mexico.",
     "Drive and customize cars, race across an open world, complete events and compete online.",
     "https://cdn.akamai.steamstatic.com/steam/apps/1551360/header.jpg", "Racing,Open World,Cars,Multiplayer,Driving"),
    ("Need for Speed Heat", "Ghost Games", "Electronic Arts", "2019-11-08", "Racing", "T", 4.3,
     "An arcade street-racing game set in Palm City with day and night events.",
     "Race during the day, earn reputation at night, customize cars and evade police pursuits.",
     "https://cdn.akamai.steamstatic.com/steam/apps/1222680/header.jpg", "Racing,Cars,Open World,Street Racing,Multiplayer"),
    ("EA SPORTS FC 26", "EA Canada", "Electronic Arts", "2025-09-26", "Sports", "E", 4.0,
     "A football simulation game featuring club and international football experiences.",
     "Play matches, manage teams, build squads and compete through multiple football modes.",
     "https://cdn.akamai.steamstatic.com/steam/apps/3405690/header.jpg", "Sports,Football,Simulation,Multiplayer,Competitive"),
    ("NBA 2K26", "Visual Concepts", "2K", "2025-09-05", "Sports", "E", 4.0,
     "A basketball simulation game featuring multiple competitive and career modes.",
     "Play basketball games, build a career, manage teams and compete online.",
     "https://cdn.akamai.steamstatic.com/steam/apps/3472040/header.jpg", "Sports,Basketball,Simulation,Multiplayer,Competitive"),
    ("Fortnite", "Epic Games", "Epic Games", "2017-07-25", "Battle Royale", "T", 4.3,
     "A free-to-play multiplayer game known for battle royale, building and evolving seasonal experiences.",
     "Drop into a match, collect equipment, build or use cover and outlast opponents or complete objectives.",
     "https://image.api.playstation.com/vulcan/ap/rnd/202608/2000/7128bc29987d227134423f25aa988d46c995cfa599cd9880.jpg", "Battle Royale,Multiplayer,Free to Play,Action,Building"),
    ("Warframe", "Digital Extremes", "Digital Extremes", "2013-03-25", "Action RPG", "M", 4.4,
     "A free-to-play cooperative action RPG centered on spacefaring warriors called Warframes.",
     "Complete missions, customize Warframes and weapons, collect resources and cooperate with other players.",
     "https://cdn.akamai.steamstatic.com/steam/apps/230410/header.jpg", "Action RPG,Co-op,Free to Play,Multiplayer,Third Person"),
]

EXTRA_PLATFORMS = {
    "Cyberpunk 2077":["PC","PlayStation 5","Xbox Series X|S"],
    "Baldur's Gate 3":["PC","PlayStation 5","Xbox Series X|S"],
    "The Witcher 3: Wild Hunt":["PC","PlayStation 5","PlayStation 4","Xbox Series X|S","Xbox One","Nintendo Switch"],
    "The Elder Scrolls V: Skyrim Special Edition":["PC","PlayStation 5","PlayStation 4","Xbox Series X|S","Xbox One","Nintendo Switch"],
    "Counter-Strike 2":["PC"], "Apex Legends":["PC","PlayStation 5","PlayStation 4","Xbox Series X|S","Xbox One","Nintendo Switch"],
    "DOOM Eternal":["PC","PlayStation 5","PlayStation 4","Xbox Series X|S","Xbox One","Nintendo Switch"],
    "God of War":["PC","PlayStation 5","PlayStation 4"], "Ghost of Tsushima":["PC","PlayStation 5","PlayStation 4"],
    "Devil May Cry 5":["PC","PlayStation 5","PlayStation 4","Xbox Series X|S","Xbox One"],
    "Resident Evil 4":["PC","PlayStation 5","PlayStation 4","Xbox Series X|S"], "Silent Hill 2":["PC","PlayStation 5"],
    "Phasmophobia":["PC","PlayStation 5","Xbox Series X|S"], "Hogwarts Legacy":["PC","PlayStation 5","PlayStation 4","Xbox Series X|S","Xbox One","Nintendo Switch"],
    "Terraria":["PC","PlayStation 5","PlayStation 4","Xbox Series X|S","Xbox One","Nintendo Switch","Android","iOS"],
    "The Sims 4":["PC","PlayStation 5","PlayStation 4","Xbox Series X|S","Xbox One"],
    "Forza Horizon 5":["PC","Xbox Series X|S","Xbox One"], "Need for Speed Heat":["PC","PlayStation 4","Xbox One"],
    "EA SPORTS FC 26":["PC","PlayStation 5","PlayStation 4","Xbox Series X|S","Xbox One","Nintendo Switch 2","Nintendo Switch"],
    "NBA 2K26":["PC","PlayStation 5","PlayStation 4","Xbox Series X|S","Xbox One","Nintendo Switch 2","Nintendo Switch"],
    "Fortnite":["PC","PlayStation 5","PlayStation 4","Xbox Series X|S","Xbox One","Nintendo Switch","Android"],
    "Warframe":["PC","PlayStation 5","PlayStation 4","Xbox Series X|S","Xbox One","Nintendo Switch"],
}

EXTRA_STORES = {
    "Cyberpunk 2077":[("Steam","https://store.steampowered.com/app/1091500/Cyberpunk_2077/","PC"),("GOG","https://www.gog.com/game/cyberpunk_2077","PC"),("PlayStation Store","https://store.playstation.com/","PlayStation"),("Xbox","https://www.xbox.com/","Xbox")],
    "Baldur's Gate 3":[("Steam","https://store.steampowered.com/app/1086940/Baldurs_Gate_3/","PC"),("GOG","https://www.gog.com/game/baldurs_gate_3","PC"),("PlayStation Store","https://store.playstation.com/","PlayStation"),("Xbox","https://www.xbox.com/","Xbox")],
    "The Witcher 3: Wild Hunt":[("Steam","https://store.steampowered.com/app/292030/The_Witcher_3_Wild_Hunt/","PC"),("GOG","https://www.gog.com/game/the_witcher_3_wild_hunt","PC")],
    "The Elder Scrolls V: Skyrim Special Edition":[("Steam","https://store.steampowered.com/app/489830/The_Elder_Scrolls_V_Skyrim_Special_Edition/","PC"),("Xbox","https://www.xbox.com/","Xbox"),("PlayStation Store","https://store.playstation.com/","PlayStation")],
    "Counter-Strike 2":[("Steam","https://store.steampowered.com/app/730/CounterStrike_2/","PC")],
    "Apex Legends":[("EA","https://www.ea.com/games/apex-legends","Official"),("Steam","https://store.steampowered.com/app/1172470/Apex_Legends/","PC")],
    "DOOM Eternal":[("Steam","https://store.steampowered.com/app/782330/DOOM_Eternal/","PC"),("Bethesda","https://bethesda.net/","Official")],
    "God of War":[("Steam","https://store.steampowered.com/app/1593500/God_of_War/","PC"),("PlayStation Store","https://store.playstation.com/","PlayStation")],
    "Ghost of Tsushima":[("Steam","https://store.steampowered.com/app/2215430/Ghost_of_Tsushima_DIRECTORS_CUT/","PC"),("PlayStation Store","https://store.playstation.com/","PlayStation")],
    "Devil May Cry 5":[("Steam","https://store.steampowered.com/app/601150/Devil_May_Cry_5/","PC")],
    "Resident Evil 4":[("Steam","https://store.steampowered.com/app/2050650/Resident_Evil_4/","PC"),("Capcom","https://www.residentevil.com/re4/","Official")],
    "Silent Hill 2":[("Steam","https://store.steampowered.com/app/2124490/SILENT_HILL_2/","PC"),("PlayStation Store","https://store.playstation.com/","PlayStation")],
    "Phasmophobia":[("Steam","https://store.steampowered.com/app/739630/Phasmophobia/","PC")],
    "Hogwarts Legacy":[("Steam","https://store.steampowered.com/app/990080/Hogwarts_Legacy/","PC"),("PlayStation Store","https://store.playstation.com/","PlayStation")],
    "Terraria":[("Steam","https://store.steampowered.com/app/105600/Terraria/","PC"),("GOG","https://www.gog.com/game/terraria","PC")],
    "The Sims 4":[("EA","https://www.ea.com/games/the-sims/the-sims-4","Official"),("Steam","https://store.steampowered.com/app/1222670/The_Sims_4/","PC")],
    "Forza Horizon 5":[("Steam","https://store.steampowered.com/app/1551360/Forza_Horizon_5/","PC"),("Xbox","https://www.xbox.com/","Xbox")],
    "Need for Speed Heat":[("EA","https://www.ea.com/games/need-for-speed/need-for-speed-heat","Official")],
    "EA SPORTS FC 26":[("EA","https://www.ea.com/games/ea-sports-fc/fc-26","Official")],
    "NBA 2K26":[("2K","https://nba.2k.com/","Official")],
    "Fortnite":[("Epic Games Store","https://store.epicgames.com/en-US/p/fortnite","PC"),("Epic Games","https://www.fortnite.com/","Official")],
    "Warframe":[("Steam","https://store.steampowered.com/app/230410/Warframe/","PC"),("Warframe","https://www.warframe.com/","Official")],
}

UI_TEXT = {
    "en": {"discover":"Discover", "admin":"Admin", "search":"Search games, developers, genres...", "featured":"Featured Games", "trending":"Trending Now", "top":"Top Rated", "free":"Free to Play", "browse":"Browse by Genre", "filters":"Filters", "reset":"Reset", "apply":"Apply Filters", "catalog":"Game Catalogue", "games":"Games", "details":"View Details", "about":"About the Game", "how":"How It Works", "platforms":"Platforms", "languages":"Languages", "where":"Where to Get It", "regional":"Regional Information", "price":"Regional Price", "developer":"Developer", "publisher":"Publisher", "release":"Release Date", "rating":"Rating", "age":"Age Rating", "tags":"Tags", "edit":"Edit Game", "back":"Back to games", "lang":"Language"},
    "hi": {"discover":"गेम खोजें", "admin":"एडमिन", "search":"गेम, डेवलपर या शैली खोजें...", "featured":"चुनिंदा गेम", "trending":"अभी लोकप्रिय", "top":"सर्वाधिक रेटेड", "free":"फ्री टू प्ले", "browse":"शैली के अनुसार खोजें", "filters":"फ़िल्टर", "reset":"रीसेट", "apply":"फ़िल्टर लागू करें", "catalog":"गेम कैटलॉग", "games":"गेम", "details":"विवरण देखें", "about":"गेम के बारे में", "how":"यह कैसे काम करता है", "platforms":"प्लेटफ़ॉर्म", "languages":"भाषाएँ", "where":"कहाँ से प्राप्त करें", "regional":"क्षेत्रीय जानकारी", "price":"क्षेत्रीय कीमत", "developer":"डेवलपर", "publisher":"प्रकाशक", "release":"रिलीज़ तारीख", "rating":"रेटिंग", "age":"उम्र रेटिंग", "tags":"टैग", "edit":"गेम संपादित करें", "back":"गेम पर वापस जाएँ", "lang":"भाषा"},
    "mr": {"discover":"गेम शोधा", "admin":"अॅडमिन", "search":"गेम, विकसक किंवा शैली शोधा...", "featured":"निवडक गेम", "trending":"सध्या लोकप्रिय", "top":"सर्वाधिक रेटेड", "free":"फ्री टू प्ले", "browse":"शैलीनुसार शोधा", "filters":"फिल्टर", "reset":"रीसेट", "apply":"फिल्टर लागू करा", "catalog":"गेम कॅटलॉग", "games":"गेम्स", "details":"तपशील पहा", "about":"गेमबद्दल", "how":"हे कसे कार्य करते", "platforms":"प्लॅटफॉर्म", "languages":"भाषा", "where":"कुठे मिळेल", "regional":"प्रादेशिक माहिती", "price":"प्रादेशिक किंमत", "developer":"विकसक", "publisher":"प्रकाशक", "release":"रिलीज तारीख", "rating":"रेटिंग", "age":"वय रेटिंग", "tags":"टॅग", "edit":"गेम संपादित करा", "back":"गेम्सकडे परत", "lang":"भाषा"}
}


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def ensure_column(conn, table, column, definition):
    columns = [r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()]
    if column not in columns:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")



def dedupe_games(conn):
    """Clean duplicates from older V6 builds before creating uniqueness constraints."""
    # First remove duplicate store rows. Older builds could insert the same
    # store repeatedly because stores(name,url) was not unique. Preserve the
    # lowest-id row and repoint any game_store relationships to it.
    dup_stores = conn.execute(
        "SELECT name, url FROM stores GROUP BY name, url HAVING COUNT(*) > 1"
    ).fetchall()
    for name, url in dup_stores:
        ids = [r[0] for r in conn.execute(
            "SELECT id FROM stores WHERE name=? AND url=? ORDER BY id", (name, url)
        ).fetchall()]
        keep = ids[0]
        for sid in ids[1:]:
            # Move relationships to the retained store. INSERT OR IGNORE
            # handles cases where the game is already linked to the keeper.
            conn.execute(
                "INSERT OR IGNORE INTO game_stores(game_id, store_id) "
                "SELECT game_id, ? FROM game_stores WHERE store_id=?",
                (keep, sid)
            )
            conn.execute("DELETE FROM game_stores WHERE store_id=?", (sid,))
            conn.execute("DELETE FROM stores WHERE id=?", (sid,))

    # Remove duplicate game rows created by older V6 builds and keep the first
    # row per name. Relationships on duplicate games are discarded because the
    # retained row is reseeded/repaired below.
    dup_names = [r[0] for r in conn.execute(
        "SELECT name FROM games GROUP BY name HAVING COUNT(*) > 1"
    ).fetchall()]
    for name in dup_names:
        ids = [r[0] for r in conn.execute(
            "SELECT id FROM games WHERE name=? ORDER BY id", (name,)
        ).fetchall()]
        for gid in ids[1:]:
            for table in ("game_platforms", "game_languages", "prices", "game_stores"):
                conn.execute(f"DELETE FROM {table} WHERE game_id=?", (gid,))
            conn.execute("DELETE FROM games WHERE id=?", (gid,))

    # Only create the indexes after the duplicate rows have been cleaned.
    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_games_name_unique ON games(name)")
    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_stores_name_url_unique ON stores(name,url)")


def ensure_extra_catalog(conn):
    for g in EXTRA_GAMES:
        conn.execute("""INSERT OR IGNORE INTO games
            (name,developer,publisher,release_date,genre,age_rating,rating,summary,how_it_works,image_url,tags)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)""", g)
    for name, plist in EXTRA_PLATFORMS.items():
        row = conn.execute("SELECT id FROM games WHERE name=?", (name,)).fetchone()
        if not row: continue
        gid=row[0]
        for pname in plist:
            conn.execute("INSERT OR IGNORE INTO platforms(name) VALUES (?)", (pname,))
            pid=conn.execute("SELECT id FROM platforms WHERE name=?", (pname,)).fetchone()[0]
            conn.execute("INSERT OR IGNORE INTO game_platforms VALUES (?,?)", (gid,pid))
    # Give every extra game a useful language set.
    for name, *_ in EXTRA_GAMES:
        gid=conn.execute("SELECT id FROM games WHERE name=?", (name,)).fetchone()[0]
        for lang in ["English","French","German","Spanish","Japanese"]:
            conn.execute("INSERT OR IGNORE INTO languages(name) VALUES (?)", (lang,))
            lid=conn.execute("SELECT id FROM languages WHERE name=?", (lang,)).fetchone()[0]
            conn.execute("INSERT OR IGNORE INTO game_languages VALUES (?,?)", (gid,lid))
    # Sample regional pricing, explicitly demo/admin-maintained.
    free_names={"Counter-Strike 2","Apex Legends","Fortnite","Warframe","The Sims 4"}
    for name,*_ in EXTRA_GAMES:
        gid=conn.execute("SELECT id FROM games WHERE name=?", (name,)).fetchone()[0]
        for country,price in [("India",0 if name in free_names else 1499),("United States",0 if name in free_names else 39.99),("United Kingdom",0 if name in free_names else 34.99),("Japan",0 if name in free_names else 5980)]:
            cid=conn.execute("SELECT id FROM countries WHERE name=?", (country,)).fetchone()[0]
            conn.execute("INSERT OR IGNORE INTO prices VALUES (?,?,?,?)", (gid,cid,"Free" if name in free_names else "Paid",price))
    for game_name, stores in EXTRA_STORES.items():
        gid=conn.execute("SELECT id FROM games WHERE name=?", (game_name,)).fetchone()[0]
        for store_name,url,platform in stores:
            conn.execute("INSERT OR IGNORE INTO stores(name,url,platform) VALUES (?,?,?)", (store_name,url,platform))
            sid=conn.execute("SELECT id FROM stores WHERE name=? AND url=?", (store_name,url)).fetchone()[0]
            conn.execute("INSERT OR IGNORE INTO game_stores VALUES (?,?)", (gid,sid))

def init_db():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = get_db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS games (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        developer TEXT NOT NULL,
        publisher TEXT NOT NULL,
        release_date TEXT NOT NULL,
        genre TEXT NOT NULL,
        age_rating TEXT NOT NULL,
        rating REAL NOT NULL,
        summary TEXT NOT NULL,
        how_it_works TEXT NOT NULL,
        image_url TEXT,
        tags TEXT NOT NULL DEFAULT ''
    );

    CREATE TABLE IF NOT EXISTS platforms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    );

    CREATE TABLE IF NOT EXISTS game_platforms (
        game_id INTEGER NOT NULL,
        platform_id INTEGER NOT NULL,
        PRIMARY KEY (game_id, platform_id),
        FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE,
        FOREIGN KEY (platform_id) REFERENCES platforms(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS countries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        currency TEXT NOT NULL,
        symbol TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS prices (
        game_id INTEGER NOT NULL,
        country_id INTEGER NOT NULL,
        pricing_type TEXT NOT NULL CHECK(pricing_type IN ('Free', 'Paid')),
        price REAL DEFAULT 0,
        PRIMARY KEY (game_id, country_id),
        FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE,
        FOREIGN KEY (country_id) REFERENCES countries(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS languages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    );

    CREATE TABLE IF NOT EXISTS game_languages (
        game_id INTEGER NOT NULL,
        language_id INTEGER NOT NULL,
        PRIMARY KEY (game_id, language_id),
        FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE,
        FOREIGN KEY (language_id) REFERENCES languages(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS stores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        url TEXT NOT NULL,
        platform TEXT NOT NULL DEFAULT ''
    );

    CREATE TABLE IF NOT EXISTS game_stores (
        game_id INTEGER NOT NULL,
        store_id INTEGER NOT NULL,
        PRIMARY KEY (game_id, store_id),
        FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE,
        FOREIGN KEY (store_id) REFERENCES stores(id) ON DELETE CASCADE
    );
    """)

    # V4 migration: add tags to a V2/V3 database without destroying existing data.
    ensure_column(conn, "games", "tags", "TEXT NOT NULL DEFAULT ''")

    if conn.execute("SELECT COUNT(*) FROM games").fetchone()[0] == 0:
        seed_data(conn)
    else:
        # Keep existing records, but give the original demo games their V4 tags.
        for name, tags in GAME_TAGS.items():
            conn.execute("UPDATE games SET tags=? WHERE name=? AND (tags IS NULL OR tags='')", (tags, name))

        # If V3/V2 is copied forward, replace only the old placeholder/known URLs.
        for name, image_url in REAL_IMAGES.items():
            row = conn.execute("SELECT image_url FROM games WHERE name=?", (name,)).fetchone()
            current = row[0] if row else ""
            if row and (not current or "unsplash.com" in current):
                conn.execute("UPDATE games SET image_url=? WHERE name=?", (image_url, name))

        for game_name, stores in STORE_DATA.items():
            row = conn.execute("SELECT id FROM games WHERE name=?", (game_name,)).fetchone()
            if row:
                gid = row[0]
                for store_name, url, platform_name in stores:
                    conn.execute("INSERT OR IGNORE INTO stores(name,url,platform) VALUES (?,?,?)", (store_name, url, platform_name))
                    sid = conn.execute("SELECT id FROM stores WHERE name=? AND url=?", (store_name, url)).fetchone()[0]
                    conn.execute("INSERT OR IGNORE INTO game_stores VALUES (?,?)", (gid, sid))

    dedupe_games(conn)
    ensure_extra_catalog(conn)
    conn.commit()
    conn.close()


def seed_data(conn):
    platforms = ["PC", "PlayStation 5", "PlayStation 4", "Xbox Series X|S",
                 "Xbox One", "Xbox 360", "Wii U", "Nintendo Switch", "Android", "iOS", "PlayStation 3"]
    countries = [
        ("India", "INR", "₹"),
        ("United States", "USD", "$"),
        ("United Kingdom", "GBP", "£"),
        ("Japan", "JPY", "¥")
    ]
    languages = ["English", "Hindi", "Japanese", "French", "German", "Spanish", "Italian"]

    for p in platforms:
        conn.execute("INSERT OR IGNORE INTO platforms(name) VALUES (?)", (p,))
    for c in countries:
        conn.execute("INSERT OR IGNORE INTO countries(name,currency,symbol) VALUES (?,?,?)", c)
    for lang in languages:
        conn.execute("INSERT OR IGNORE INTO languages(name) VALUES (?)", (lang,))

    games = [
        ("Minecraft", "Mojang Studios", "Mojang", "2011-11-18", "Sandbox", "E10+", 4.8,
         "A sandbox game where players explore, collect resources, craft items and build structures in a procedurally generated world.",
         "Players explore the world, gather resources, craft tools and items, build structures and can play in survival or creative modes.", REAL_IMAGES["Minecraft"], GAME_TAGS["Minecraft"]),
        ("Grand Theft Auto V", "Rockstar North", "Rockstar Games", "2013-09-17", "Action-Adventure", "M", 4.6,
         "An open-world action-adventure game set in the fictional state of San Andreas.",
         "Players explore an open world, complete missions, interact with characters and use vehicles and equipment.", REAL_IMAGES["Grand Theft Auto V"], GAME_TAGS["Grand Theft Auto V"]),
        ("Elden Ring", "FromSoftware", "Bandai Namco Entertainment", "2022-02-25", "Action RPG", "M", 4.7,
         "An action role-playing game set in a large fantasy world filled with exploration, combat and challenging enemies.",
         "Players explore an interconnected world, develop a character, collect equipment and fight enemies using different combat styles.", REAL_IMAGES["Elden Ring"], GAME_TAGS["Elden Ring"]),
        ("Valorant", "Riot Games", "Riot Games", "2020-06-02", "FPS", "T", 4.5,
         "A competitive tactical first-person shooter combining precise gunplay with character abilities.",
         "Teams compete in objective-based rounds where players use weapons and unique agent abilities.", REAL_IMAGES["Valorant"], GAME_TAGS["Valorant"]),
        ("Red Dead Redemption 2", "Rockstar Studios", "Rockstar Games", "2018-10-26", "Action-Adventure", "M", 4.9,
         "An open-world western adventure following Arthur Morgan and the Van der Linde gang.",
         "Players explore a large world, complete story and side missions, interact with characters and manage equipment and resources.", REAL_IMAGES["Red Dead Redemption 2"], GAME_TAGS["Red Dead Redemption 2"]),
        ("Stardew Valley", "ConcernedApe", "ConcernedApe", "2016-02-26", "Simulation RPG", "E10+", 4.7,
         "A farming and life simulation game where players build a new life in a small rural community.",
         "Players farm crops, raise animals, explore areas, meet characters and develop their farm and relationships.", REAL_IMAGES["Stardew Valley"], GAME_TAGS["Stardew Valley"]),
        ("Batman: Arkham Asylum", "Rocksteady Studios", "Warner Bros. Interactive Entertainment", "2009-08-25", "Action-Adventure", "T", 4.6,
         "A dark, atmospheric Batman adventure set inside the infamous Arkham Asylum, where the Joker and other villains have taken control.",
         "Players use Batman's gadgets, stealth, combat and detective abilities to explore the asylum, solve puzzles and confront villains.", REAL_IMAGES["Batman: Arkham Asylum"], GAME_TAGS["Batman: Arkham Asylum"]),
        ("Batman: Arkham City", "Rocksteady Studios", "Warner Bros. Interactive Entertainment", "2011-10-18", "Action-Adventure", "T", 4.7,
         "A Batman action-adventure set in the sprawling fortified district known as Arkham City.",
         "Players glide across Gotham, investigate crimes, fight enemies, use gadgets and complete story and side missions.", REAL_IMAGES["Batman: Arkham City"], GAME_TAGS["Batman: Arkham City"]),
        ("Batman: Arkham Origins", "WB Games Montréal", "Warner Bros. Interactive Entertainment", "2013-10-25", "Action-Adventure", "T", 4.4,
         "A prequel featuring a younger Batman during an early chapter of his career as Gotham's crime fighter.",
         "Players investigate Gotham, fight assassins and criminals, use gadgets and develop Batman's abilities through the story.", REAL_IMAGES["Batman: Arkham Origins"], GAME_TAGS["Batman: Arkham Origins"]),
        ("Batman: Arkham Knight", "Rocksteady Studios", "Warner Bros. Interactive Entertainment", "2015-06-23", "Action-Adventure", "M", 4.6,
         "The finale of Rocksteady's Arkham trilogy, featuring a fully realized Gotham City and the Batmobile.",
         "Players explore Gotham, use Batman's gadgets and combat skills, investigate threats and drive the Batmobile through the city.", REAL_IMAGES["Batman: Arkham Knight"], GAME_TAGS["Batman: Arkham Knight"]),
    ]

    for g in games:
        conn.execute("""
            INSERT OR IGNORE INTO games
            (name,developer,publisher,release_date,genre,age_rating,rating,summary,how_it_works,image_url,tags)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, g)

    platform_map = {
        "Minecraft": ["PC", "PlayStation 5", "Xbox Series X|S", "Nintendo Switch", "Android", "iOS"],
        "Grand Theft Auto V": ["PC", "PlayStation 5", "PlayStation 4", "Xbox Series X|S", "Xbox One"],
        "Elden Ring": ["PC", "PlayStation 5", "PlayStation 4", "Xbox Series X|S"],
        "Valorant": ["PC"],
        "Red Dead Redemption 2": ["PC", "PlayStation 4", "Xbox One"],
        "Stardew Valley": ["PC", "PlayStation 5", "PlayStation 4", "Xbox Series X|S", "Nintendo Switch", "Android", "iOS"],
        "Batman: Arkham Asylum": ["PC", "PlayStation 3", "PlayStation 4", "Xbox 360", "Xbox One", "Nintendo Switch"],
        "Batman: Arkham City": ["PC", "PlayStation 3", "PlayStation 4", "Xbox 360", "Xbox One", "Wii U", "Nintendo Switch"],
        "Batman: Arkham Origins": ["PC", "PlayStation 3", "Xbox 360", "Wii U"],
        "Batman: Arkham Knight": ["PC", "PlayStation 4", "Xbox One"]
    }
    language_map = {
        "Minecraft": ["English", "French", "German", "Spanish", "Japanese"],
        "Grand Theft Auto V": ["English", "French", "German", "Spanish", "Japanese"],
        "Elden Ring": ["English", "French", "German", "Spanish", "Japanese"],
        "Valorant": ["English", "Hindi", "Japanese", "French", "German"],
        "Red Dead Redemption 2": ["English", "French", "German", "Spanish", "Japanese"],
        "Stardew Valley": ["English", "French", "German", "Spanish", "Japanese"],
        "Batman: Arkham Asylum": ["English", "French", "German", "Spanish", "Italian"],
        "Batman: Arkham City": ["English", "French", "German", "Spanish", "Italian"],
        "Batman: Arkham Origins": ["English", "French", "German", "Spanish", "Italian"],
        "Batman: Arkham Knight": ["English", "French", "German", "Spanish", "Italian"]
    }
    price_map = {
        "Minecraft": {"India": ("Paid", 1999), "United States": ("Paid", 29.99), "United Kingdom": ("Paid", 24.99), "Japan": ("Paid", 3960)},
        "Grand Theft Auto V": {"India": ("Paid", 1499), "United States": ("Paid", 29.99), "United Kingdom": ("Paid", 24.99), "Japan": ("Paid", 3300)},
        "Elden Ring": {"India": ("Paid", 3599), "United States": ("Paid", 59.99), "United Kingdom": ("Paid", 49.99), "Japan": ("Paid", 9240)},
        "Valorant": {"India": ("Free", 0), "United States": ("Free", 0), "United Kingdom": ("Free", 0), "Japan": ("Free", 0)},
        "Red Dead Redemption 2": {"India": ("Paid", 1999), "United States": ("Paid", 59.99), "United Kingdom": ("Paid", 49.99), "Japan": ("Paid", 8800)},
        "Stardew Valley": {"India": ("Paid", 499), "United States": ("Paid", 14.99), "United Kingdom": ("Paid", 11.99), "Japan": ("Paid", 1480)},
        "Batman: Arkham Asylum": {"India": ("Paid", 999), "United States": ("Paid", 19.99), "United Kingdom": ("Paid", 15.99), "Japan": ("Paid", 1980)},
        "Batman: Arkham City": {"India": ("Paid", 999), "United States": ("Paid", 19.99), "United Kingdom": ("Paid", 15.99), "Japan": ("Paid", 1980)},
        "Batman: Arkham Origins": {"India": ("Paid", 999), "United States": ("Paid", 19.99), "United Kingdom": ("Paid", 15.99), "Japan": ("Paid", 1980)},
        "Batman: Arkham Knight": {"India": ("Paid", 1499), "United States": ("Paid", 19.99), "United Kingdom": ("Paid", 15.99), "Japan": ("Paid", 1980)}
    }

    for name, plist in platform_map.items():
        gid = conn.execute("SELECT id FROM games WHERE name=?", (name,)).fetchone()[0]
        for p in plist:
            conn.execute("INSERT OR IGNORE INTO platforms(name) VALUES (?)", (p,))
            pid = conn.execute("SELECT id FROM platforms WHERE name=?", (p,)).fetchone()[0]
            conn.execute("INSERT OR IGNORE INTO game_platforms VALUES (?,?)", (gid, pid))

    for name, llist in language_map.items():
        gid = conn.execute("SELECT id FROM games WHERE name=?", (name,)).fetchone()[0]
        for lang in llist:
            lid = conn.execute("SELECT id FROM languages WHERE name=?", (lang,)).fetchone()[0]
            conn.execute("INSERT OR IGNORE INTO game_languages VALUES (?,?)", (gid, lid))

    for name, country_prices in price_map.items():
        gid = conn.execute("SELECT id FROM games WHERE name=?", (name,)).fetchone()[0]
        for country, (ptype, price) in country_prices.items():
            cid = conn.execute("SELECT id FROM countries WHERE name=?", (country,)).fetchone()[0]
            conn.execute("INSERT OR IGNORE INTO prices VALUES (?,?,?,?)", (gid, cid, ptype, price))

    for game_name, stores in STORE_DATA.items():
        gid = conn.execute("SELECT id FROM games WHERE name=?", (game_name,)).fetchone()[0]
        for store_name, url, platform_name in stores:
            conn.execute("INSERT OR IGNORE INTO stores(name,url,platform) VALUES (?,?,?)", (store_name, url, platform_name))
            sid = conn.execute("SELECT id FROM stores WHERE name=? AND url=?", (store_name, url)).fetchone()[0]
            conn.execute("INSERT OR IGNORE INTO game_stores VALUES (?,?)", (gid, sid))

    for game_name, stores in ARKHAM_STORE_DATA.items():
        gid = conn.execute("SELECT id FROM games WHERE name=?", (game_name,)).fetchone()[0]
        for store_name, url, platform_name in stores:
            conn.execute("INSERT OR IGNORE INTO stores(name,url,platform) VALUES (?,?,?)", (store_name, url, platform_name))
            sid = conn.execute("SELECT id FROM stores WHERE name=? AND url=?", (store_name, url)).fetchone()[0]
            conn.execute("INSERT OR IGNORE INTO game_stores VALUES (?,?)", (gid, sid))





def ensure_arkham_games(conn):
    # Kept for backward compatibility with older imports; catalog migration is handled by ensure_extra_catalog.
    return


@app.context_processor
def inject_ui():
    lang = session.get("lang", "en")
    if lang not in UI_TEXT:
        lang = "en"
    return {"ui": UI_TEXT[lang], "current_lang": lang}


@app.route("/set-language/<lang>")
def set_language(lang):
    if lang in UI_TEXT:
        session["lang"] = lang
    return redirect(request.referrer or url_for("index"))

@app.route("/")
def index():
    q = request.args.get("q", "").strip()
    genre = request.args.get("genre", "").strip()
    platform = request.args.get("platform", "").strip()
    tag = request.args.get("tag", "").strip()
    price_type = request.args.get("price", "").strip()
    country = request.args.get("country", "India").strip()
    sort = request.args.get("sort", "name").strip()

    conn = get_db()
    where = ["1=1"]
    params = []

    if q:
        like = f"%{q}%"
        where.append("(g.name LIKE ? OR g.developer LIKE ? OR g.publisher LIKE ? OR g.genre LIKE ? OR g.tags LIKE ? OR g.summary LIKE ?)")
        params += [like, like, like, like, like, like]
    if genre:
        where.append("g.genre = ?")
        params.append(genre)
    if platform:
        where.append("EXISTS (SELECT 1 FROM game_platforms gp JOIN platforms p ON p.id=gp.platform_id WHERE gp.game_id=g.id AND p.name=?)")
        params.append(platform)
    if tag:
        where.append("(',' || lower(g.tags) || ',') LIKE ?")
        params.append(f"%,{tag.lower()},%")
    if price_type:
        where.append("EXISTS (SELECT 1 FROM prices pr JOIN countries c ON c.id=pr.country_id WHERE pr.game_id=g.id AND c.name=? AND pr.pricing_type=?)")
        params += [country, price_type]

    order_map = {
        "name": "g.name COLLATE NOCASE ASC",
        "name_desc": "g.name COLLATE NOCASE DESC",
        "rating": "g.rating DESC, g.name COLLATE NOCASE ASC",
        "rating_low": "g.rating ASC, g.name COLLATE NOCASE ASC",
        "newest": "g.release_date DESC",
        "oldest": "g.release_date ASC",
    }
    if sort in ("price_low", "price_high"):
        direction = "ASC" if sort == "price_low" else "DESC"
        order_sql = f"COALESCE((SELECT pr.price FROM prices pr JOIN countries c2 ON c2.id=pr.country_id WHERE pr.game_id=g.id AND c2.name=?), 999999) {direction}, g.name COLLATE NOCASE ASC"
        price_order_params = [country]
    else:
        order_sql = order_map.get(sort, order_map["name"])
        price_order_params = []

    sql = f"""
        SELECT g.*, pr.pricing_type, pr.price AS regional_price, c.symbol AS currency_symbol
        FROM games g
        LEFT JOIN countries c ON c.name=?
        LEFT JOIN prices pr ON pr.game_id=g.id AND pr.country_id=c.id
        WHERE {' AND '.join(where)}
        ORDER BY {order_sql}
    """
    games = conn.execute(sql, [country] + params + price_order_params).fetchall()

    genres = conn.execute("SELECT DISTINCT genre FROM games ORDER BY genre").fetchall()
    platforms = conn.execute("SELECT name FROM platforms ORDER BY name").fetchall()
    countries = conn.execute("SELECT * FROM countries ORDER BY name").fetchall()
    tag_rows = conn.execute("SELECT tags FROM games WHERE tags <> ''").fetchall()
    tags = sorted({t.strip() for row in tag_rows for t in row[0].split(',') if t.strip()}, key=str.lower)
    total_games = conn.execute("SELECT COUNT(*) FROM games").fetchone()[0]
    featured = conn.execute("SELECT * FROM games ORDER BY rating DESC, release_date DESC LIMIT 3").fetchall()
    free_games = conn.execute("SELECT g.* FROM games g JOIN prices pr ON pr.game_id=g.id JOIN countries c ON c.id=pr.country_id WHERE c.name=? AND pr.pricing_type='Free' ORDER BY g.rating DESC LIMIT 3", (country,)).fetchall()
    trending = conn.execute("SELECT * FROM games ORDER BY release_date DESC, rating DESC LIMIT 3").fetchall()
    conn.close()

    dashboard_stats = {
        "games": total_games,
        "genres": len(genres),
        "platforms": len(platforms),
        "countries": len(countries),
    }
    return render_template(
        "index.html", games=games, genres=genres, platforms=platforms,
        countries=countries, tags=tags, q=q, selected_genre=genre,
        selected_platform=platform, selected_tag=tag, selected_price=price_type,
        selected_country=country, selected_sort=sort, total_games=total_games,
        featured=featured, free_games=free_games, trending=trending, dashboard_stats=dashboard_stats,
        has_filters=any([q, genre, platform, tag, price_type]) or sort != "name"
    )


@app.route("/game/<int:game_id>")
def game_detail(game_id):
    country_name = request.args.get("country", "India")
    conn = get_db()
    game = conn.execute("SELECT * FROM games WHERE id=?", (game_id,)).fetchone()
    if not game:
        conn.close()
        return "Game not found", 404

    platforms = conn.execute("""
        SELECT p.name FROM platforms p JOIN game_platforms gp ON p.id=gp.platform_id
        WHERE gp.game_id=? ORDER BY p.name
    """, (game_id,)).fetchall()
    languages = conn.execute("""
        SELECT l.name FROM languages l JOIN game_languages gl ON l.id=gl.language_id
        WHERE gl.game_id=? ORDER BY l.name
    """, (game_id,)).fetchall()
    tags = [t.strip() for t in (game["tags"] or "").split(",") if t.strip()]
    stores = conn.execute("SELECT s.* FROM stores s JOIN game_stores gs ON s.id=gs.store_id WHERE gs.game_id=? ORDER BY s.name", (game_id,)).fetchall()
    countries = conn.execute("SELECT * FROM countries ORDER BY name").fetchall()
    pricing = conn.execute("""
        SELECT pr.*, c.name country_name, c.currency, c.symbol
        FROM prices pr JOIN countries c ON c.id=pr.country_id
        WHERE pr.game_id=? AND c.name=?
    """, (game_id, country_name)).fetchone()
    conn.close()
    return render_template("game.html", game=game, platforms=platforms, languages=languages,
                           tags=tags, stores=stores, countries=countries, pricing=pricing, selected_country=country_name)


@app.route("/admin")
def admin():
    q = request.args.get("q", "").strip()
    conn = get_db()
    if q:
        like = f"%{q}%"
        games = conn.execute("SELECT * FROM games WHERE name LIKE ? OR developer LIKE ? OR genre LIKE ? ORDER BY name", (like, like, like)).fetchall()
    else:
        games = conn.execute("SELECT * FROM games ORDER BY name").fetchall()
    stats = {
        "games": conn.execute("SELECT COUNT(*) FROM games").fetchone()[0],
        "genres": conn.execute("SELECT COUNT(DISTINCT genre) FROM games").fetchone()[0],
        "platforms": conn.execute("SELECT COUNT(*) FROM platforms").fetchone()[0],
        "stores": conn.execute("SELECT COUNT(*) FROM stores").fetchone()[0],
        "countries": conn.execute("SELECT COUNT(*) FROM countries").fetchone()[0],
        "languages": conn.execute("SELECT COUNT(*) FROM languages").fetchone()[0],
        "free": conn.execute("SELECT COUNT(DISTINCT game_id) FROM prices WHERE pricing_type='Free'").fetchone()[0],
    }
    conn.close()
    return render_template("admin.html", games=games, stats=stats, q=q)


def clean_csv(value):
    return [x.strip() for x in (value or '').split(',') if x.strip()]


def valid_http_url(value):
    if not value:
        return True
    try:
        parsed = urlparse(value)
        return parsed.scheme in ('http', 'https') and bool(parsed.netloc)
    except Exception:
        return False


def save_relationships(conn, game_id, data):
    # Platforms
    conn.execute("DELETE FROM game_platforms WHERE game_id=?", (game_id,))
    for platform in clean_csv(data.get("platforms", "")):
        conn.execute("INSERT OR IGNORE INTO platforms(name) VALUES (?)", (platform,))
        pid = conn.execute("SELECT id FROM platforms WHERE name=?", (platform,)).fetchone()[0]
        conn.execute("INSERT OR IGNORE INTO game_platforms VALUES (?,?)", (game_id, pid))

    # Languages
    conn.execute("DELETE FROM game_languages WHERE game_id=?", (game_id,))
    for language in clean_csv(data.get("languages", "")):
        conn.execute("INSERT OR IGNORE INTO languages(name) VALUES (?)", (language,))
        lid = conn.execute("SELECT id FROM languages WHERE name=?", (language,)).fetchone()[0]
        conn.execute("INSERT OR IGNORE INTO game_languages VALUES (?,?)", (game_id, lid))

    # Stores: one per line: Store Name | URL | Platform
    conn.execute("DELETE FROM game_stores WHERE game_id=?", (game_id,))
    raw = data.get("stores", "")
    for item in raw.split("\n"):
        item = item.strip()
        if not item or "|" not in item:
            continue
        parts = [x.strip() for x in item.split("|", 2)]
        if len(parts) != 3 or not parts[0] or not parts[1]:
            continue
        store_name, url, platform_name = parts
        if not valid_http_url(url):
            raise ValueError(f"Invalid store URL: {url}")
        conn.execute("INSERT OR IGNORE INTO stores(name,url,platform) VALUES (?,?,?)", (store_name, url, platform_name))
        sid = conn.execute("SELECT id FROM stores WHERE name=? AND url=?", (store_name, url)).fetchone()[0]
        conn.execute("INSERT OR IGNORE INTO game_stores VALUES (?,?)", (game_id, sid))

    # Regional prices: one per line: Country | Free/Paid | amount
    raw_prices = data.get("prices", "")
    conn.execute("DELETE FROM prices WHERE game_id=?", (game_id,))
    for item in raw_prices.split("\n"):
        item = item.strip()
        if not item or "|" not in item:
            continue
        parts = [x.strip() for x in item.split("|", 2)]
        if len(parts) != 3:
            continue
        country_name, pricing_type, amount = parts
        if pricing_type not in ("Free", "Paid"):
            raise ValueError("Pricing type must be Free or Paid.")
        try:
            price = 0.0 if pricing_type == "Free" else float(amount)
        except ValueError:
            raise ValueError(f"Invalid price for {country_name}.")
        if price < 0:
            raise ValueError("Price cannot be negative.")
        country = conn.execute("SELECT id FROM countries WHERE name=?", (country_name,)).fetchone()
        if not country:
            raise ValueError(f"Unknown country: {country_name}")
        conn.execute("INSERT OR REPLACE INTO prices(game_id,country_id,pricing_type,price) VALUES (?,?,?,?)",
                     (game_id, country[0], pricing_type, price))


def validate_rating(value):
    try:
        rating = float(value)
    except (TypeError, ValueError):
        raise ValueError("Rating must be a number between 0 and 5.")
    if rating < 0 or rating > 5:
        raise ValueError("Rating must be between 0 and 5.")
    return rating


def validate_game_form(data):
    required = ["name", "developer", "publisher", "release_date", "genre", "age_rating", "rating", "summary", "how_it_works"]
    for field in required:
        if not data.get(field, "").strip():
            raise ValueError(f"{field.replace('_', ' ').title()} is required.")
    if not valid_http_url(data.get("image_url", "").strip()):
        raise ValueError("Image URL must be a valid http/https URL or left blank.")
    return validate_rating(data["rating"])


@app.route("/admin/add", methods=["GET", "POST"])
def add_game():
    if request.method == "POST":
        data = request.form
        conn = get_db()
        try:
            rating = validate_game_form(data)
            existing = conn.execute("SELECT id FROM games WHERE lower(name)=lower(?)", (data["name"].strip(),)).fetchone()
            if existing:
                raise ValueError("A game with this name already exists.")
            conn.execute("""
                INSERT INTO games
                (name,developer,publisher,release_date,genre,age_rating,rating,summary,how_it_works,image_url,tags)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)
            """, (data["name"].strip(), data["developer"].strip(), data["publisher"].strip(), data["release_date"],
                  data["genre"].strip(), data["age_rating"].strip(), rating, data["summary"].strip(), data["how_it_works"].strip(),
                  data.get("image_url", "").strip(), data.get("tags", "").strip()))
            game_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            save_relationships(conn, game_id, data)
            conn.commit()
            flash("Game added successfully.", "success")
            return redirect(url_for("admin"))
        except Exception as e:
            conn.rollback()
            flash(f"Could not add game: {e}", "error")
        finally:
            conn.close()
    conn = get_db()
    countries = conn.execute("SELECT * FROM countries ORDER BY name").fetchall()
    conn.close()
    return render_template("add_game.html", countries=countries)


@app.route("/admin/edit/<int:game_id>", methods=["GET", "POST"])
def edit_game(game_id):
    conn = get_db()
    game = conn.execute("SELECT * FROM games WHERE id=?", (game_id,)).fetchone()
    if not game:
        conn.close()
        return "Game not found", 404

    if request.method == "POST":
        data = request.form
        try:
            rating = validate_game_form(data)
            duplicate = conn.execute("SELECT id FROM games WHERE lower(name)=lower(?) AND id<>?", (data["name"].strip(), game_id)).fetchone()
            if duplicate:
                raise ValueError("Another game already uses this name.")
            conn.execute("""
                UPDATE games SET name=?, developer=?, publisher=?, release_date=?, genre=?,
                age_rating=?, rating=?, summary=?, how_it_works=?, image_url=?, tags=? WHERE id=?
            """, (data["name"].strip(), data["developer"].strip(), data["publisher"].strip(), data["release_date"],
                  data["genre"].strip(), data["age_rating"].strip(), rating, data["summary"].strip(), data["how_it_works"].strip(),
                  data.get("image_url", "").strip(), data.get("tags", "").strip(), game_id))
            save_relationships(conn, game_id, data)
            conn.commit()
            flash("Game updated successfully.", "success")
            return redirect(url_for("admin"))
        except Exception as e:
            conn.rollback()
            flash(f"Could not update game: {e}", "error")

    platforms = conn.execute("SELECT p.name FROM platforms p JOIN game_platforms gp ON p.id=gp.platform_id WHERE gp.game_id=? ORDER BY p.name", (game_id,)).fetchall()
    languages = conn.execute("SELECT l.name FROM languages l JOIN game_languages gl ON l.id=gl.language_id WHERE gl.game_id=? ORDER BY l.name", (game_id,)).fetchall()
    stores = conn.execute("SELECT s.* FROM stores s JOIN game_stores gs ON s.id=gs.store_id WHERE gs.game_id=? ORDER BY s.name", (game_id,)).fetchall()
    prices = conn.execute("SELECT pr.*, c.name country_name FROM prices pr JOIN countries c ON c.id=pr.country_id WHERE pr.game_id=? ORDER BY c.name", (game_id,)).fetchall()
    countries = conn.execute("SELECT * FROM countries ORDER BY name").fetchall()
    platform_text = ", ".join(p["name"] for p in platforms)
    language_text = ", ".join(x["name"] for x in languages)
    store_text = "\n".join(f"{x['name']} | {x['url']} | {x['platform']}" for x in stores)
    price_text = "\n".join(f"{x['country_name']} | {x['pricing_type']} | {x['price']}" for x in prices)
    conn.close()
    return render_template("edit_game.html", game=game, platform_text=platform_text, language_text=language_text,
                           store_text=store_text, price_text=price_text, countries=countries)


@app.route("/admin/delete/<int:game_id>", methods=["POST"])
def delete_game(game_id):
    conn = get_db()
    game = conn.execute("SELECT name FROM games WHERE id=?", (game_id,)).fetchone()
    if not game:
        conn.close()
        flash("Game not found.", "error")
        return redirect(url_for("admin"))
    # Explicit cleanup keeps the app safe even if an older DB has foreign keys disabled.
    for table in ("game_platforms", "game_languages", "prices", "game_stores"):
        conn.execute(f"DELETE FROM {table} WHERE game_id=?", (game_id,))
    conn.execute("DELETE FROM games WHERE id=?", (game_id,))
    conn.commit()
    conn.close()
    flash(f"{game['name']} deleted.", "success")
    return redirect(url_for("admin"))


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
