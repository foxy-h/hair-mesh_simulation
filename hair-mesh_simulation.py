########################################################################
#                                                                      #       
#_____________CREATING A RIG AND PHYSICS SIMULATION____________________#
#                                                                      #
#                                                                      #
########################################################################


# Blender build: 2.93.6
# PYTHON INTERACTIVE CONSOLE 3.9.2 (default, Mar  1 2021, 08:18:55) [MSC v.1916 64 bit (AMD64)]

# Up to here, the script is a easy way to generate a rig, which will be
# damped tracked to the single vertices of the Hair_Sim_Mesh.
# The constraint is layed ontop of the SIM.bones (Bone Layer 1)
# All SIM.bones are parented and connected to the previous SIM.bone
# The SIM.bone.000 ist parented (not connected) to the MAIN_CNTRL.bone.000

# A second, identical strand of CNTRL.bones (Bone Layer 2) is created
# Every CNTRL.bone is parented to its corresponding SIM.bone (means the same place/endnumber)



##### NEEDS OPTIMIZATION #####
# - the MAIN_CNTRL.bone is currently created in the "create_SIM_bones"-function.
# - so far, only one mesh object must be active, no selected
# - the mesh object should be just one vertex strand



import bpy, bmesh #first import bpy and bmesh

obj = bpy.context.active_object
obj_data = bpy.data.objects

def main():
    
    print("Start")
    print(bpy.context.active_object)
    print(bpy.context.selected_objects)

    ##### CHECKING if an Object is selected
    if len(bpy.context.selected_objects) == 1:
        print("Object found.")


####### TO-Do: Check if Mesh is the active object ########


#### GET Vertex Locations
        
        vertex_loc = get_vertex_loc()
        print("Location of Vertices:\n", vertex_loc)

        
#### CREATE Vertex Group "Pinning" for Cloth Simulation
#        
#        group = obj.vertex_groups.new(name = 'pinning')
#        for i in range(0,20):
#            group.add([i], 1.0-(i/20), 'ADD')
#        print("Vertex Group Creation 'Cloth Sim' successfull.")
#____________________________________________________________________________#

#### CREATE Vertex Group "Goal" for Soft Body Simulation
        
        goal_gradient = 50        
        group = obj.vertex_groups.new(name = 'Goal')
        for i in range(0, goal_gradient):
            group.add([i], 1.0-(i/goal_gradient), 'ADD')
        print("\nVertex Group Creation 'Soft Body Sim' successfull.\n")

#### CREATE Vertex Group "root"
         
        group = obj.vertex_groups.new(name = 'root')
        group.add([0], 1.0, 'ADD')
        print("\nVertex Group Creation 'root' successfull.\n")

#### CREATE Vertex Groups for "Damping Track" Constraints
        
        if create_vertex_groups(vertex_loc) == True:
            print("\nVertex Group Creation 'Damping Track' successfull.\n")
        else:
            print("\nVertex Group Creation 'Damping Track' failed.\n") 
       
#### CAUSION:
#### After the following function, the active object is the newly created
#### Armature!
        
#### CREATE Rig
        
        if create_rig(vertex_loc) == True:
            print("\nRig Creation successfull.\n")
        else:
            print("\nRig Creation failed.\n")

        # GET a Link to the Armature Object as long as it is the active Object
        obj_armature = bpy.context.view_layer.objects.active
        print("Active Object: ", bpy.context.view_layer.objects.active.name)


#### SET Mesh Object as active Object
        bpy.context.view_layer.objects.active = obj
        print(f"\nSet '{obj.name}' Mesh to active Object.\n")



#### CREATE Vertex Group "MAIN_CNTRL.bone" for Armature Modifier
        
        main_cntrl_gradient = 100
        group = obj.vertex_groups.new(name = 'MAIN_CNTRL.bone.000')
        for i in range(0, main_cntrl_gradient):
            group.add([i], 1.0-(i/main_cntrl_gradient), 'ADD')
        print("\nVertex Group Creation 'Armature Modifier' successfull.\n") 
        
        
#### ADD Armature Modifier and make Armature Parent
        
        bpy.ops.object.modifier_add(type='ARMATURE')
        obj.modifiers["Armature"].object = obj_armature
        obj.parent = obj_armature
        
#### ADD Cloth Modifier to active Object
#        
#        bpy.ops.object.modifier_add(type='CLOTH')
#        obj.modifiers["Cloth"].settings.vertex_group_mass = 'pinning'
#____________________________________________________________________________#
 
        
#### ADD Soft Body Modifier to active Object
        
        bpy.ops.object.modifier_add(type='SOFT_BODY')
        
        # Modify some settings
