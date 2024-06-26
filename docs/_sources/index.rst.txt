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

Squire
======
.. automodule:: git2s3.squire

Configuration
=============

.. autoclass:: git2s3.config.Field(BaseModel)
   :members: EnvConfig
   :exclude-members: _abc_impl, model_config, model_fields

====

.. autoclass:: git2s3.config.EnvConfig(BaseSettings)
   :members: EnvConfig
   :exclude-members: _abc_impl, model_config, model_fields, model_computed_fields

====

.. autoclass:: git2s3.config.LogOptions(StrEnum)

====

.. autoclass:: git2s3.config.Fields(StrEnum)

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
