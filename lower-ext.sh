#!/bin/bash

for f in *.JPG; do mv "$f" "${f%.JPG}.jpg"; done
