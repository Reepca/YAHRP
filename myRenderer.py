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


def render(obj, cameraStuff, environment):
    """obj - the object to render. This should probably be an instance of some
    class that we'll think up later, after we've already decided how we're
    going to use it. It'll have mesh data with references to
    materials/textures/etc, maybe some other stuff.

    cameraStuff - either a dictionary containing camera info (where the eye is,
    where we're looking at, what the field of view is, etc) or, again, some
    instance of a class we think up after we've decided how we're going to use
    it. Yay for top-down design. NAME MAY BE SUBJECT TO CHANGE.

    environment - right now I think this should mostly be lighting. I can't
    think of anything else at the moment, but if there's anything else that
    affects how the object is drawn that shouldn't be associated with the
    object itself, it should go here."""

    # Bind the vertex data to an openGL Vertex Buffer Object if it isn't
    # already bound. The GLint used to represent that Vertex Buffer Object
    # should be kept with the object (obj) itself.

    # we can set up shaders here, but it might be wasteful - the shaders
    # shouldn't need to be set up each time something is drawn. Perhaps things
    # like "currently active shader" and such should be kept in a class that
    # this is a method of?

    # So now we have the vertex data on the GPU and the program for drawing on
    # the GPU. But there's still some more necessary - the shader output
    # depends not only on the vertices themselves, but also on data that should
    # be shared across all of the running instances of the shader. This kind of
    # data is called a "uniform". Here we should send "uniform" information
    # about the camera and maybe lighting stuff to the GPU as well.

    # Make the vertex data the active buffer thing.

    # Run glDrawArrays(). This will use the implicit shader, the implicit
    # uniforms, and the implicit (it kind of bugs me how implicit everything is
    # in openGL) bound vertex buffer to do some drawing.

    # Is there anything we need to do to cleanup after rendering a single
    # object? I can't think of anything. Guess we're done at this point.
