.. _setting_up_rabbit_mq-setting-up-rabbit-mq:

Setting Up RabbitMQ
====================
Before we setup RabbitMQ, I should tell you what it is.  It's a library written
on top of the Erlang programming language which allows you to send messages
across the Internet, or just to different processes running on your machine.

Even though it is written in Erlang, RabbitMQ supports many different
programming languages, including Python.  It does this with the ``pika``
library.

Bernhard Wenzel provides a great introduction to RabbitMQ here:

.. raw:: html

  <center>
  <iframe width="560" height="315" src="https://www.youtube.com/embed/deG25y_r6OY" frameborder="0" gesture="media" allow="encrypted-media" allowfullscreen></iframe>
  </center>

I found the installation documentation on the RabbitMQ website to be largely
illegible to me as a new user, so I wrote this guide to save you the pain which
I went through.

To get your RabbitMQ server working over a network with Python requires at
least 10 steps, so I have automated them using Ansible.

If you haven't seen Ansible before it is a tool for automatically deploying
software onto Linux systems.  

To install Ansible:

.. code-block:: python

  > sudo apt-get install ansible

Now if you don't know already, figure out what your hostname is, by typing:

.. code-block:: python

  > hostname

When I type this on the raspberry pi that I tested this procedure with, I see it's
hostname is ``scotty``.  In the following examples replace ``scotty`` with your
hostname.

Now you will need to change the host files for Ansible.

.. code-block:: python

  sudo pico /etc/ansible/hosts

Now add the following:

.. code-block:: python

  [scotty]
  127.0.0.1

Save (write-out) and exit the file.  What I have done is to link my hostname, ``scotty`` to
my IP address.  127.0.0.1 is always the IP of your local machine.  This is
telling Ansible that I want to do a deployment to this machine when I reference
``scotty`` in the Ansible file (which we will talk about shortly).   If you want
to have Ansible deploy RabbitMQ to other IP addresses, you can add them below
the 127.0.0.1 address.

Ansible does it's deployments using ssh.  This means that we have to setup ssh
for our computer.

To do this, we generate a public and private key, then concatenate our public
key into our ``authorized_keys``.  If you don't have a ``id_rsa`` or a
``id_rsa.pub`` in your ``~/.ssh/`` directory, then you need to make them.  To
do this:

.. code-block:: python

  > cd ~/.ssh
  > sudo ssh-keygen

When you see option to enter a passphrase, just hit enter.

Now that you have a public and private key, you want to concatenate your
``authorized_keys`` file with your public key:

.. code-block:: python

  > sudo cat '~/.ssh/id_rsa.pub' >> '~/.ssh/authorized_keys'

.. note::

  If you have included other IP addresses in your ansible host file, you will
  need to place your public key onto these servers as well, to do this:

  .. code-block:: python
  
    > cat ~/.ssh/id_rsa.pub | \
      ssh user@hostname 'cat >> .ssh/authorized_keys'
  
To test that this works, I type the following and confirm that I can login
using ssh:

.. code-block:: python

  > ssh $USER@scotty

If this command succeeds, you will log into another version of your shell.

To exit this connection, just type ``exit``.

Now that I can login to this computer using ssh, Ansible can perform automatic
deployments for me.

Ansible uses a set of :term:`yml<YAML>` files to hold instructions on how to deploy
something.  These files are pretty straightforward to read and are largely self
documenting.

Since I only want to deploy RabbitMQ, I have written just one Ansible
:term:`yml<YAML>` file to do this job.  But a RabbitMQ server is configured
with two different configuration files, one that holds the environment
variables and the other that is an Erlang data structure.  To keep
configurations :term:`DRY<DRY>`, Ansible allows you to define
:term:`jinja2<JINJA2>` template files (j2 extension) to be filled in
with the variables defined in your deployment :term:`yml<YAML>` file.

When your run Ansible, it will reference your template files, change the parts
that you have marked up with :term:`jinja2 syntax<JINJA2>` with the variables
defined in your :term:`yml<YAML>` file, then place these newly constructed
configuration files in the directory where they need to be with the correct
permissions.

So to deploy a networkable RabbitMQ setup I have created three files which will
be used by Ansible:

====================================== =====================
Purpose                                File Name and Link
====================================== =====================
The deployment :term:`yml<YML>` script rabbit_install.yml_
The rabbitmq environment configuration rabbit-env.conf.j2_
The rabbitmq configuration             rabbitmq.config.j2_
====================================== =====================

Copy the above files into a directory on your Linux machine.

The only thing you should change is the ``hosts`` (which is set to scotty), the
``rabbit_name`` (bob), ``rabbit_password`` (dobbs) and the ``guest_password``
(rabbit123) to whatever you want.  These variables are found in the
rabbit_install.yml_ file.

