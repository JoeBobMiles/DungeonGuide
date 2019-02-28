# DUNGEON GUIDE

A quest to implement the most brutal math in all of D&D, the computation of
monster challenge rating (CR), into a single, time-saving application. This is
a CLI application aimed for managing monsters and computing their CR so that
lazy DMs everywhere can vet their homebrew monsters and validate third-party
party killers.

This project aims to use the YAML format for storing monster data and
information. The reason for that is that a) I adore YAML as of the time of this
writing, and b) it seems the most flexible and human readable/writable format
around. (As an aside, YAML can also be fed into Pandoc to generate PDFs and HTML
documents, so I can create pretty monster stat-blocks down the line).

## The Grand Design

The idea behind this application is mostly to help me as a game master and
player. I'm really bad at balancing things and remembering stats, so the idea
here is to create a system that automates balance checking and statblock output
so that I don't make the same mistakes I've made in the past (and boy are there
a lot of those).