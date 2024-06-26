.. Git2S3 documentation master file, created by
   sphinx-quickstart on Tue Jun 25 10:26:17 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Git2S3's documentation!
==================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   README

Git2S3 - Main
=============

.. automodule:: git2s3.main

S3
==
.. automodule:: git2s3.s3

Squire
======

.. automodule:: git2s3.squire

Configuration
=============

.. autoclass:: git2s3.config.DataStore(BaseModel)
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

====

.. autoclass:: git2s3.config.EnvConfig(BaseSettings)
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

====

.. autoclass:: git2s3.config.LogOptions(StrEnum)

====

.. autoclass:: git2s3.config.SourceControl(StrEnum)

Exceptions
==========

.. automodule:: git2s3.exc

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
