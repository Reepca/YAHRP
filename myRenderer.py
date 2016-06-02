# Author: Joel and Caleb

# Overview: this file is meant to copy the good parts of the daeviewer example
# and replace it with something that allows us to easily control the camera and
# other features. Also meant to use more modern openGL, 'cuz I have no idea
# what the author of daeview is doing mixing shader stuff with fixed-function
# pipeline stuff (glLightfv, for example).

# Assumptions this file should make: there is already an openGL context of at
# least v3.0 initialized - it's from 2008 for crying out loud, it's not too
# much to ask. It's not like it will stop people from at least developing -
# llvmpipe is a thing.

# What this code is responsible for: being handed a model to draw and some
# auxiliary information about how to draw it (lights, camera... action?) and
# JUST DOING IT. Because the screen real estate being drawn to is implicit
# (openGL's a state machine innit?), this really, really doesn't have to care
# about multiple windows or anything like that. Note: to reduce copying to the
# GPU (a slow operation), a caching system could be implemented whereby a model
# can be looked up in a dictionary associating models with identifiers for
# already-loaded openGL vertex array thingies.

# What this code is not responsible for: loading models, changing their
# properties, eating dogs, segfaulting, etc.


