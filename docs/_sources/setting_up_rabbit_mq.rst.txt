.. _setting_up_rabbit_mq-setting-up-rabbit-mq:

Setting Up Rabbit MQ
====================
Before we setup Rabbit MQ I should tell you what it is.  It's a library written
on top of the Erlang programming language which allows you to send messages
across the Internet, or just to different processes running on your machine.

Bernhard Wenzel provides a great introduction to RabbitMQ here:

.. raw:: html

  <center>
  <iframe width="560" height="315" src="https://www.youtube.com/embed/deG25y_r6OY" frameborder="0" gesture="media" allow="encrypted-media" allowfullscreen></iframe>
  </center>

We will use it as a message abstraction layer.  We will try to abstract away
how messages are sent across the network so that all of your statecharts look
like they are sitting on the same computer.

I found the installation documentation on the RabbitMQ web sight to be largely
illegible to me as a new user, so I wrote this guide to save you the pain which
I went through.

To get your rabbitmq software working over a network with Python requires at
least 10 steps, so I have automated them using Ansible.

To install Ansible:

.. code-block:: python

  > sudo apt-get install ansible

If you haven't seen Ansible before it is a tool for automatically deploying
software onto Linux systems.  Now you will need to figure out what your
hostname is:

.. code-block:: python

  > hostname

When I type this on the raspberry pi that I tested this procedure with I see it's
hostname is ``scotty``.  In the following examples replace ``scotty`` with your
hostname.

Now you will need to change the host files for ansible.

.. code-block:: python

  sudo pico /etc/ansible/hosts

Now add the following:

.. code-block:: python

  [scotty]
  127.0.0.1

Save and exit the file.  What I have done is to link my hostname, ``scotty`` to
my IP address.  127.0.0.1 is always the IP of your local machine.  This is
telling Ansible that I want to do a deployment to this machine when I reference
``scotty`` in the ansible file (which we will talk about shortly).   If you want
to have Ansible deploy rabbitmq to other IP addresses, you can add them below
the 127.0.0.1 address.

Ansible does it's deployments using ssh.  This means that we have to setup ssh
for our computer.

To do this, we generate a public and private key, then concatenate our public
key into our ``authorized_keys``.  If you don't have a ``id_rsa`` or a
``id_rsa.pub`` in your ``~/.ssh/`` directory, then you need to make them.  To
do this:

.. code-block:: python

  > sudo ssh-keygen

When you see option to enter a passphrase, just hit enter.

Now that you have a public and private key, you want to concatenate your
``authorized_keys`` file with your public key:

.. code-block:: python

  sudo cat '~/.ssh/id_rsa.pub' >> '~/.ssh/authorized_keys'

To test that this works, I type the following and confirm that I can login
using ssh:

.. code-block:: python

  ssh $USER@scotty

To exit this connection, I just type ``exit``.

Now that I can login to this computer using ssh, Ansible can perform automatic
deployments for me.

Ansible uses a set of yaml files to hold instructions on how to deploy
something.  These files are pretty straightforward to read and are largely self
documenting.

Since I only want to deploy rabbitmq, I have written just one ansible yaml file to
do this job.  But a rabbitmq server is configured with two different configuration
files, one that holds the environment variables and the other that is an
Erlang data structure.  To keep configurations DRY ansible allows you to define
jinja2 template files (j2) that will be filled in with the variables defined in your
deployment yaml file.

To deploy a networkable rabbitmq setup I have created three files:

* rabbit_install.yml
* rabbit-env.conf.j2
* rabbitmq.config.j2

The only thing you should change is the ``rabbit_name``, ``rabbit_password`` and
the ``guest_password`` to whatever you want.  These variables are found in the
``rabbit_install.yml`` file.

Copy these files into a directory on your linux machine, then in that same
directory:

.. code-block:: python

  > ansible-playbook -K rabbit_install.yml

This command will prompt you for your ``sudo`` password, enter it and the
rabbitmq server should be setup.
