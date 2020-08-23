# Musharna

A simple web app that finds what Twitter users around the world have recently been dreaming about, and displays it in a stream-like fashion.

# How it works

A **Flask** route calls the **Twitter API** to search for Tweets with dream-related keywords and adds them to a **Mongo Atlas** database. *Retweets, media tweets, links, and replies are excluded*. This route is run once per day using the **Heroku Scheduler**.

The app displays all dream-related Tweets from the day before. Each dream's text is animated using the the **typed.js** library, mimicking users typing up what they dreamed about.

## Initial Observations

- K-Pop stans
- "I dreamed about you"
- A lot of unique and interesting dreams, which is what I wanted to see!

## To Do List

- Once enough data is collected, a way to analyze the content of these dream-related Tweets (and maybe generate fake dream Tweets)
- Basic Tweet search functionality

##

![musharna picture](https://cdn.bulbagarden.net/upload/2/2d/518Musharna.png)

> Musharna, the Drowsing Pokémon and the evolved form of
> [Munna](https://bulbapedia.bulbagarden.net/wiki/Munna_(Pok%C3%A9mon)
> "Munna (Pokémon)"). The mist from its forehead takes the form of
> things present in the dreams it has eaten.
--Ash's Pokédex

