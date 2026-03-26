bl_info = {
    "name": "Quick Move and Rotation (codewalker) - Clipboard Edition",
    "author": "lafa2k",
    "version": (1.4),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Item > Transform",
    "description": "Sincroniza Pos/Rot com correção de W e ferramentas MLO",
    "category": "Object",
}

import bpy
import bmesh
from mathutils import Vector, Quaternion

class CW_OT_ApplyTransform(bpy.types.Operator):
    """Aplica Posição e Rotação com correção de W"""
    bl_idname = "object.cw_sync_apply"
    bl_label = "Sincronizar no Blender"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        obj = context.active_object
        if not obj:
            self.report({'WARNING'}, "Selecione um objeto")
            return {'CANCELLED'}

        try:
            p_str = context.scene.cw_pos_str.replace(" ", "")
            if p_str:
                p = [float(x) for x in p_str.split(',')]
                if len(p) == 3:
                    obj.location = Vector(p)

            r_str = context.scene.cw_rot_str.replace(" ", "")
            if r_str:
                r = [float(x) for x in r_str.split(',')]
                if len(r) == 4:
                    quat = Quaternion((r[3] * -1, r[0], r[1], r[2]))
                    obj.rotation_mode = 'QUATERNION'
                    obj.rotation_quaternion = quat
            
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Erro: {e}")
            return {'CANCELLED'}

class CW_OT_CopyPos(bpy.types.Operator):
    """Copia a posição para o clipboard"""
    bl_idname = "object.cw_copy_pos"
    bl_label = "Copy Coord"
    
    def execute(self, context):
        obj = context.active_object
        if obj:
            loc = obj.location
            pos_text = f"{loc.x:.8f}, {loc.y:.8f}, {loc.z:.8f}"
            context.scene.cw_pos_str = pos_text
            context.window_manager.clipboard = pos_text
            self.report({'INFO'}, "Posição copiada!")
        return {'FINISHED'}

class CW_OT_CopyRot(bpy.types.Operator):
    """Copia a rotação (XYZW com W*-1) para o clipboard"""
    bl_idname = "object.cw_copy_rot"
    bl_label = "Copy Rotation"
    
    def execute(self, context):
        obj = context.active_object
        if obj:
            q = obj.rotation_euler.to_quaternion() if obj.rotation_mode != 'QUATERNION' else obj.rotation_quaternion
            rot_text = f"{q.x:.8f}, {q.y:.8f}, {q.z:.8f}, {q.w * -1:.8f}"
            context.scene.cw_rot_str = rot_text
            context.window_manager.clipboard = rot_text
            self.report({'INFO'}, "Rotação copiada!")
        return {'FINISHED'}

class MLO_OT_CopyVertexPos(bpy.types.Operator):
    """Pega a coordenada global do vértice selecionado"""
    bl_idname = "object.mlo_copy_vertex"
    bl_label = "Get/Copy Vertex Pos"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        obj = context.edit_object or context.active_object
        if obj.mode != 'EDIT':
            self.report({'WARNING'}, "Precisa estar no EDIT MODE")
            return {'CANCELLED'}
        
        bm = bmesh.from_edit_mesh(obj.data)
        selected_verts = [v for v in bm.verts if v.select]
        
        if selected_verts:
            v = selected_verts[-1]
            world_pos = obj.matrix_world @ v.co
            pos_text = f"{world_pos.x:.8f}, {world_pos.y:.8f}, {world_pos.z:.8f}"
            
            context.scene.mlo_vert_str = pos_text
            context.window_manager.clipboard = pos_text
            self.report({'INFO'}, "Coordenada do Vértice Copiada!")
        else:
            self.report({'WARNING'}, "Nenhum vértice selecionado")
            
        return {'FINISHED'}

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
        
        # --- Grupo Principal ---
        col = layout.column(align=True)
        col.prop(scene, "cw_pos_str", text="Pos")
        col.prop(scene, "cw_rot_str", text="Quat (XYZW)")
        col.operator("object.cw_sync_apply", icon='IMPORT')
        
        row = layout.row(align=True)
        row.operator("object.cw_copy_pos", icon='COPY_ID')
        row.operator("object.cw_copy_rot", icon='COPY_ID')
        
        # --- Grupo MLO TOOLS ---
        # Removi a 'box' para evitar conflito de desenho no painel lateral
        layout.separator()
        layout.label(text="MLO TOOLS", icon='TOOL_SETTINGS')
        
        mlo_col = layout.column(align=True)
        mlo_col.prop(scene, "mlo_vert_str", text="")
        # Só habilita o botão se estiver no modo de edição
        mlo_col.enabled = (context.mode == 'EDIT_MESH')
        mlo_col.operator("object.mlo_copy_vertex", icon='VERTEXSEL')

# --- REGISTRO ---

classes = (
    CW_OT_ApplyTransform,
    CW_OT_CopyPos,
    CW_OT_CopyRot,
    MLO_OT_CopyVertexPos,
    CW_PT_Panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.cw_pos_str = bpy.props.StringProperty(name="Pos String")
    bpy.types.Scene.cw_rot_str = bpy.props.StringProperty(name="Rot String")
    bpy.types.Scene.mlo_vert_str = bpy.props.StringProperty(name="Vertex String")

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.cw_pos_str
    del bpy.types.Scene.cw_rot_str
    del bpy.types.Scene.mlo_vert_str

if __name__ == "__main__":
    register()