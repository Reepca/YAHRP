# Author: Joel and Caleb

# Imports:
import collada
import pyglet
from pyglet.gl import *
import ctypes
import glutils
from glutils import VecF

# Shader
######################################################################
# Phong with textures
texturePhong = (['''
varying vec3 normal, lightDir0, eyeVec;

void main()
{
	normal = gl_NormalMatrix * gl_Normal;

	vec3 vVertex = vec3(gl_ModelViewMatrix * gl_Vertex);

	lightDir0 = vec3(gl_LightSource[0].position.xyz - vVertex);
	eyeVec = -vVertex;

	gl_Position = ftransform();
        gl_TexCoord[0]  = gl_TextureMatrix[0] * gl_MultiTexCoord0;
}
'''], 
['''
varying vec3 normal, lightDir0, eyeVec;
uniform sampler2D my_color_texture[1]; //0 = ColorMap

void main (void)
{
        vec4 texColor = texture2D(my_color_texture[0], gl_TexCoord[0].st);
	vec4 final_color;

/*	final_color = (gl_FrontLightModelProduct.sceneColor * vec4(texColor.rgb,1.0)) +
		      gl_LightSource[0].ambient * vec4(texColor.rgb,1.0);*/
	final_color = (gl_FrontLightModelProduct.sceneColor * vec4(texColor.rgb,1.0)) + 
		       vec4(texColor.rgb,1.0);

	vec3 N = normalize(normal);
	vec3 L0 = normalize(lightDir0);

	float lambertTerm0 = dot(N,L0);

	if(lambertTerm0 > 0.0)
	{
		final_color += gl_LightSource[0].diffuse *
		               gl_FrontMaterial.diffuse *
					   lambertTerm0;

		vec3 E = normalize(eyeVec);
		vec3 R = reflect(-L0, N);
		float specular = pow( max(dot(R, E), 0.0),
		                 gl_FrontMaterial.shininess );
		final_color += gl_LightSource[0].specular *
		               gl_FrontMaterial.specular *
					   specular;
	}
	gl_FragColor = final_color;
}
'''])

class Shader:
	# vert, frag and geom take arrays of source strings
	# the arrays will be concattenated into one string by OpenGL
	def __init__(self, vert = [], frag = [], geom = []):
		# create the program handle
		self.handle = glCreateProgram()
		# we are not linked yet
		self.linked = False

		# create the vertex shader
		self.createShader(vert, GL_VERTEX_SHADER)
		# create the fragment shader
		self.createShader(frag, GL_FRAGMENT_SHADER)
		# the geometry shader will be the same, once pyglet supports the extension
		# self.createShader(frag, GL_GEOMETRY_SHADER_EXT)

		# attempt to link the program
		self.link()

	def createShader(self, strings, type):
		count = len(strings)
		# if we have no source code, ignore this shader
		if count < 1:
			return

		# create the shader handle
		shader = glCreateShader(type)

		# convert the source strings into a ctypes pointer-to-char array, and upload them
		# this is deep, dark, dangerous black magick - don't try stuff like this at home!
		src = (ctypes.c_char_p * count)(*strings)
		glShaderSource(shader, count, ctypes.cast(ctypes.pointer(src),
			       ctypes.POINTER(ctypes.POINTER(ctypes.c_char))), None)

		# compile the shader
		glCompileShader(shader)

		temp = ctypes.c_int(0)
		# retrieve the compile status
		glGetShaderiv(shader, GL_COMPILE_STATUS, ctypes.byref(temp))

		# if compilation failed, print the log
		if not temp:
			# retrieve the log length
			glGetShaderiv(shader, GL_INFO_LOG_LENGTH, ctypes.byref(temp))
			# create a buffer for the log
			buffer = ctypes.create_string_buffer(temp.value)
			# retrieve the log text
			glGetShaderInfoLog(shader, temp, None, buffer)
			# print the log to the console
			print buffer.value
		else:
			# all is well, so attach the shader to the program
			glAttachShader(self.handle, shader);

	def link(self):
		# link the program
		glLinkProgram(self.handle)

		temp = ctypes.c_int(0)
		# retrieve the link status
		glGetProgramiv(self.handle, GL_LINK_STATUS, ctypes.byref(temp))

		# if linking failed, print the log
		if not temp:
			#	retrieve the log length
			glGetProgramiv(self.handle, GL_INFO_LOG_LENGTH, ctypes.byref(temp))
			# create a buffer for the log
			buffer = create_string_buffer(temp.value)
			# retrieve the log text
			glGetProgramInfoLog(self.handle, temp, None, buffer)
			# print the log to the console
			print buffer.value
		else:
			# all is well, so we are linked
			self.linked = True

	def bind(self):
		# bind the program
		glUseProgram(self.handle)

	def unbind(self):
		# unbind whatever program is currently bound - not necessarily this program,
		# so this should probably be a class method instead
		glUseProgram(0)

	# upload a floating point uniform
	# this program must be currently bound
	def uniformf(self, name, *vals):
		# check there are 1-4 values
		if len(vals) in range(1, 5):
			# select the correct function
			{ 1 : glUniform1f,
				2 : glUniform2f,
				3 : glUniform3f,
				4 : glUniform4f
				# retrieve the uniform location, and set
			}[len(vals)](glGetUniformLocation(self.handle, name), *vals)

	# upload an integer uniform
	# this program must be currently bound
	def uniformi(self, name, *vals):
		# check there are 1-4 values
		if len(vals) in range(1, 5):
			# select the correct function
			{ 1 : glUniform1i,
				2 : glUniform2i,
				3 : glUniform3i,
				4 : glUniform4i
				# retrieve the uniform location, and set
			}[len(vals)](glGetUniformLocation(self.handle, name), *vals)

	# upload a uniform matrix
	# works with matrices stored as lists,
	# as well as euclid matrices
	def uniform_matrixf(self, name, mat):
		# obtian the uniform location
		loc = glGetUniformLocation(self.Handle, name)
		# uplaod the 4x4 floating point matrix
		glUniformMatrix4fv(loc, 1, False, (c_float * 16)(*mat))


