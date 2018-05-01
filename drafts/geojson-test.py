#!/usr/bin/env python

from geojson import Feature, Point

pointone = Point((-115.81, 37.24))

featureone = Feature(geometry=pointone, properties={"prop1":"val1"})

print featureone