Now to setup your RabbitMQ server, type:

.. code-block:: python

  > ansible-playbook -K rabbit_install.yml

This command will prompt you for your ``sudo`` password, enter it and the
rabbitmq server should be setup.

To see if your server is running, you can open the management software that
comes with it via their web app, by typing ``localhost:15672`` and log in with your
user name and password, if you didn't change this in the
rabbit_install.yml_ file, your user name will be ``bob`` and the password will
be ``dobbs``:

.. image:: _static/ RabbitMQ.PNG
    :align: center

If you have come this far you have a working RabbitMQ message broker running on
your Linux system.

Ok, now what?

To learn how to use it with Python, there is a great set of tutorials provided
on the `RabbitMQ site <https://www.rabbitmq.com/getstarted.html/>`_.

The only problem with these tutorials is that they do not show you how to
network RabbitMQ.  I wrestled with their example code for a while and got them
working across my network.

If you want to code by example I recommend that you work through their
tutorials, then use my code to see how to make it work across a network:

=================  ======================= ===================================
Tutorial Purpose   RabbitMQ Pika Tutorial  Networked Version of their Tutorial
=================  ======================= ===================================
Hello World        `simple hello world`_   - `networked hello world send`_
                                           - `networked hello world receive`_
Work Queues        `simple work queues`_   - `networked work queues send`_
                                           - `networked work queues receive`_
Publish/Subscribe  `simple pub-sub`_       - `networked pub-sub send`_
                                           - `networked pub-sub receive`_
Routing            `simple routing`_       - `networked routing send`_
                                           - `networked routing receive`_
Topic Routing      `simple topic routing`_ - `networked topic routing send`_
                                           - `networked topic routing receive`_
RPC                `simple RPC`_           - `networked rpc send`_
                                           - `networked rpc receive`_
=================  ======================= ===================================

.. note::
  On security.  This configuration is NOT secure at all.

  The rabbitmq server is not secure.  I have made it possible to transmit
  messages across the network using the default user name, guest.  Also, the
  messages are not encrypted.

.. _rabbit_install.yml: https://github.com/aleph2c/miros/blob/master/experiment/rabbit/ansible/rabbit_install.yml
.. _rabbit-env.conf.j2: https://github.com/aleph2c/miros/blob/master/experiment/rabbit/ansible/rabbitmq-env.conf.j2
.. _rabbitmq.config.j2: https://github.com/aleph2c/miros/blob/master/experiment/rabbit/ansible/rabbitmq.config.j2
.. _simple hello world: https://www.rabbitmq.com/tutorials/tutorial-one-python.html
.. _networked hello world send: https://github.com/aleph2c/miros/blob/master/experiment/rabbit/a_send.py
.. _networked hello world receive: https://github.com/aleph2c/miros/blob/master/experiment/rabbit/a_receive.py
.. _simple work queues: https://www.rabbitmq.com/tutorials/tutorial-two-python.html
.. _networked work queues send: https://github.com/aleph2c/miros/blob/master/experiment/rabbit/b_new_task.py
.. _networked work queues receive: https://github.com/aleph2c/miros/blob/master/experiment/rabbit/b_worker.py
.. _simple pub-sub: https://www.rabbitmq.com/tutorials/tutorial-three-python.html
.. _networked pub-sub send: https://github.com/aleph2c/miros/blob/master/experiment/rabbit/c_emit_log_fanout.py
.. _networked pub-sub receive: https://github.com/aleph2c/miros/blob/master/experiment/rabbit/c_receive_logs_fanout.py
.. _simple routing: https://www.rabbitmq.com/tutorials/tutorial-four-python.html
.. _networked routing send: https://github.com/aleph2c/miros/blob/master/experiment/rabbit/d_emit_log_direct.py
.. _networked routing receive: https://github.com/aleph2c/miros/blob/master/experiment/rabbit/d_receive_logs_direct.py
.. _simple topic routing: https://www.rabbitmq.com/tutorials/tutorial-five-python.html
.. _networked topic routing send: https://github.com/aleph2c/miros/blob/master/experiment/rabbit/e_emit_log_topic.py
.. _networked topic routing receive: https://github.com/aleph2c/miros/blob/master/experiment/rabbit/e_receive_logs_topic.py
.. _simple RPC: https://www.rabbitmq.com/tutorials/tutorial-six-python.html
.. _networked rpc send: https://github.com/aleph2c/miros/blob/master/experiment/rabbit/f_rpc_client.py
.. _networked rpc receive: https://github.com/aleph2c/miros/blob/master/experiment/rabbit/f_rpc_server.py
