# Term-Project-112 - Asteroids
# “Asteroids” is based on the shooter arcade game with the same name created by Atari in 1979. In the game, you will be controlling a spaceship to shoot asteroids and score points, as well as dodge aliens.
#
# asteroids.py is the main file. It contains the game class and the ModalApp class. splashScreen.py and endScreen.py contain the spash and end screen classes. The project only uses 112 graphics, so no modules are needed.
#
# Most of the important code is in player.py, asteroids.py, astroid.py, ray.py, boid.py, and sliceFunction.py.
#
# Sources used:
# https://www.red3d.com/cwr/boids/
# https://github.com/RamenBucket/112-Hackathon-20
# https://ncase.me/sight-and-light/
# https://thecodingtrain.com/CodingChallenges/124-flocking-boids
# http://rosettacode.org/wiki/Sutherland-Hodgman_polygon_clipping#Python
# https://www.cs.cmu.edu/~112/notes/notes-animations-part1.html#installingModules
# https://www.geeksforgeeks.org/check-if-two-given-line-segments-intersect/
# https://thecodingtrain.com/CodingChallenges/145-2d-ray-casting.html
#
# Controls:
# w - accelerate forward
# s - decelerate
# a - turn counterclockwise
# d - turn clockwise
# space - shoot
#
# Gameplay:
# Health is in the top left corner and score is in the top right corner
# Black polyons are asteroids and you loose health if you are inside.
# Small white squares are aliens. You don't loose health from them, but they can shoot tiny black squares that can damage you.
# When you sucessfully "slice" an asteroid, you get 100 points

