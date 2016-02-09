import imp
from mathutils import Matrix
from arnold import *

if "bpy" in locals():
    imp.reload(BaseLight)
else:
    import bpy
    from . import BaseLight

class PointLight(BaseLight.BaseLight):
    def __init__(self, light):
        super(PointLight,self).__init__(light)
         
    def write(self):
        self.alight = AiNode(b"point_light")
        AiNodeSetStr(self.alight,b"name",self.lightdata.name.encode('utf-8'))
        # set position
        # fist apply the matrix
        lmatrix = self.light.matrix_world
        tmatrix = mmatrix.transposed()
        AiArraySetMtx(matrices,  0 , tmatrix)
        AiNodeSetArray(self.alight, b"matrix", matrices)

        # Write common attributes
        super(PointLight,self).write()


