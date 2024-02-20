# Storytelling App

This directory contains a simple web app (no dependencies) that acts as a virtual tabletop for a collaborative storytelling game.

## The Game

The rules of the game are as follows:

* Two participants get in front of the screen and are given a new set of hidden cards (back side up).
* The participants freely turn as many cards as they want. The cards show places, characters, and objects.
* The participants discuss together and choose 6 cards to use in a story.
* The participants then discuss together the details of the story.
* Finally, the participants retell the story to an audience.

## Controls

Cards can be revealed by pressing them. Pressing the ESC key shows or hides UI buttons. The button functionality can also be achieved by pressing one of the number keys in the keyboard:

* Pressing [1] or "Reveal All" reveals all cards (flips them to the picture side).
* Pressing [2] or "Shuffle" hides all cards and fetches new ones.
* Pressing [3] or "Shuffle and Reveal" combines the two previous actions: it hides the cards, fetches new ones, and then reveals all cards.

## Running Locally

You only need to serve the files in the directory! My favorite is running this command from this directory:

```sh
python -m http.server
```
