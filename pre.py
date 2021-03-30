import time
import re
import numpy as np
import os
start = time.process_time()
nnode=1
nface=1

curdir=os.getcwd()
curdir=curdir.strip('convert_msh')
newdir=curdir+'inputdata'
os.chdir(newdir)#enter data directory

with open('input.txt','r') as g:#read file name and mesh type
    count=len(g.readlines())
    g.seek(0)
    for i in range(1,count+1):
        line=g.readline()
        find_1=bool(re.match('[\s]*inputpath',line))
        find_2=bool(re.match('[\s]*meshtype',line))
        if find_1 == True:
            line=line.lstrip()
            line=line.strip('inputpath = ')
            line=line.rstrip()
            filename=line.strip('\n')
            filename=filename.strip('.msh')
        if find_2 == True:
            line=line.lstrip()
            line=line.strip('meshtype = ')
            line=line.rstrip()
            cell_type=line.strip('\n')
            cell_type=int(cell_type)

if(cell_type==6):
    face_type=4
    cell_num_node=8
elif(cell_type==4):
    face_type=3
    cell_num_node=4

with open(filename+'.msh', 'r') as f:
    count = len(f.readlines())  #total number of lines in the mesh file
    f.seek(0)   #return to the top of file
    for i in range(1, count + 1):
        line = f.readline()
        find_note = bool(re.match('\(0', line))#annotation in the mesh file
        note2_re = re.compile('^\($')
        note3_re = re.compile('^\)\)$')
        find_note2 = bool(note2_re.match(line))
        find_note3 = bool(note3_re.match(line))
        find_dim = bool(re.match('\(2', line))#dimension of the mesh
        float_re = re.compile('^([-+]?([0-9]+(\.[0-9]*)?|\.[0-9]+)([eE][-+]?[0-9]+)?[\s]+){3}$')#find float(coordinate) in the file
        find_float = bool(float_re.match(line))
        find_nnode = bool(re.match('\(10',line))#total number of nodes
        if cell_type == 6:
            face_re = re.compile('^([a-f0-9]*[\s]+){6}$')#face info
        elif cell_type == 4:
            face_re = re.compile('^([a-f0-9]*[\s]+){5}$')
        find_face = bool(face_re.match(line))
        find_nface = bool(re.match('\(13',line))#total number of faces
        find_ncell = bool(re.match('\(12',line))#total number of cells

        if find_note == True or find_note2 == True or find_note3 == True:
            continue#if is annotation line, skip to read next line
        else:
            pass#if not, do nothing

        if find_dim == True:
            line=line.strip('(2')
            line=line.rstrip(')\n')
            meshdim=int(line)

        if find_float == True:
            line=line.split(' ', 2)
            for i in range(3):
                node_coor[nnode][i] = line[i]
            nnode=nnode+1

        if find_nnode == True:
            line=line.strip('(10')
            line=line.strip(' (')
            line=line.split(' ',4)
            if int(line[0],16) == 0:
                num_nodes=int(line[2],16)
            node_coor=np.zeros((num_nodes+1,3))#generate the coordinate array with num_nodes

        if find_nface == True:
            line=line.strip('(13')
            line=line.strip(' (')
            line=line.split(' ',4)
            if int(line[0],16) == 0:
                num_faces=int(line[2],16)
                face_node=np.zeros((num_faces+1,face_type+1),dtype=int)#generate the face info array with num_faces
                face_cell=np.zeros((num_faces+1,2),dtype=int)

        if find_ncell == True:
            line=line.strip('(12')
            line=line.strip(' (')
            line=line.split(' ',4)
            if int(line[0],16) == 0:
                num_cells=int(line[2],16)

        if find_face == True:
            if cell_type == 6:
                line=line.split(' ',5)
            elif cell_type == 4:
                line=line.split(' ',4)
            for i in range(1,face_type+1):
                face_node[nface][i]=int(line[i-1],16)
            face_cell[nface][0]=int(line[len(line)-2],16)
            face_cell[nface][1]=int(line[len(line)-1],16)
            nface=nface+1

newdir=curdir+'data'
os.chdir(newdir)
with open('intermediate/1.msh','w') as c:#store the modified .msh file in the intermediate directory
    print(meshdim,file=c)
    print(num_nodes,file=c)
    for i in range(1,num_nodes+1):
        print(node_coor[i][0],node_coor[i][1],node_coor[i][2],file=c)
    print(num_cells,file=c)
    print(num_faces,file=c)
    for i in range(1,num_faces+1):
        print(' '.join(map(str,face_node[i,1:])),' '.join(map(str,face_cell[i,:])),file=c)
end=time.process_time()
print(' Mesh conversion time:',end-start)