class GLSLRenderer: 

    def __init__(self, dae):
        self.dae = dae
        # To calculate model boundary along Z axis
        self.z_max = -100000.0
        self.z_min = 100000.0
        self.textures = {}
        self.shaders = {}
        self.batch_list = []

        # Initialize OpenGL
        glClearColor(0.0, 0.0, 0.0, 0.5) # Black Background
        glEnable(GL_DEPTH_TEST) # Enables Depth Testing
        glEnable(GL_CULL_FACE)
        glEnable(GL_MULTISAMPLE);

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glEnable(GL_LIGHTING)

        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_AMBIENT, VecF(0.9, 0.9, 0.9, 1.0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, VecF(1.0, 1.0, 1.0, 1.0))
        glLightfv(GL_LIGHT0, GL_SPECULAR, VecF(0.3, 0.3, 0.3, 1.0))

        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, VecF(0.1, 0.1, 0.1, 1.0))
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, VecF(0.1, 0.1, 0.1, 1.0))
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 50)

        print('Running with OpenGL version:', glutils.getOpenGLVersion())
        print('Initializing shaders...')
        (vert, frag) = shaders.texturePhong
        prog = Shader(vert, frag)
        self.shaders['texture'] = prog
        print('  texture')
        print('  done.')
###########################################JOEL GOT TO HERE RESTRUCTUING FOR PERSONAL PROFIT###########################################
        print('Creating GL buffer objects for geometry...')
        if self.dae.scene is not None:
            for geom in self.dae.scene.objects('geometry'):
                for prim in geom.primitives():
                    mat = prim.material
                    diff_color = VecF(0.3,0.3,0.3,1.0)
                    spec_color = None 
                    shininess = None
                    amb_color = None
                    tex_id = None
                    shader_prog = self.shaders[mat.effect.shadingtype]
                    for prop in mat.effect.supported:
                        value = getattr(mat.effect, prop)
                        # it can be a float, a color (tuple) or a Map
                        # ( a texture )
                        if isinstance(value, collada.material.Map):
                            colladaimage = value.sampler.surface.image

                            # Accessing this attribute forces the
                            # loading of the image using PIL if
                            # available. Unless it is already loaded.
                            img = colladaimage.pilimage
                            if img: # can read and PIL available
                                shader_prog = self.shaders['texture']
                                # See if we already have texture for this image
                                if self.textures.has_key(colladaimage.id):
                                    tex_id = self.textures[colladaimage.id]
                                else:
                                    # If not - create new texture
                                    try:
                                        # get image meta-data
                                        # (dimensions) and data
                                        (ix, iy, tex_data) = (img.size[0], img.size[1], img.tostring("raw", "RGBA", 0, -1))
                                    except SystemError:
                                        # has no alpha channel,
                                        # synthesize one
                                        (ix, iy, tex_data) = (img.size[0], img.size[1], img.tostring("raw", "RGBX", 0, -1))
                                    # generate a texture ID
                                    tid = GLuint()
                                    glGenTextures(1, ctypes.byref(tid))
                                    tex_id = tid.value
                                    # make it current
                                    glBindTexture(GL_TEXTURE_2D, tex_id)
                                    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
                                    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
                                    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
                                    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
                                    # copy the texture into the
                                    # current texture ID
                                    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, tex_data)

                                    self.textures[colladaimage.id] = tex_id
                            else:
                                print '  %s = Texture %s: (not available)'%(
                                    prop, colladaimage.id)
                        else:
                            if prop == 'diffuse' and value is not None:
                                diff_color = value
                            elif prop == 'specular' and value is not None:
                                spec_color = value
                            elif prop == 'ambient' and value is not None:
                                amb_color = value
                            elif prop == 'shininess' and value is not None:
                                shininess = value

                    # use primitive-specific ways to get triangles
                    prim_type = type(prim).__name__
                    if prim_type == 'BoundTriangleSet':
                        triangles = prim
                    elif prim_type == 'BoundPolylist':
                        triangles = prim.triangleset()
                    else:
                        print 'Unsupported mesh used:', prim_type
                        triangles = None

                    if triangles is not None:
                        triangles.generateNormals()
                        # We will need flat lists for VBO (batch) initialization
                        vertices = triangles.vertex.flatten().tolist()
                        batch_len = len(vertices)//3
                        indices = triangles.vertex_index.flatten().tolist()
                        normals = triangles.normal.flatten().tolist()

                        batch = pyglet.graphics.Batch()

                        # Track maximum and minimum Z coordinates
                        # (every third element) in the flattened
                        # vertex list
                        ma = max(vertices[2::3])
                        if ma > self.z_max:
                            self.z_max = ma

                        mi = min(vertices[2::3])
                        if mi < self.z_min:
                            self.z_min = mi

                        if tex_id is not None:

                            # This is probably the most inefficient
                            # way to get correct texture coordinate
                            # list (uv). I am sure that I just do not
                            # understand enough how texture
                            # coordinates and corresponding indexes
                            # are related to the vertices and vertex
                            # indicies here, but this is what I found
                            # to work. Feel free to improve the way
                            # texture coordinates (uv) are collected
                            # for batch.add_indexed() invocation.
                            uv = [[0.0,0.0]] * batch_len
                            for t in triangles:
                                nidx = 0
                                texcoords = t.texcoords[0]
                                for vidx in t.indices:
                                    uv[vidx] = texcoords[nidx].tolist()
                                    nidx += 1
                            # Flatten the uv list
                            uv = [item for sublist in uv for item in sublist]

                            # Create textured batch
                            batch.add_indexed(batch_len, 
                                              GL_TRIANGLES,
                                              None,
                                              indices,
                                              ('v3f/static', vertices),
                                              ('n3f/static', normals),
                                              ('t2f/static', uv))
                        else:
                            # Create colored batch
                            batch.add_indexed(batch_len, 
                                              GL_TRIANGLES,
                                              None,
                                              indices,
                                              ('v3f/static', vertices),
                                              ('n3f/static', normals))

                        # Append the batch with supplimentary
                        # information to the batch list
                        self.batch_list.append(
                            (batch, shader_prog, tex_id, diff_color, 
                             spec_color, amb_color, shininess))
        print 'done. Ready to render.'

    def render(self, rotate_x, rotate_y, rotate_z):
        """Render batches created during class initialization"""

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        # Place the light far behind our object
        z_offset = self.z_min - (self.z_max - self.z_min) * 3
        light_pos = VecF(100.0, 100.0, 10.0 * -z_offset)
        glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
        
        # Move the object deeper to the screen and rotate
        glTranslatef(0, 0, z_offset)
        glRotatef(rotate_x, 1.0, 0.0, 0.0)
        glRotatef(rotate_y, 0.0, 1.0, 0.0)
        glRotatef(rotate_z, 0.0, 0.0, 1.0)

        prev_shader_prog = None
        # Draw batches (VBOs)
        for (batch, shader_prog, tex_id, diff_color, spec_color, amb_color, shininess) in self.batch_list:
            # Optimization to not make unnecessary bind/unbind for the
            # shader. Most of the time there will be same shaders for
            # geometries.
            if shader_prog != prev_shader_prog:
                if prev_shader_prog is not None:
                    prev_shader_prog.unbind()
                prev_shader_prog = shader_prog
                shader_prog.bind()

            if diff_color is not None:
                shader_prog.uniformf('diffuse', *diff_color)
            if spec_color is not None:
                shader_prog.uniformf('specular', *spec_color)
            if amb_color is not None:
                shader_prog.uniformf('ambient', *amb_color)
            if shininess is not None:
                shader_prog.uniformf('shininess', shininess)

            if tex_id is not None:
                # We assume that the shader here is 'texture'
                glActiveTexture(GL_TEXTURE0)
                glEnable(GL_TEXTURE_2D)
                glBindTexture(GL_TEXTURE_2D, tex_id)
                shader_prog.uniformi('my_color_texture[0]', 0)

            batch.draw()
        if prev_shader_prog is not None:
            prev_shader_prog.unbind()


    def cleanup(self):
        print 'Renderer cleaning up'