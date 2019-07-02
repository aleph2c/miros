
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

.. image:: _static/sprinkler.jpg
    :target: https://www.ijcaonline.org/archives/volume172/number6/28254-2017915160
    :align: center

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

We will use three different statecharts, one per object in the above diagram.
Having independent objects interface in a statechart is called orthogonality in
statechart theory.

.. _quickstart-figuring-out-what-information-will-be-passed-around:

Figuring out what Information will be Passed Around
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Let's wave our hands an assume that the three active objects used in this
designed have been built already and are working, but we want to figure out how
they will communicate with one another.

David Harel called such a thing, a ``statocol`` (state protocol):  what
information will the statecharts need to share, so as a group, they will
achieve our design goal; and give us our networked sprinkler:

.. image:: _static/sprinkler_high_level.svg
    :target: _static/sprinkler_high_level.pdf
    :align: center

We need to figure out how to call the open weather api, with a city id, before it
will return weather information for its location. This is the problem the
``OpenWeatherMapCityDetails`` object solves: it will provide the city id when we
give it the city and country names of where we have placed the sprinkler.

A rough sketch of the ``OpenWeatherMapCityDetails`` object will look like this:

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

There can be many events which all share the same name; an event's name is
called a signal.  An event of a particular signal, can also carry a python
object with it.  As this event is passed through the system, the object that it
is carrying stays linked to it.  A linked object is called a payload.  The miros
library lets you link any python object to an event, or in other words, your
Event can have any Python object as a payload.  However, we are limiting
ourselves to only send namedtuples as payloads, because they are immutable and
provide very nice syntax.

Here is how you would use the miros library to publish (public send) a
``REQUEST_DETAILS_FOR_CITY`` event:

.. code-block:: python
 
  from miros import event
  from miros import signals
  from collections import namedtuple

  # define the REQUEST_DETAILS_FOR_CITY payload type
  RequestDetailsForCityPayload = namedtuple('RequestDetailsForCityPayload',
    ['city', 'country'])
   
  # Assume the CityWeather ActiveObject has been defined elsewhere and is
  # working.
  city_weather = CityWeather()

  # Published an event will have a red dot beside it on the diagram, it
  # publishes and the event has to wait somewhere before it is processed (red
  # light).
  #
  # If the 'REQUEST_DETAILS_FOR_CITY' signal name has not been defined before
  # miros will define it now.  Its signal will be given a signal_number
  # attribute and a signal_name attribute equal to 'REQUEST_DETAILS_FOR_CITY'
  # (signal name construction happens automatically in miros)
  city_weather.publish(
    Event(signal=signals.REQUEST_DETAILS_FOR_CITY,
      payload=RequestDetailsForCityPayload(city='Vancouver', country='CA')
    )
  )
  # any ActiveObject that has subscribed to REQUEST_DETAILS_FOR_CITY will 
  # receive the event and react to it.  When an event is received which
  # was subscribed to on the diagram, it will have a green dot beside it.
  # (green light)

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

CityWeather Specifications
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: _static/city_weather.svg
    :target: _static/city_weather.pdf
    :align: center

.. _quickstart-sprinkler-specifications:

Sprinkler Specifications
^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: _static/sprinkler.svg
    :target: _static/sprinkler.pdf
    :align: center

.. raw:: html

  <a class="reference internal" href="introduction.html"<span class="std-ref">prev</span></a>, <a class="reference internal" href="index.html#top"><span class="std std-ref">top</span></a>, <a class="reference internal" href="zero_to_one.html"><span class="std std-ref">next</span></a>

.. toctree::
   :maxdepth: 2
   :caption: Contents:

