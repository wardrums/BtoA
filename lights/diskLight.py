import imp
from arnold import *
from ..GuiUtils import pollLight
from ..BaseLight import BaseLight
from ..AiTypes import *
from mathutils import Matrix
from bpy.props import (CollectionProperty,StringProperty, BoolProperty,
                       IntProperty, FloatProperty, FloatVectorProperty,
                       EnumProperty, PointerProperty)
from bl_ui import properties_data_lamp
from .. import utils
from bl_ui.properties_data_lamp import DataButtonsPanel

pm = properties_data_lamp

if "bpy" not in locals():
    import bpy

enumValue = ("DISKLIGHT","Disk","")
blenderType = "SPOT"

# There must be one class that inherits from bpy.types.PropertyGroup
# Here we place all the parameters for the Material
class BtoAPointLightSettings(bpy.types.PropertyGroup):
    opacity = FloatProperty(name="Opacity",default=1)

    indirect = ai_FLOAT(ai_name='indirect')
    sss = ai_FLOAT(ai_name='sss')
    diffuse = ai_FLOAT(ai_name='diffuse')
    max_bounces = ai_INT(ai_name='max_bounces')
#    filters = ai_NODEs(ai_name='filters')
    affect_diffuse = ai_BOOL(ai_name='affect_diffuse')
    exposure = ai_FLOAT(ai_name='exposure')
    volume_samples = ai_INT(ai_name='volume_samples')
    cast_volumetric_shadows = ai_BOOL(ai_name='cast_volumetric_shadows')
    specular = ai_FLOAT(ai_name='specular')
    time_samples = ai_FLOATs(ai_name='time_samples')
    color = ai_RGB(ai_name='color')
    intensity = ai_FLOAT(ai_name='intensity')
    radius = ai_FLOAT(ai_name='radius')
    volume = ai_FLOAT(ai_name='volume')    
    #decay_type = ai_ENUM(ai_name='decay_type')

className = BtoAPointLightSettings
bpy.utils.register_class(className)

def write(li):
    blight = BaseLight(li)    
    blight.alight = AiNode(b"disk_light")
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


class BtoA_DiskLight_gui(DataButtonsPanel, bpy.types.Panel):
    bl_label = "Disk Light"
    COMPAT_ENGINES = {'BtoA'}

#    @classmethod
#    def poll(cls, context):
#        return pollLight(cls,context,enumValue[0],blendLights={"AREA"} )
    @classmethod
    def poll(cls, context):
        lamp = context.lamp
        engine = context.scene.render.engine
        return (engine in cls.COMPAT_ENGINES)
        
    def draw(self, context):
        try:
            layout = self.layout
            lamp = context.lamp
            disk = lamp.BtoA.diskLight
            split = layout.split()

            col1 = split.column()
            col2 = split.column()
            col1.prop(spot, "penumbra_angle", text="Penumbra")
            col2.prop(spot, "aspect_ratio", text="Aspect Ratio")
            col2.prop(lamp, "show_cone")
        except:
            pass