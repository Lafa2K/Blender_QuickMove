bl_info = {
    "name": "Quick Move and Rotation (codewalker)",
    "author": "lafa2k",
    "version": (1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Item > Transform",
    "description": "Sincroniza Pos/Rot com correção de W para CodeWalker",
    "category": "Object",
}

import bpy
from mathutils import Vector, Quaternion

class CW_OT_ApplyTransform(bpy.types.Operator):
    """Aplica Posição e Rotação com correção de W"""
    bl_idname = "object.cw_sync_apply"
    bl_label = "Sincronizar CW"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        obj = context.active_object
        if not obj:
            self.report({'WARNING'}, "Selecione um objeto")
            return {'CANCELLED'}

        try:
            # Posição
            p_str = context.scene.cw_pos_str.replace(" ", "")
            if p_str:
                p = [float(x) for x in p_str.split(',')]
                if len(p) == 3:
                    obj.location = Vector(p)

            # Rotação (XYZW) -> Blender (WXYZ) com W * -1
            r_str = context.scene.cw_rot_str.replace(" ", "")
            if r_str:
                r = [float(x) for x in r_str.split(',')]
                if len(r) == 4:
                    # Inversão do W solicitada: (W*-1, X, Y, Z)
                    quat = Quaternion((r[3] * -1, r[0], r[1], r[2]))
                    obj.rotation_mode = 'XYZ'
                    obj.rotation_euler = quat.to_euler()
            
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Erro: {e}")
            return {'CANCELLED'}

class CW_PT_Panel(bpy.types.Panel):
    bl_label = "CodeWalker Sync"
    bl_idname = "CW_PT_sync_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Item'
    bl_parent_id = "VIEW3D_PT_transform"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        col = layout.column(align=True)
        
        col.prop(scene, "cw_pos_str", text="Pos")
        col.prop(scene, "cw_rot_str", text="Quat (XYZW)")
        layout.operator("object.cw_sync_apply", icon='IMPORT')

# --- REGISTRO SEGURO ---

def register():
    # Propriedades
    bpy.types.Scene.cw_pos_str = bpy.props.StringProperty(name="Pos String")
    bpy.types.Scene.cw_rot_str = bpy.props.StringProperty(name="Rot String")
    
    # Classes
    bpy.utils.register_class(CW_OT_ApplyTransform)
    bpy.utils.register_class(CW_PT_Panel)

def unregister():
    # Classes
    bpy.utils.unregister_class(CW_OT_ApplyTransform)
    bpy.utils.unregister_class(CW_PT_Panel)
    
    # Propriedades
    del bpy.types.Scene.cw_pos_str
    del bpy.types.Scene.cw_rot_str

if __name__ == "__main__":
    register()