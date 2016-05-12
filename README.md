# YAHRP

Yet Another Hopeful Reepca Project - this one is an attempt to make a little
runescape-like game.

So far, the general idea looks like this:

Software is split into multiple-clients and single-server. Server and client
always run separately even if on the same system. The server provides
information about the game state and which actions are available to the
client. The client only needs to tell the server which action it will take -
this is basically a remote function call.

Communication should be done using the conspack protocol. The client is left
free to implement a lot of things - the user interface is completely up to it,
the rendering (if any) is completely up to it, even the assets are up to it,
although the server should provide a "canonical" representation of objects that
can be cached. It would be fun to see an interactive command-line version of
a client next to a full-blown openGL version.

I (Reepca) currently plan to work on the server, written in Common Lisp, while
Buzzlet works on the client, written in... whatever he feels like, I guess. If
you're reading this and aren't either of us, um... this is only public because
we're cheap, but if you feel like using our crappy code for whatever reason,
just check out the LICENSE file - it's GPLv3. And if for some reason you feel
like enhancing our crappy code and contributing it, I... I dunno, we'd cross
that bridge when we came to it.