#        obj.modifiers["Softbody"].settings.collision_collection = bpy.data.collections['COLLISION'] 
        obj.modifiers["Softbody"].settings.friction = 0.5
        obj.modifiers["Softbody"].settings.mass = 0.2
        obj.modifiers["Softbody"].settings.speed = 0.5
        obj.modifiers["Softbody"].point_cache.frame_end = 1000
        obj.modifiers["Softbody"].settings.vertex_group_goal = 'Goal'
        obj.modifiers["Softbody"].settings.goal_spring = 0.5
        obj.modifiers["Softbody"].settings.goal_friction = 20
        obj.modifiers["Softbody"].settings.goal_default = 0.96       
        
        
        

    # FALSE Statement if there is no active Object 
    else:
        print("\nNo active Object.\n")

####################################################


def get_vertex_loc():

    if obj.mode == 'EDIT':
        # Link to edit mode data via bmesh
        bm = bmesh.from_edit_mesh(obj.data)
        # Link to vertice data block
        vertices = bm.verts
        print("local coordinates: ", vertices)
    else:
        # Link to vertice data block
        vertices = obj.data.vertices
        print("local coordinates: ", vertices)

    # Transform local to global coordinates
    verts = [obj.matrix_world @ vert.co for vert in vertices] 
    print("global coordinates: ",verts)


    # Coordinates as tuples.
    plain_verts = [vert.to_tuple() for vert in verts]
    print("tupples: ", plain_verts)

    return plain_verts


####################################################


def create_vertex_groups(plain_verts):

    # first vertex group will be "pinning", so we need to increase i by 1
    for i in range(len(plain_verts)-1):
        i += 1
        group = obj.vertex_groups.new(name = str(i-1))
        group.add([i], 1.0, 'ADD')
    
    return True



####################################################

        
        
########################################################################
#                                                                      #       
#___________________________RIG CREATION_______________________________#
#                                                                      #
########################################################################


####### INCLUDES:

####### - MAIN_CNTRL Bone
#######     - parenting to Root Bone (Steht noch aus)
#######     - moving to Layer 0
####### - Set of Simulation Bones
#######     - parenting SIM.bone.000 to MAIN_CNTRL.bone.000
#######     - parenting and connecting to previous Bone
#######     - moving to Layer 1
####### - Set of Control Bones
#######     - parenting to corresponding SIM Bone
#######     - moving to Layer 2


def create_rig(plain_verts):
    
        
    print("\nStart Creation of Rig\n")

#### NAME of Collection
    name_collection = "Hair Rig"   
    
    # CHECK if Collection with Name already exists
    for collection in bpy.data.collections:
        print("Collections: ", collection)
        if collection == name_collection:
            collection_exists = True
            print("Found Collection")
        else:
            collection_exists = False
            print("Didn't Found Collection")
    
    # IF Collection doesn't exist, then create it
    if  collection_exists == False:
        #### CREATE Collection
        rig_collection = bpy.data.collections.new(name_collection)
        #### LINK Collection to Scene and active Collection
        bpy.context.collection.children.link(rig_collection)
        print(f"\n'{name_collection}' Collection linked to active Collection.\n")
        
    else:
        print("\nCollection already exists.\n")        
        
    
    
#### NAME of Armature
    name_armature = "hair_rig"
    #### CREATE Armature Data
    data_armature = bpy.data.armatures.new(name_armature)
    print(f"\n'{name_collection}' Armature Data created.\n")
    #### CREATE Armature Object
    obj_armature = bpy.data.objects.new(name_armature, data_armature)
    print(f"\n'{name_collection}' Object created and linked Armature Data to it.\n")
    #### LINK Armature Object to Collection
    bpy.data.collections[name_collection].objects.link(obj_armature)
    print(f"\nArmature linked to '{name_collection}' Collection.\n")
    
    
    
####### MAKE RIG THE ACTIVE OBJECT ########
    
####### TO-Do: Check if rig is the active object ########
    
    #### DESELECT active object
    obj.select_set(False)
    #### SELECT Armature Object
    obj_armature.select_set(True)
    #### SET Armature Object as active Object
    bpy.context.view_layer.objects.active = obj_armature
    print(f"\nSet '{obj_armature.name}' Armature to active Object.\n")



##### TOGGLE EDIT MODE ########
    # Needed because Bones are created in Edit Mode
    
    
    #### SET Mode of active Object to "Edit" Mode
    bpy.ops.object.mode_set(mode = 'EDIT', toggle = False)
    
    #### CHECK if Armature is in Edit Mode
    if data_armature.is_editmode == True:
  
        armature = bpy.ops.armature
        
        # Change visible Layers
        for i in range(4):
            obj_armature.data.layers[i] = True

        # Link to editing Bones in Armature Data
        armature_bones = data_armature.edit_bones
        
        
####### CREATE Simulation Bones
        
        if create_SIM_bones(plain_verts, armature_bones) is True:
            print("\nCreation and Parenting of MAIN_CNTRL Bone and Simulation Bones successfull.\n")
                
            # MOVE Simulation Bones to Layer 1
            move_bones_to_other_layer(plain_verts, armature_bones, 'SIM', 1)
            print("\nMoved Simulation Bones to Layer 1.\n")
            
        else:
            print("\nCreation of Simulation Bones failed.\n")


####### CREATE Control Bones
        
        if create_CNTRL_bones(plain_verts, armature_bones) is True:
            print("\nCreation and Parenting of Control Bones successfull.\n")
                
            # MOVE Control Bones to Layer 2
            move_bones_to_other_layer(plain_verts, armature_bones, 'CNTRL', 2)
            print("\nMoved Control Bones to Layer 2.\n")
            
        else:
            print("\nCreation of Control Bones failed.\n")    
    
        
##### MOVE MAIN_CNTRL to Layer 0
    # Instead of giving the vertex positions we give a list, cause we just have one Bone
    # and in the function, we substract the length of the vertex list by 2
        
        move_bones_to_other_layer(range(0, 3), armature_bones, 'MAIN_CNTRL', 0)
        print("\nMoved MAIN_CNTRL Bones to Layer 0.\n")    
    
    
    # If Armature is not in Edit Mode, return to Main
    else:
        print("\nArmature not in Edit Mode.\n")
        return 0



 
##### Creation of Bones finished #######
 
##### TOGGLE POSE MODE ########
    # Needed because Bone Constraints are created in Pose Mode
        
    #### SET Mode of active Object to "Pose" Mode
    bpy.ops.object.mode_set(mode = 'POSE', toggle = False)
    
    
##### CREATE Constraints of SIM.bone
    # Because first Bone is MAIN.CNTRL and the second Bone (SIM.bone.000) needs to point at Group 1
    # count of subtarget needs to be increased by 1
    
    for count in range(len(plain_verts)-2):
        
        if count < 10:
            
            armature_constraints = obj_armature.pose.bones['SIM.bone.00'+ str(count)].constraints

            armature_constraints.new('DAMPED_TRACK')
            armature_constraints['Damped Track'].target = obj
            armature_constraints['Damped Track'].subtarget = str(count+1)  
        elif count < 100:
            
            armature_constraints = obj_armature.pose.bones['SIM.bone.0'+ str(count)].constraints

            armature_constraints.new('DAMPED_TRACK')
            armature_constraints['Damped Track'].target = obj
            armature_constraints['Damped Track'].subtarget = str(count+1)             
        else:
            
            armature_constraints = obj_armature.pose.bones['SIM.bone.'+ str(count)].constraints

            armature_constraints.new('DAMPED_TRACK')
            armature_constraints['Damped Track'].target = obj
            armature_constraints['Damped Track'].subtarget = str(count+1)
        
        print(f"The {count +1} Constraint is created.")
    
    print(f"\nConstraints Creation successfull.\n")

##### TOGGLE OBJECT MODE ######
    # Rig is completly created    
    # Set Mode of active Object to "Object" Mode
    bpy.ops.object.mode_set(mode = 'OBJECT', toggle = False)
    
    return True





########################################################################
#                                                                      #       
#___________________SIMULATION BONES CREATION__________________________#
#                                                                      #
########################################################################


####### INCLUDES Creating:

####### - MAIN_CNTRL.bone
####### - Set of Simulation Bones
#######     - parenting SIM.bone.000 to MAIN_CNTRL.bone.000
#######     - parenting and connecting to previous Bone

        
def create_SIM_bones(plain_verts, armature_bones):

    # First Bone will be MAIN_CNTRL
    bone = armature_bones.new("MAIN_CNTRL.bone.000")
    bone.head = (plain_verts[0])
    bone.tail = (plain_verts[1])
    
    # First Bone is MAIN_CNTRL, so we must begin at the 2nd Vertex
    for vert in range(len(plain_verts)-2):
        
        vert += 1
        # Create new Simulation Bone
        bone = armature_bones.new("SIM.bone.000")
        # Set Head of new Bone to 'n'. Vertice Position
        bone.head = (plain_verts[vert])
        # Set Head of new Bone to 'n+1'. Vertice Position
        bone.tail = (plain_verts[vert+1])
        
        print(f"created {vert} Simulation Bone")

    print(f"\n{vert+1} Simulation Bones Created.\n")
    
    #### PARENT 1st Simulation Bone to MAIN Control
    armature_bones['SIM.bone.000'].parent = armature_bones['MAIN_CNTRL.bone.000']
    
    
    #### PARENT every Bone to it's previous Bone
    for count in range(len(plain_verts)-3):
        count += 1
        
        # Name needs to be changed cause of count
        if count < 10:
            armature_bones['SIM.bone.00'+ str(count)].parent = armature_bones['SIM.bone.00'+str(count-1)]
            # Connect Bone to it's parent
            armature_bones['SIM.bone.00'+ str(count)].use_connect = True                
        
        # count = 10
        elif count == 10:
            armature_bones['SIM.bone.0'+ str(count)].parent = armature_bones['SIM.bone.00'+str(count-1)]
            # Connect Bone to it's parent
            armature_bones['SIM.bone.0'+ str(count)].use_connect = True
        
        # count <100
        elif count < 100:
            armature_bones['SIM.bone.0'+ str(count)].parent = armature_bones['SIM.bone.0'+str(count-1)]
            # Connect Bone to it's parent
            armature_bones['SIM.bone.0'+ str(count)].use_connect = True
        
        # count = 100
        elif count == 100:
            armature_bones['SIM.bone.'+ str(count)].parent = armature_bones['SIM.bone.0'+str(count-1)]
            # Connect Bone to it's parent
            armature_bones['SIM.bone.'+ str(count)].use_connect = True
        
        # count >100
        else:
            armature_bones['SIM.bone.'+ str(count)].parent = armature_bones['SIM.bone.'+str(count-1)]
            # Connect Bone to it's parent
            armature_bones['SIM.bone.'+ str(count)].use_connect = True  
        
            
        print(f"Simulation Bone {count} is parented to Simulation Bone {count-1}")
    
    return True


########################################################################
#                                                                      #       
#_____________________CONTROL BONES CREATION___________________________#
#                                                                      #
########################################################################


####### INCLUDES Creating:

####### - Set of Control Bones
#######     - parenting to corresponding SIM Bone
        
        
def create_CNTRL_bones(plain_verts, armature_bones):

    # First Bone is MAIN_CNTRL, so we must begin at the 2nd Vertex
    for vert in range(len(plain_verts)-2):
        
        vert += 1
        # Create new Bone
        bone = armature_bones.new("CNTRL.bone.000")
        # Set Head of new Bone to 'n'. Vertice Position
        bone.head = (plain_verts[vert])
        # Set Tail of new Bone to 'n+1'. Vertice Position
        bone.tail = (plain_verts[vert+1])
        
        print(f"created {vert} Control Bone")
    
    print(f"\n{vert+1} Control Bones Created.\n")

    # PARENT every Bone to it's corresponding SIM.bone
    for count in range(len(plain_verts)-2):
        
        # Name needs to be changed cause of count
        if count < 10:
            armature_bones['CNTRL.bone.00'+ str(count)].parent = armature_bones['SIM.bone.00'+str(count)]
        
        # count < 100
        elif count < 100:
            armature_bones['CNTRL.bone.0'+ str(count)].parent = armature_bones['SIM.bone.0'+str(count)]
        
        # count >= 100
        else:
            armature_bones['CNTRL.bone.'+ str(count)].parent = armature_bones['SIM.bone.'+str(count)]
        
        print(f"Control Bone {count} is parented to Simulation Bone {count}")
        
        count += 1
    
    return True
      

########################################################################
#                                                                      #       
#_______________________MOVING BONES TO LAYER__________________________#
#                                                                      #
########################################################################


####### INCLUDES:

####### - Move Bones with certain Name to other Layer
####### - Layer Number is defined by function Input 



def move_bones_to_other_layer(plain_verts, armature_bones, bone_name, layer_number):
    
    
    for count in range(len(plain_verts)-2):
        for i in range(20):
            if i == layer_number:
                
                # Name needs to be changed cause of count
                if count < 10:
                    # Set defined Layer active for Bones count < 10
                    armature_bones[bone_name +'.bone.00'+ str(count)].layers[i] = True
                elif count < 100:
                    # count < 100
                    armature_bones[bone_name +'.bone.0'+ str(count)].layers[i] = True
                else:
                    # count > 100
                    armature_bones[bone_name +'.bone.'+ str(count)].layers[i] = True
            else:
                if count < 10:
                    # Set other Layers inactive for Bones count < 10
                    armature_bones[bone_name +'.bone.00'+ str(count)].layers[i] = False
                elif count < 100:
                    # count < 100
                    armature_bones[bone_name +'.bone.0'+ str(count)].layers[i] = False
                else:
                    # count > 100
                    armature_bones[bone_name +'.bone.'+ str(count)].layers[i] = False


main()
