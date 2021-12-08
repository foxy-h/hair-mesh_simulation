# hair-mesh_simulation

What is it for?

This is a script which provides a fast and easy solution for creating a rig, which is following a strand of vertices.
Later the vertex strand gets a soft body physics modifier.
To follow the vertex strand, every vertex is assigned to a vertex group (number 0 to inf)
Also there is a "Goal" and a "MAIN_CNTRL.bone.000" vertex group created. The vertex value decreases linear from the root to tip.
The first vertex in the vertex strand becomes the root. 
The second vertex is assigned to group "0", the third to group "1" and so on.

How is the rig builded?

First, we get the vertex locations of the mesh.
Then, between the first and second vertex a "MAIN_CNTRL.bone.000" is created. 
Between the second and third vertex a "SIM.bone.000" is created, between the third and fourth a "SIM.bone.001" and so on.
A second bone strand with the name "CNTRL.bones" is created and parented to the SIM.bones. Now, we can weight paint a second mesh to the CNTRL.bones.

What are the limitations so far?

So far, the script works fine, if you have 1 selected mesh, which consists of a vertex strand (see the blend-file attached). If multiple objects are selected, the script will raise no Error, but nothing happens.
Also, unfortunately the collection checker doesn't work. The newly generated rig is moved in the correct collection, but also another collection is created with the regex ".001". 
The cool thing so far is, that you can apply the script on multiple mesh objects (not after another! Not at the same time!) and the newly generated rig just counts up.
BUT so far, it is not possible to merge the mesh strands and rigs to one, because the vertex groups for the damped track are always named 0 to inf, so the groups are merged together as soon as the meshes are merged together.





So far, I created functions for the following Operations:
- main(): main function.
	 - check if there is an active object
	 - call "get_vertex_loc()" and saves it in variable
	 - create vertex group "Goal"
	 - create vertex group "root"
	 - call "create_vertex_groups(plain_verts)"
	 - call "create_rig(plain_verts)"
	 - set mesh object as active object (because after calling create_rig, the new rig is the active object)
	 - create vertex group "MAIN_CNTRL.bone.000"
	 - add "Armature" Modifier
	 - add "Soft Body" Modifier
				
- get_vertex_loc(): allows us to get the location of the vertices of the mesh. Returns the vertex coordinates in form of tuples. (variable = plain_verts)

- create_vertex_groups(plain_verts): creates vertex groups 0 to inf.The second vertex will be assigned to group 0. It needs as attribute the vertex coordinates in tuple form(for range()). Returns "True" when finished.

- create_rig(plain_verts): creates the rig. Needs as attribute the vertex coordinates in tuple form.
	- searches for a collection of specific name
	- if names not exist, a collection will be created and linked to active scene and collection
	- creates armature data and assign it to armature object
	- set armature to active object
	- toggle edit mode for bone creation
	- if rig in edit mode
	- make Bone Layers 0-3 visible
	- call "create_SIM_bones(plain_verts, data_armature)"
	- call "move_bones_to_other_layer(plain_verts, data_armature, "SIM", 1)"
	- call "create_CNTRL_bones(plain_verts, data_armature)"
	- call "move_bones_to_other_layer(plain_verts, data_armature, "CNTRL", 2)"
	- call "move_bones_to_other_layer(plain_verts, data_armature, "MAIN_CNTRL", 0)"
	- toggle pose mode for constraint assignment
	- create constraint "DAMPED TRACK", so the SIM.bones point to the vertex group of the former active mesh object
	- toggle object mode
	- Return True

- create_SIM_bones(plain_verts, data_armature): creates MAIN_CNTRL.bone.000 and SIM.bones + it parents and connects the SIM.bones to each other, except the SIM.bone.000. It is parented (not connected) to the MAIN_CNTRL.bone.000. Returns "True" when finished.

- create_CNTRL_bones(plain_verts, data_armature): creates CNTRL.bones + it parents the CNTRL.bones to te corresponding SIM.bones. Returns "True" when finished. 
									
- move_bones_to_other_layer(plain_verts, data_armature, bone_name, layer_number): move all bones with bone_name f.e. "SIM" (third attribute) to layer_number f.e. 1 (fourth attribute).
