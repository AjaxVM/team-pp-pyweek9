"""
pyggle.misc
This library (PYGGEL) is licensed under the LGPL by Matthew Roe and PYGGEL contributors.

The misc module contains various functions and classes that don't fit anywhere else.
"""

from include import *
import view, math3d, data

import random
from scene import BaseSceneObject

class OutlineGroup(object):
    def __init__(self, group, *args):
        self.group = group
        self.args = args
    def render(self):
        for i in self.group:
            i.render(*self.args)

def outline(renderable, color, size, color4=False):
    glPushAttrib(GL_ALL_ATTRIB_BITS)
    glClearStencil(0)
    glClear(GL_STENCIL_BUFFER_BIT)
    glEnable(GL_STENCIL_TEST)
    glStencilFunc(GL_ALWAYS, 1, 0xfff)
    glStencilOp(GL_KEEP, GL_KEEP, GL_REPLACE)
    data.BlankTexture().bind()
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    if color4:
        glColor4f(0.0, 0.0, 0.0, 0.0)
    else:
        glColor3f(0,0,0)
    renderable.render()
    glDisable(GL_LIGHTING)

    glStencilFunc(GL_NOTEQUAL, 1, 0xfff)
    glStencilOp(GL_KEEP, GL_KEEP, GL_REPLACE)

    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glLineWidth(size)
    if color4:
        glColor4f(*color+(1,))
    else:
        glColor3f(*color)
    renderable.render()

    glPopAttrib()

def test_safe(filename, acceptable_functions=[]):
    """tests all the function calls in a file against a set of acceptable ones.
       this function also does not allow importing of other modules.
       returns True, [] if there are only acceptable function calls,
       returns False and a list of bad function calls, if the test fails.
       OR returns False, "import" if there is an import statement"""
    text = open(filename, "rU").read()
    text.replace("\r", "\n")

    while "#" in text:
        text = text[0:text.index("#")] +\
               text[text.index("\n", text.index("#"))::]

    for i in text.split():
        if i == "import" or\
           i[-7::] == ":import" or\
           i[-7::] == ";import":
            return False, "import"

    #split all the text
    new = []
    cur = ""
    cur_string = False
    for i in text:
        if not cur_string:
            if i == "(":
                new.append(cur)
                cur = ""
                new.append("(")

            elif i == ")":
                new.append(cur)
                cur = ""
                new.append(")")
            else:
                if i == '"':
                    cur_string = True
                cur+=i

        else:
            if i == '"':
                cur_string = False
                cur += i
            else:
                cur += i

    if cur:
        new.append(cur)

    #remove anything that isn't a function call
    ok = []
    for i in xrange(len(new)):
        if new[i] == "(":
            last = new[i-1].split()[-1].split(".")[-1]
            if last == "(" or True in [last.endswith(__i) for __i in (", ", ",", ": ", ":","=")]:
                continue
            if len(new[i-1].split()) >= 2:
                before_that = new[i-1].split()[-2].split(".")[-1]
            else:
                before_that = None
            #remove a function/class declaration, and tuple declarations, they are different!
            if not before_that in ["def", "class"] and\
               not last in ["print", "=", "in"]:
                ok.append(last)
            else:
                if before_that in ["def", "class"]:
                    acceptable_functions.append(last)

    for i in ok:
        if i in acceptable_functions:
            continue
        else:
            return False, ok

    return True, []

def randfloat(a, b, num=8):
    """Returns a random floating point number in range(a,b)."""
    num = 10**num
    a = int(a*num)
    b = int(b*num)
    x = random.randint(a, b)
    return x * (1.0/num)

class ObjectGroup(object):
    """A simple Group object for storing a lot of similar objects in."""
    def __init__(self):
        """Create the group."""
        self._objects = []

    def __iter__(self):
        """Return an iteration object to iterate over all objects in the group."""
        return iter(self._objects)

    def __len__(self):
        """Return the size of the group."""
        return len(self._objects)

    def add(self, o):
        """Add object "o" to group."""
        self._objects.append(o)

    def remove(self, o):
        """Remove object "o" from group."""
        if o in self._objects:
            self._objects.remove(o)

class ObjectInstance(object):
    """An instance of a group of objects."""
    def __init__(self, groups):
        """Create the instance.
           groups are the ObjectGroup's this instance belongs to."""
        for g in groups:
            g.add(self)
        self._groups = groups

    def kill(self):
        """Kill the instance, removes from all groups."""
        for g in self._groups:
            g.remove(self)

    def update(self):
        """Update the instance."""
        pass

    def alive(self):
        """Return whether or not the object is alive."""
        l = []; [l.extend(i) for i in self._groups]
        return self in l

