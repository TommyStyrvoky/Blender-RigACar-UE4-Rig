bl_info = {
    "name": "RigACar to Unreal Engine",
    "blender": (3, 6, 0),
    "version": (1, 0),
    "author": "Tommy Styrvoky",
    "location": "object > create a rig for UE from RigACar",
    "category": "Object",
}

import bpy
import mathutils
from mathutils import Vector,Euler

boneNames =['Body',
            'wheel.Ft.L','wheel.Ft.R','wheel.Bk.L','wheel.Bk.R',
            'wheelbrake.Ft.L','wheelbrake.Ft.R','wheelbrake.Bk.L','wheelbrake.Bk.R']

class BuildUERig(bpy.types.Operator):
    global boneNames
    
    """Create rig for unreal engine export"""
    bl_idname = "object.buildcar"
    bl_label = "create a rig for UE from RigACar"
    bl_options = {'REGISTER', 'UNDO'} 

    def execute(self, context):
        RigACarRig = bpy.context.active_object
        if RigACarRig == None:
            self.report({"WARNING"}, 'no armature selected')
            return {"CANCELLED"}
            
        objectType = RigACarRig.type
        location = RigACarRig.location
        rotation = RigACarRig.rotation_euler
        
        if not objectType== 'ARMATURE':#break
            self.report({"WARNING"}, f'Select an armature not {objectType}')
            return {"CANCELLED"}

        
        pathConstraint = None
        pathConstraintState = False
        for constraint in RigACarRig.constraints:
            if constraint.type == 'FOLLOW_PATH':
                pathConstraint = constraint
                pathConstraintState = pathConstraint.enabled
                break
            
        if pathConstraint:
            if pathConstraintState:
                pathConstraint.enabled = False
        RigACarRig.rotation_euler = Euler((0,0,0), 'XYZ')
        RigACarRig.location = Vector((0,0,0))

        carUERig = None
        
        #create bones and add constraints
        
        bpy.ops.object.armature_add()
        carUERig = bpy.context.view_layer.objects.active
        carUERig.location = RigACarRig.location
        carUERig.name ='UE_Car_Rig'
        carUERig.parent=RigACarRig.parent
        
        bpy.ops.object.mode_set(mode = 'EDIT', toggle=False)
        bpy.context.view_layer.objects.active = carUERig
        carUERig.data.bones[0].name = 'Root'
        root = carUERig.data.bones[0]
        
        
        for boneName in boneNames:
            rigObj = None
            bone =None
            for child in RigACarRig.children:
                if child.type == 'MESH' and child.name==boneName:
                    rigObj = child
                    break
            
            if rigObj:
                bpy.context.view_layer.objects.active = carUERig
                bpy.ops.object.mode_set(mode = 'EDIT', toggle=False)
                bone = carUERig.data.edit_bones.new(boneName)
                transform = rigObj.matrix_world.to_translation()
                bone.head = transform+Vector((0,0,0)) 
                bone.tail = transform+Vector((0,0,1)) #offset
                bone.parent = carUERig.data.edit_bones['Root']

                bpy.ops.object.mode_set(mode = 'POSE', toggle=False)
                bpy.context.object.data.bones.active = carUERig.data.bones[boneName]
                bone.select = True
                
                bpy.ops.pose.constraint_add(type='CHILD_OF')
                bpy.context.object.pose.bones[boneName].constraints["Child Of"].target = rigObj
                bpy.ops.constraint.childof_set_inverse(constraint="Child Of", owner='BONE')
                bpy.ops.object.mode_set(mode = 'OBJECT', toggle=False)

        #return rig to original position
        RigACarRig.location = location
        RigACarRig.rotation_euler = rotation
        if pathConstraint:
            if pathConstraintState:
                pathConstraint.enabled = True

        bpy.context.view_layer.objects.active = carUERig
        return {'FINISHED'}            # Lets Blender know the operator finished successfully.

def menu_func(self, context):
    self.layout.operator(BuildUERig.bl_idname)

def register():
    bpy.utils.register_class(BuildUERig)
    bpy.types.VIEW3D_MT_object.append(menu_func)  # Adds the new operator to an existing menu.

def unregister():
    bpy.utils.unregister_class(BuildUERig)

if __name__ == "__main__":
    register()