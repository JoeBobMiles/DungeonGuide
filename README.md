# DUNGEON GUIDE

This is a CLI application for managing monster, NPC, item, and spell stat-blocks
for D&D. It uses YAML as the storage format for data.

## Why YAML?

1.  I adore YAML as of the moment.
2.  YAML is easy for humans to read and write (easier than other formats like
    JSON), and there is a handy package that is already available for Python.
3.  YAML, unlike other markup languages, can be fed into Pandoc to generate web
    and print friendly documents, which for me is a plus.

## The Grand Design

The idea behind this application is mostly to help me as a game master and
player. I'm really bad at balancing things and remembering stats, so the idea
here is to create a system that automates balance checking and statblock output
so that I don't make the same mistakes I've made in the past.