class StaticObjectGroup(BaseSceneObject):
    """A class that takes a list of renderable objects (that won't ever change position, rotation, etc.
           This includes Image3D's - as they require a dynamic look-up of the camera to billboard correctly)
       and compiles them into a single data.DisplayList so that rendering is much faster."""
    def __init__(self, objects=[]):
        """Create the group.
           objects must be a list of renderable objects"""
        BaseSceneObject.__init__(self)

        if not hasattr(objects, "__iter__"):
            objects = [objects]
        self.objects = objects
        self.gl_list = data.DisplayList()
        self.pickable = False

        self.compile()

    def add_object(self, obj):
        """Add an object to the group - if called then group.compile() must be called afterwards, to recreate the display list"""
        self.objects.append(obj)

    def compile(self):
        """Compile everything into a data.DisplayList"""
        self.gl_list.begin()
        for i in self.objects:
            i.render()
        self.gl_list.end()

    def render(self, camera=None):
        """Render the group.
           camera should be None or the camera the scene is using - only here for compatability"""
        glPushMatrix()
        x,y,z = self.pos
        glTranslatef(x,y,-z)
        a, b, c = self.rotation
        glRotatef(a, 1, 0, 0)
        glRotatef(b, 0, 1, 0)
        glRotatef(c, 0, 0, 1)
        try:
            glScalef(*self.scale)
        except:
            glScalef(self.scale, self.scale, self.scale)

        self.gl_list.render()
        data.Texture.bound = None
        glPopMatrix()

    def get_pos(self):
        """Return the position of the mesh"""
        return self.pos

def save_screenshot(filename):
    """Save a screenshot to filename"""
    pygame.image.save(pygame.display.get_surface(), filename)

def test_clockwise3d(verts):
    if len(verts) < 2:
        return True
    tot = 0
    for x in xrange(len(verts)):
        a = verts[x]
        if x+1 == len(verts):
            b = verts[-1]
        else:
            b = verts[x+1]

        tot += (b[0]-a[0]) * (b[1]+a[1])

    return tot >= 0

def make_order_right3d(verts):
    if test_clockwise3d(verts):
        new = list(verts)
        new.reverse()
        return new
    return list(verts)

class BatchVertObject(BaseSceneObject):
    def __init__(self, verts=[], texture=None, texcs=[], colorize=(1,1,1,1), scale=1,
                 pos=(0,0,0), rotation=(0,0,0), fix_order=True, usage=GL_POLYGON):
        BaseSceneObject.__init__(self)

        self.verts = verts
        if texture:
            self.texture = texture
        if texcs:
            self.texcs = texcs
        else:
            self.texcs = [(0,0)]*len(self.verts)
        self.colorize = colorize
        self.scale = scale

        self.pos = pos
        self.rotation = rotation

        self.usage = usage

        self.display_list = data.DisplayList()
        self._compile(fix_order)

    def _compile(self, fix_order):
        if not self.verts:
            return
        self.display_list.begin()

        norms = []

        if fix_order and test_clockwise3d(self.verts):
            new = list(self.verts)
            new.reverse()
            self.verts = new
            new = list(self.texcs)
            new.reverse()
            self.texcs = new

            n = 0
            while len(self.verts) % 3:
                self.verts.append(self.verts[n])
                self.texcs.append(self.texcs[n])
                n += 1

            for i in xrange(0, len(self.verts), 3):
                norms.append(math3d.calcTriNormal(self.verts[i],
                                                  self.verts[i+1],
                                                  self.verts[i+2]))

        glBegin(self.usage)
        if norms:
            for i in xrange(len(norms)):
                x = i * 3
                glNormal3f(*norms[i])
                for j in xrange(x, x+3):
                    glTexCoord2f(*self.texcs[j])
                    glVertex3f(*self.verts[j])
        else:
            for i in xrange(len(self.verts)):
                glTexCoord2f(*self.texcs[i])
                glVertex3f(*self.verts[i])
        glEnd()
        self.display_list.end()

    def render(self, camera=None):
        glPushMatrix()
        x, y, z = self.pos
        glTranslatef(x, y, -z)
        a, b, c = self.rotation
        glRotatef(a, 1, 0, 0)
        glRotatef(b, 0, 1, 0)
        glRotatef(c, 0, 0, 1)
        try:
            glScalef(*self.scale)
        except:
            glScalef(self.scale, self.scale, self.scale)
        glColor(*self.colorize)
        self.texture.bind()
        if self.outline:
            outline(self.display_list, self.outline_color, self.outline_size)
        self.display_list.render()
        glPopMatrix()
