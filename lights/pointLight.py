import imp
from arnold import *
from ..GuiUtils import pollLight
from ..BaseLight import BaseLight
from .. import utils
from mathutils import Matrix
from bpy.props import (CollectionProperty,StringProperty, BoolProperty,
                       IntProperty, FloatProperty, FloatVectorProperty,
                       EnumProperty, PointerProperty)
from bl_ui import properties_data_lamp
pm = properties_data_lamp

if "bpy" not in locals():
    import bpy

enumValue = ("POINTLIGHT","Point","")
blenderType = "POINT"

# There must be one class that inherits from bpy.types.PropertyGroup
# Here we place all the parameters for the Material
class BtoAPointLightSettings(bpy.types.PropertyGroup):
    opacity = FloatProperty(name="Opacity",default=1)

className = BtoAPointLightSettings
bpy.utils.register_class(className)

def write(li):
    blight = BaseLight(li)    
    blight.alight = AiNode(b"point_light")
    AiNodeSetStr(blight.alight,b"name",blight.lightdata.name.encode('utf-8'))
    # set position
    # fist apply the matrix
    matrices = AiArrayAllocate(1, 1, AI_TYPE_MATRIX);
    lmatrix = blight.light.matrix_world.copy()
    matrix = utils.getYUpMatrix(lmatrix)
    AiArraySetMtx(matrices,  0 , matrix)
    AiNodeSetArray(blight.alight, b"matrix", matrices)
    # write all common attributes
    blight.write()

