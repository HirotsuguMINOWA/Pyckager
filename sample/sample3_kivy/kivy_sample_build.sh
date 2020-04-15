#!/bin/bash
cython -3 --embed sample3_kivy_main.py
gcc `pkg-config --cflags --libs python3` kivy_sample.c
