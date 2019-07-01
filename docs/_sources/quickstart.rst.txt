
  *I invented the term object oriented, and I can tell you that C++ wasn't what I had in mind.* 
 

  -- Alan Kay

.. _quick-start:

Quick Start
===========
If you know nothing about statecharts I suggest you start here: :ref:`zero to
one <zero_to_one-zero-to-one>`

If you haven't seen UML diagrams before, scan the :ref:`understanding diagrams
<reading_diagrams-reading-diagrams>` part of this guide to make sense of the
pictures.

If you are an embedded developer and want to port your working miros Python code to
C/C++ for a considerable performance gain.  Check out this project: `qp codebase
<https://github.com/QuantumLeaps/qpc>`_.  It is documented here: `Practical UML
Statecharts in C/C++, 2nd Edition
<https://sourceforge.net/projects/qpc/files/doc/PSiCC2.pdf/download>`_.

In the next section we will show how to tackle a problem using UML statecharts.

.. _quickstart-a-quick-example:

A Networked Sprinkler
---------------------

Let's use the Python miros library to build a sprinkler. This
sprinkler will water our plants in the summer, after dark, and only when it is
not raining.  To do this we will call out to the `open weather api
<https://openweathermap.org/api>`_.

Once the networked sprinkler knows which city its working in it should just turn
on and operate as if it could measure the weather conditions with local instruments.

The ``open weather`` documentation recommends that we request city information
using a city ID, so our software should extract this id from a file the ``open
weather`` folks have put on their website:
http://bulk.openweathermap.org/sample/city.list.json.gz.

Our design will consist of three different active objects which will work
together:

   * something that will control the sprinkler (Sprinkler).
   * something that will download a file from the open weather website and
     extract the correct city ID for a given city and country
     (OpenWeatherMapCityDetails).
   * something that will act like a weather station attached to the sprinkler,
     by making calls to the open weather API (CityWeather).

Here is a high level diagram of how these parts fit together and what they do:

.. image:: _static/sprinkler_high_level.svg
    :target: _static/sprinkler_high_level.pdf
    :align: center

.. note::

  On interpreting the diagram:

  The Sprinkler class **will have a** CityWeather object **and an**
  OpenWeatherMapCityDetails object (black diamond arrows).  The CityWeather
  object will interact with the Sprinkler and OpenWeatherMapCityDetails objects.
  (dashed lines)

Each of the objects will be a type of miros ActiveObject, so they will:

  * be able to subscribe and post events.
  * run in their own thread
  * be pre-instrumented with sensible logging (for trouble shooting and
    documentation)

.. _quickstart-figuring-out-what-information-will-be-passed-around:

Figuring out what Information will be Passed Around
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

So let's look at our high level design again and think about them as cells.
They manage their own clocks and their own internal states, but they need to
pass simple messages to one another in the form of ``miros.Events``.

Lets wave our hands and assume the inner parts of the cells are working, but we
want to see how the cells communicate with one another.

.. image:: _static/sprinkler_high_level.svg
    :target: _static/sprinkler_high_level.pdf
    :align: center

What information should they share?  Let's drill in a bit.

We need to figure out how to call the open weather api, with a city id, before it
will return weather information for its location. This is the problem the
``OpenWeatherMapCityDetails`` object solves: it will provide the city id when we
give it the city and country names of where we have placed the sprinkler.

The high level event interface of the ``OpenWeatherMapCityDetails`` object will look
like this:

.. image:: _static/open_weather_map_city_details_medium.svg
    :target: _static/open_weather_map_city_details_medium.pdf
    :align: center

This diagram shows us the input and output goals; for a city and a country
return the open weather api's city id.  

``OpenWeatherMapCityDetails`` will subscribe to and receive events called
``REQUEST_DETAILS_FOR_CITY``.  Below this event is the namedtuple,
``RequestDetailsForCityPayload``.  This is the immutable payload that will ride
inside of the event.  Likewise the namedtuple called ``CityDetailsPayload`` will
ride inside of the ``CITY_DETAILS`` event.

.. note::

   On interpreting the diagram:

   All of the high level event interfaces will look like this one.  Arrows going
   into the rounded rectangle beside the green dots are the published events
   that the object will consume.  Arrows leaving the object, beside the red
   dots, will be the events it publishes.  The namedtuples near the event's name
   will describe the payload data structure.

.. note::

   On namedtuples:

   The miros library can place any kind of object into an event payload.
   However event payloads are objects that are shared between threads, we don't
   want one thread to change this object while another thread is trying to read
   it, so as a rule use immutable objects as payloads when programming with miros
   (to avoid nasty multithreading bugs).

The high level event interface of the ``CityWeather`` object looks like this:

.. image:: _static/city_weather_details_medium.svg
    :target: _static/city_weather_details_medium.pdf
    :align: center

This diagram shows us the ``CityWeather`` input and output goals: For a city and
a country get its city id, and when asked, return the weather information for
that city.

.. note::

  On implimentation (and sausage making):

  I wrote some prototype code, to poke at the open weather city api prior to
  designing this system.  I used the python debugger to break right after
  receiving a message from their service.  I compared what I was seeing with
  their documentation, then decided on what the payload data structures should
  look like.

Here is the high level interface diagram of the ``Sprinkler``:

.. image:: _static/sprinkler_details_medium.svg
    :target: _static/sprinkler_details_medium.pdf
    :align: center

This diagram shows us the ``Sprinkler`` input and output goals: Ask for the
weather and get the weather.



Now that we have a decent understanding about what information we want to flow
in our system, let's focus in on each part.

.. _quickstart-openweathermapcitydetails-specifications:

OpenWeatherMapCityDetails Specifications
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The ``OpenWeatherMapCityDetails`` needs to provide a city ID given a city and a
country.  This city ID will be used by the ``CityDetails`` object to make a call
to the open web API.

.. image:: _static/open_weather_map_city_details.svg
    :target: _static/open_weather_map_city_details.pdf
    :align: center


.. _quickstart-citydetails-specifications:

CityDetails Specifications
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. _quickstart-sprinkler-specifications:

Sprinkler Specifications
^^^^^^^^^^^^^^^^^^^^^^^^




.. raw:: html

  <a class="reference internal" href="introduction.html"<span class="std-ref">prev</span></a>, <a class="reference internal" href="index.html#top"><span class="std std-ref">top</span></a>, <a class="reference internal" href="zero_to_one.html"><span class="std std-ref">next</span></a>

.. toctree::
   :maxdepth: 2
   :caption: Contents:

