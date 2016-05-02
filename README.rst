Proog - A Mail Server Framework
===============================

Proog is a toolkit for writing mail services.

Why?
----

Mail servers are notoriously difficult to configure. Postfix, for example, has
a handful of "maps" files all with slightly different syntax and it has well
over 500 configuration options giving the user fine grained control over every
aspect of the server. Exim is a similar story, except its configuration is
Turing complete. So I wanted to make mail server that was opinionated about how
it would work. My way or the highway.

On the other hand, neither of them really offer any sane way for me to
implement something like Inboxen. I like Salmon, but I still had to put Postfix
in front of it for various reasons.

This is where Proog comes in: a toolkit written in Python that will allow me to
create mail applications with a common base.

Status
------

I'm still thinking things through, so a lot of things are either broken or just
not implemented yet. File an issue if you have any questions!

Wait, what about Salmon?
------------------------

Salmon has a very limited scope, as well as a requirement to be *mostly*
backwards compatible with Lamson. It's been designed to sit behind another mail
server (like Postfix), which deals with all the tricky business of attempting
redelivery and filtering out bad clients.

Things I'd like to be able to with Proog that would be impossible with Salmon:

* Respond negatively to a client based on their ``MAIL FROM`` or ``RCPT TO``
  before they've had a chance to send ``DATA``
* Be publicly facing, with TLS support and authentication
* Implement all the necessary features to be a relay
