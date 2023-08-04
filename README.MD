# Introduction
This is a personal project whereby I attempt to dynamically visualize music with as little hand-crafting as possible. The idea is that I'm trying to build an entity I call a Musical Meta AI Construct (Metac, abbreviated). An entity of my own design.

The `DJ` class handles all audio related computations and runs concurrently in a separate process, so you can modify the frame rate without concern that the music will lag with respect to the visualization.

The `bolts.py` module handles all geometric inspired lightning bolts. The `polytopes.py` file handles all polytope generation. `utils.py` contains a number of generic classes that are useful for all metacs (though requires refactoring for the DJ class).

# Setup
Install python 3.10 and use which ever package manager you prefer. Refer to the `requirements.txt` for dependencies. Make sure to have the latest graphics drivers and ensure that OpenGL is accessible to you.

# Execution
I have yet to create an API to Spotify, Soundcloud or YouTube, so you will need to download your song of choice as a `.wav` file and store it in the `music` folder. You will also need to create a `music` folder in the root directory.

`draw_triangle.py` and `draw_rotating_triangle.py` are my first attempts at understanding the shader language, so they aren't particularly useful except for a couple code snippets. They are kept for reference.

The main files to look out for are the `lightwall.py` and `hex_bolt_metac.py` files. To execute them, modify the `filename` variable with your song of choice and run the following in console:
```shell
python lightwall.py
```

or

```shell
python hex_bolt_metac.py
```

# TODOS
## Hex Bolt Metac
Add hex grid and configure alphas to correspond to dampened bass.
