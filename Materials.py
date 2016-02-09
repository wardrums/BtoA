import imp, os, glob, sys
from arnold import *
from bpy.props import (CollectionProperty,StringProperty, BoolProperty,
IntProperty, FloatProperty, FloatVectorProperty, EnumProperty, PointerProperty)
from bl_ui import properties_material
pm = properties_material

if "bpy" in locals():
    pass
else:
    import bpy


########################
#
# custom material properties
#
########################

   

class BtoA_context_material(pm.MaterialButtonsPanel,bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_label = "BtoA Materials"
    bl_context = "material"
    COMPAT_ENGINES = {'CYCLES'}

    @classmethod
    def poll(cls, context):
        return (context.material or context.object)

    def draw(self, context):
        layout = self.layout

        mat = context.material
        ob = context.object
        slot = context.material_slot
        space = context.space_data
        is_sortable = len(ob.material_slots) > 1

        if ob:
            rows = 1
            if (is_sortable):
                rows = 4

            row = layout.row()

            row.template_list("MATERIAL_UL_matslots", "", ob, "material_slots", ob, "active_material_index", rows=rows)

            col = row.column(align=True)
            col.operator("object.material_slot_add", icon='ZOOMIN', text="")
            col.operator("object.material_slot_remove", icon='ZOOMOUT', text="")

            col.menu("MATERIAL_MT_specials", icon='DOWNARROW_HLT', text="")

            if is_sortable:
                col.separator()

                col.operator("object.material_slot_move", icon='TRIA_UP', text="").direction = 'UP'
                col.operator("object.material_slot_move", icon='TRIA_DOWN', text="").direction = 'DOWN'

            if ob.mode == 'EDIT':
                row = layout.row(align=True)
                row.operator("object.material_slot_assign", text="Assign")
                row.operator("object.material_slot_select", text="Select")
                row.operator("object.material_slot_deselect", text="Deselect")

        split = layout.split(percentage=0.65)

        if ob:
            split.template_ID(ob, "active_material", new="material.new")
            row = split.row()

            if slot:
                row.prop(slot, "link", text="")
            else:
                row.label()
        elif mat:
            split.template_ID(space, "pin_id")
            split.separator()




def rnaPropUpdate(self, context):
    self.update_tag()

class BtoA_material_shader_gui(pm.MaterialButtonsPanel, bpy.types.Panel):
    bl_label = "Arnold Shader"
    COMPAT_ENGINES = {'BtoA'}

    @classmethod
    def poll(cls, context):
        mat = context.material
        engine = context.scene.render.engine
        return pm.check_material(mat) and (mat.type in {'SURFACE', 'WIRE'}) and (engine in cls.COMPAT_ENGINES)

    def draw(self, context):
        layout = self.layout
        mat = pm.active_node_mat(context.material)
        split = layout.split()
        split.prop(mat.BtoA,"shaderType")

class BtoAMaterialSettings(bpy.types.PropertyGroup):
    name="BtoAMaterialSettings"
    #################   
    # Import Modules from default folder
    #################
    defaultMatDir = os.path.join(os.path.dirname(__file__),"materials")
    defaultMats = glob.glob(os.path.join(defaultMatDir,"*.py"))
    # if the dir is not a "module", lets turn it into one
    if not os.path.exists(os.path.join(defaultMatDir,"__init__py")):
        fin = open(os.path.join(defaultMatDir,"__init__.py"),'w')
        fin.close()

    # load all materials from the materials folder
    materials = []
    loadedMaterials = {}
    for modulePath in defaultMats:
        module = os.path.basename(modulePath)
        moduleName = module[:-3]
        if module == '__init__.py' or module[-3:] != '.py':
            continue
        print("BtoA:: Loading %s"%module) 
        foo = __import__("BtoA.materials."+moduleName, locals(), globals())
        module = eval("foo.materials."+moduleName)
        materials.append(module.enumValue)
        vars()[moduleName] = PointerProperty(type=module.className)
        loadedMaterials[module.enumValue[0]] = module

    #################   
    # Import Modules from the Material Module search path
    # THIS DOES NOT WORK. The GUI WILL NOT REDRAW PROPERLY
    #################
    #rawMatPath = os.environ["BTOA_MATERIAL_PATHS"]
    #searchPaths = []
    #searchPaths = rawMatPath.split(":")
    # separate /// for windows paths
    #for i in searchPaths:
    #    if "///" in i:
    #        i = i.replace(":")

    #for i in searchPaths:
    #    localMats = glob.glob(os.path.join(i,"*.py"))
    #    if len(localMats) == 0:
    #        break

        # if the dir is not a "module", lets turn it into one
    #    if not os.path.exists(os.path.join(i,"__init__py")):
    #        fin = open(os.path.join(i,"__init__.py"),'w')
    #        fin.close()

    #    for modulePath in localMats:
    #        module = os.path.basename(modulePath)
    #        moduleDir = os.path.dirname(modulePath)
    #        sys.path.append(os.path.dirname(moduleDir))
    #        print(sys.path)
    #        moduleDir = os.path.basename(moduleDir)
    #        moduleName = module[:-3]
    #        if module == '__init__.py' or module[-3:] != '.py':
    #            continue
    #        print("Loading ",module) 
            
    #        foobar = __import__(moduleDir+"."+moduleName, locals(), globals())
    #        loadedModule = eval("foobar."+moduleName)
    #        materials.append(loadedModule.enumValue)
    #        vars()[moduleName] = PointerProperty(type=loadedModule.className,name=moduleName)
    #        loadedMaterials[loadedModule.enumValue[0]] = loadedModule

    shaderType = EnumProperty(items=materials,
                             name="Shader", description="Surface Shader", 
                             default="STANDARD")

bpy.utils.register_class(BtoAMaterialSettings)
bpy.types.Material.BtoA = PointerProperty(type=BtoAMaterialSettings,name='BtoA')

class Materials:
    def __init__(self, scene,textures=None):
        self.scene = scene
        self.textures = None
        if textures:
            self.textures = textures.texturesDict
        self.materialDict = {}

    def writeMaterials(self):
        for mat in bpy.data.materials:
            self.writeMaterial(mat)

    def writeMaterial(self,mat):
        outmat = None
        currentMaterial = mat.BtoA.loadedMaterials[mat.BtoA.shaderType]
        outmat = currentMaterial.write(mat,self.textures)

        AiNodeSetStr(outmat,b"name",mat.name.encode('utf-8'))
        self.materialDict[mat.as_pointer()] = outmat
        return outmat
