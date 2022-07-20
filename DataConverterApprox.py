# No external module is used in this program

########################################
## Initialization with file name input
########################################

print(' __________________________________________________')
print('|                                                  |')
print('|   This is a ".funscript" to ".txt" converter.    |')
print('|__________________________________________________|\n')
print('Enter file name (without extention): ')
filename = input()
filekey = 1
''' This is a section that enables .csv 
    filekey = 2 will make a csv file.
while (1):
    print('Enter 1 for .txt and 2 for .csv')
    filekey = int(input())
    if (filekey == 1) or (filekey == 2):
        break
    else:
        print('Invalid entry!\n')
    '''
data = open(filename+'.funscript','r+')

print('\nWorking... please wait...\n')



#######################################
#######  Data storage initiated  #####
#######################################

t_time = []
p_pos = []

#######################
#  TimeStamp Recording
#######################

def t_time_func(data, iter):
    data.seek(iter)
    prefix = data.read(5)
    value = 0
    diff = 0
    flag = 0
    if (prefix == '"at":'):
        t1=data.tell()
        while (data.read(1)!=','):
            pass
        t2=data.tell()-1
        diff = t2 - t1
        data.seek(t1)
        value = data.read(diff)
        flag = 1
    return value, flag, diff

iteration = 0
data.seek(0)
temp = data.read(1)
while (temp!="]"):
    t_value, t_flag, jump = t_time_func(data,iteration)
    if (t_flag):
        t_time.append(t_value)
        iteration += jump
    else:
        iteration += 1
    data.seek(iteration)
    temp = data.read(1)

print("Timeline extracted...")

#########################
#  Position Recording
#########################

def p_pos_func(data, iter):
    data.seek(iter)
    prefix = data.read(6)
    value = 0
    diff = 0
    flag = 0
    if (prefix == '"pos":'):
        t1=data.tell()
        while (data.read(1)!='}'):
            pass
        t2=data.tell()-1
        diff = t2 - t1
        data.seek(t1)
        value = data.read(diff)
        flag = 1
    return value, flag, diff

iteration = 0
data.seek(0)
temp = data.read(1)
while (temp!="]"):
    p_value, p_flag, jump = p_pos_func(data,iteration)
    if (p_flag):
        p_pos.append(p_value)
        iteration += jump
    else:
        iteration += 1
    data.seek(iteration)
    temp = data.read(1)

data.close()

print("Positional data extracted...")

#############################################
# Timing compensation
# round off every input to 0.1 sec precision
#############################################

count = 0
for item in t_time:
    count+=1

it = 0
while it < count:
    t_time[it] = int(int(t_time[it])/10) # (/10) = rounded up to .01 sec only 
    it+=1
it=0
while it < count-1:
    if t_time[it] == t_time[it+1]:
        del t_time[it]
        del p_pos[it]
        it-=2
        count-=1
    it+=1
it = 0
while it<count:
    t_time[it] = str(t_time[it])
    it+=1

print("Removing unnecessary data...")


########################################
##   Add missing sections (with curves)
########################################

def fillup(time, position):  #function to fill the whole timeline
    counter = 0
    for item in time:
        counter += 1

    iteration = 0
    while iteration < counter:     # just fill up the whole timeline
        if int(time[iteration])!=iteration:
            time.insert(iteration,str(iteration))
            position.insert(iteration, str(222))
            counter += 1
        iteration += 1
        
fillup(t_time,p_pos)

def curver(position):
    counter = 0
    for item in position:
        counter += 1
    
    position[0]='0'  #fixing first and last position
    position[-1]='100'

    iteration = 0
    while iteration < counter:
        ct = 0
        if position[iteration]=='222':
            while position[iteration+ct]=='222':
                ct+=1
            aval = int(position[iteration-1])
            bval = int(position[iteration+ct])
            if aval==bval:
                for x in range(ct):
                    position[iteration+x]=position[iteration+-1]
            elif aval>bval:
                for x in range(ct):
                    val = int(((ct-x)/(ct+1))*aval)
                    position[iteration+x]=str(val)
            elif aval<bval:
                for x in range(ct):
                    val = int(((x+1)/(ct+1))*bval)
                    position[iteration+x]=str(val)
        iteration += 1

curver(p_pos)


print("Filled up and curved...")

######################################
##   Writing to file takes place here
######################################

if filekey == 1:
    # Creating and writing the Modified data
    data3 = open(filename+'_modified.txt', 'w+')

    count = 0
    for item in p_pos:
        count+=1
    iter = 0
    while iter < count-1:
        data3.write(t_time[iter]+' '+p_pos[iter]+'\n')
        iter +=1
    data3.write(t_time[iter]+' '+p_pos[iter])

    data3.close()
else:
    # Creating and writing the Modified data
    data3 = open(filename+'_modified.csv', 'w+')

    count = 0
    for item in p_pos:
        count+=1
    iter = 0
    while iter < count-1:
        data3.write(t_time[iter]+','+p_pos[iter]+'\n')
        iter +=1
    data3.write(t_time[iter]+','+p_pos[iter])

    data3.close()

print('Completed: Data written in '+filename+'.txt')