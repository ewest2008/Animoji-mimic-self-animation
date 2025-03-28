#!/usr/bin/env python3

from glumpy import app, gloo, gl
import numpy as np
import cv2
from utils.detect import get_face, get_marks
from utils.shaders import img_vertex, img_fragment

# GLSL shaders for lines

app.use("pyglet")
vertex = """
attribute vec2 position;
void main(){
    gl_Position = vec4(position, 0.0, 1.0);
}"""
frag = """
void main(){ gl_FragColor = vec4(0.0, 0.0, 0.0, 1.0); }"""

# creating a GL app window
# GL programs for landmark drawing
win = app.Window(color=(1,1,1,1))
brow1 = gloo.Program(vertex, frag, count=5)
brow2 = gloo.Program(vertex, frag, count=5)
eye1 = gloo.Program(vertex, frag, count=6)
eye2 = gloo.Program(vertex, frag, count=6)
nose1 = gloo.Program(vertex, frag, count=4)
nose2 = gloo.Program(vertex, frag, count=5)
lip1 = gloo.Program(vertex, frag, count=12)
lip2 = gloo.Program(vertex, frag, count=8)
jaw = gloo.Program(vertex, frag, count=17)

# GL program to render camera face image
quad = gloo.Program(img_vertex, img_fragment, count=4)
# cam image is displayed in a square region of 0.4x0.4 at bottom left corner
quad['position'] = [(-0.6,-1), (-1,-1), (-0.6,-0.6), (-1,-0.6)]
quad['texcoord'] = [( 0, 1), ( 1, 1), ( 0, 0), ( 1, 0)]
gl.glLineWidth(1.5)

# video capture object
cap = cv2.VideoCapture(0)
# setting frame capture duration to 40ms or 25fps
cap.set(cv2.CAP_PROP_POS_MSEC, 40)

# first lets make sure it finds a face
face_coord = None
while face_coord is None:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    face_coord = get_face(gray)

@win.event
def on_draw(dt):
    global face_coord, cap
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    new_face = get_face(gray)
    face_coord = face_coord if new_face is None else new_face
    marks = get_marks(gray, face_coord)*-1    #invert coords to render in GL
    # assign landmark points
    brow1['position'] = marks[17:22]
    brow2['position'] = marks[22:27]
    eye1['position'] = marks[36:42]
    eye2['position'] = marks[42:48]
    nose1['position'] = marks[27:31]
    nose2['position'] = marks[31:36]
    lip1['position'] = marks[48:60]
    lip2['position'] = marks[60:68]
    jaw['position'] = marks[0:17]
    # assign face image to texture
    yt, yb = max(face_coord.top()-20, 0), min(face_coord.bottom()+20, 480)
    xl, xr = max(face_coord.left()-10, 0), min(face_coord.right()+10, 640)
    img = frame[yt:yb, xl:xr]
    img = cv2.cvtColor(cv2.resize(img, (100,100)), cv2.COLOR_BGR2RGB)
    quad['texture'] = img
    # render stuff to GL window
    win.clear()
    brow1.draw(gl.GL_LINE_LOOP)
    brow2.draw(gl.GL_LINE_LOOP)
    eye1.draw(gl.GL_LINE_LOOP)
    eye2.draw(gl.GL_LINE_LOOP)
    nose1.draw(gl.GL_LINE_STRIP)
    nose2.draw(gl.GL_LINE_LOOP)
    lip1.draw(gl.GL_LINE_LOOP)
    lip2.draw(gl.GL_LINE_LOOP)
    jaw.draw(gl.GL_LINE_STRIP)
    quad.draw(gl.GL_TRIANGLE_STRIP)

# GL framerate set t 25fps
app.run(framerate=25)
cap.release()
