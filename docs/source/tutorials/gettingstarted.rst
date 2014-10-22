Getting Started
===============

In order to communicate with any federation resource using ``geni-lib`` you need to construct
a ``Context`` object that contains information about the framework you are using (for example
ProtoGENI, Emulab, GENI Clearinghouse, etc.), as well as your user information (SSH keys,
login username, federation urn, etc.).

* To start, we will create a new Python file called ``mycontext.py`` and import the necessary
  modules to start building our own context using your favorite editor::

   from geni.aggregate import FrameworkRegistry
   from geni.aggregate.context import Context
   from geni.aggregate.user import User


* Now we add a function that you will call each time you want to create your context (using the 
  GENI Clearinghouse as the default framework)::

   def buildContext ():
     portal = FrameworkRegistry.get("portal")()
  
.. note::
  The framework registry returns classes, not instances, so you need to call the framework
  object you retrieved from the registry in order to create an instance.

* You need to give the framework instance the location of your user certificate and key files::

     portal.cert = "/home/user/.ssh/portal-user.pem"
     portal.key = "/home/user/.ssh/portal-user.key"

.. note::
  You may only have one file which contains both items - you can use the same path for both
  variables if this is the case.

* With your Framework now properly configured, we need to create an object representing yourself as
  a federation user::

     user = User()
     user.name = "myusername"
     user.urn = "urn:publicid:IDN+ch.geni.net+user+myusername"
     user.addKey("/home/user/.ssh/geni_dsa.pub")

  We create a ``User()`` object, give it a name (no spaces, commonly a username), and your credential
  user URN.  We then add an SSH public key that will be installed on any compute resources that you reserve
  in order for you to authenticate with those resources.

* Next we make the parent ``Context`` object and add our user and framework to it, with a default project::

     context = Context()
     context.addUser(user, default = True)
     context.cf = portal
     context.project = "GEC21"

  This adds the user we created above, sets the control framework (``cf``), and sets your default project.

* You now want to return this object so that you can use this function every time you need a context::

     return context

Now to see the complete code in one block::

   from geni.aggregate import FrameworkRegistry
   from geni.aggregate.context import Context
   from geni.aggregate.user import User

   def buildContext ():
     portal = FrameworkRegistry.get("portal")()
     portal.cert = "/home/user/.ssh/portal-user.pem"
     portal.key = "/home/user/.ssh/portal-user.key"

     user = User()
     user.name = "myusername"
     user.urn = "urn:publicid:IDN+ch.geni.net+user+myusername"
     user.addKey("/home/user/.ssh/geni_dsa.pub")
     context = Context()
     context.addUser(user, default = True)
     context.cf = portal
     context.project = "GEC21"

     return context

You can dynamically alter this object at any time, but your defaults will serve your purposes for the vast
majority of your use cases.

Congratulations!  You've completed the most important ``geni-lib`` tutorial, and are set up for scripting
your own tools for better experiments!
