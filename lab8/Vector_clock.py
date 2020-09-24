from multiprocessing import Process, Pipe, Manager


# shared variable
res = Manager().dict()

# vector clock
vector1 = [0,0,0]
vector2 = [0,0,0]
vector3 = [0,0,0]


def event(pid, vector):
    vector[pid-1] += 1
    print('Something happened in process ', pid, ', process vector: ', vector)
    return vector

def send_message(pipe, sender, s_vector):
    s_vector[sender-1] += 1
    pipe.send((sender, s_vector))
    print('Message sent from ', sender, ', vector: ', s_vector)
    return s_vector

def recv_message(pipe, receiver, r_vector):
    r_vector[receiver-1] += 1

    id, vector = pipe.recv()
    for i in range (0, len(vector)):
        if i != (receiver-1):
            r_vector[i] += vector[i]
    print('Message received at ', receiver, ', vector: ', r_vector)
    return r_vector

# process creation
def process_one(pipe12, res):
    pid = 1
    global vector1
    vector1 = send_message(pipe12, pid, vector1)
    vector1 = send_message(pipe12, pid, vector1)
    vector1 = event(pid, vector1)
    vector1 = recv_message(pipe12, pid, vector1)
    vector1  = event(pid, vector1)
    vector1  = event(pid, vector1)
    vector1 = recv_message(pipe12, pid, vector1)
    res[0] = vector1
    # print('Process 1: ', vector1)

def process_two(pipe21, pipe23, res):
    pid = 2
    global vector2
    vector2 = recv_message(pipe21, pid, vector2)
    vector2 = recv_message(pipe21, pid, vector2)
    vector2 = send_message(pipe21, pid, vector2)
    vector2 = recv_message(pipe23, pid, vector2)
    vector2 = event(pid, vector2)
    vector2 = send_message(pipe21, pid, vector2)
    vector2 = send_message(pipe23, pid, vector2)
    vector2 = send_message(pipe23, pid, vector2)
    res[1] = vector2
    # print('Process 2: ', vector2)


def process_three(pipe32, res):
    pid = 3
    global vector3
    vector3 = send_message(pipe32, pid, vector3)
    vector3 = recv_message(pipe32, pid, vector3)
    vector3 = event(pid, vector3)
    vector3 = recv_message(pipe32, pid, vector3)
    res[2] = vector3
    # print('Process 3: ', vector3)


# pipe creation
oneandtwo, twoandone = Pipe()
twoandthree, threeandtwo = Pipe()

process1 = Process(target=process_one,
                   args=(oneandtwo,res))
process2 = Process(target=process_two,
                   args=(twoandone, twoandthree,res))
process3 = Process(target=process_three,
                   args=(threeandtwo,res))

process1.start()
process2.start()
process3.start()

process1.join()
process2.join()
process3.join()
print('\nFinal state: ')
print('Process 1: ', res[0])
print('Process 2: ', res[1])
print('Process 3: ', res[2])
