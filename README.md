Scanning XES
============

A pipeline for the [ParSeq framework](https://github.com/kklmn/ParSeq) that
implements data processing of XES theta scans, where the crystals are scanned
in their theta angle and the analyzed emission is collected by a 2D detector.

This pipeline also serves as an example for creating analysis nodes, transforms
that connect these nodes and widgets that set options and parameters of the
transforms.

<p align="center">
  <img src="parseq_XES_scan/doc/_images/Mo-Kb13.gif" width=800 />
</p>

<p align="center">
  <img src="parseq_XES_scan/doc/_images/about.gif" width=300 />
</p>

Dependencies
------------

* [ParSeq](https://github.com/kklmn/ParSeq) -- the framework package,
* [silx](https://github.com/silx-kit/silx) -- used for plotting and Qt imports.

How to use
----------

Either install ParSeq and this pipeline application by their installers or put
their main folders near by (i.e. in the same folder) and run
`python XES_scan_reduced_start.py`. You can try it with `--test` to load test data
and/or `--noGUI` but an assumed pattern is to load a project file; use the test
project file located in `parseq_XES_scan_reduced/saved`.