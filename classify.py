import numpy as np


def classify(candidate_with_id, refArr):
    label = []
    candidate = []
    result = []
    for feature in candidate_with_id:
        label.append(feature[0])
        del feature[0]
        candidate.append(feature)
    i = 0
    for item in candidate:
        # print(item)
        distance_sum = 0
        distances = []
        distance_min = -1
        for ref in refArr:
            distance = np.linalg.norm(np.array(item) - np.array(ref))
            distance_sum += distance
            distances.append(distance)
            if distance_min == -1 or distance < distance_min:
                distance_min = distance
            # print(distance)
        distance_sum /= len(refArr)
        print(label[i], distance_sum, distance_min, distances)
        if (distance_min<17.5 and distance_sum < 17.5) or distance_min<16:
            result.append(label[i])
        i += 1
    print(result)
    return result

def classify_example(id):
    refArr = []
    candidate = []
    label = []
    with open("reference.txt",'r') as ref_file:
        for line in ref_file.readlines():
            ref_feature = line.replace(',\n','').split(',')
            del(ref_feature[0])
            refArr.append([float(i) for i in ref_feature])
    with open("result.txt",'r') as results:
        for line in results.readlines():
            if 'crop/%05d' % id in line:
                arr_feature = line.replace(',\n','').split(',')
                label.append(arr_feature[0])
                del(arr_feature[0])
                candidate.append([float(i) for i in arr_feature])

    print("Reference Arr:")
    for i in refArr:
        print(i)
    i=0
    for item in candidate:
        #print(item)
        distance_sum = 0
        distances = []
        distance_min = -1
        for ref in refArr:
            distance = np.linalg.norm(np.array(item)-np.array(ref))
            distance_sum += distance
            distances.append(distance)
            if distance_min == -1 or distance< distance_min:
                distance_min = distance
            #print(distance)
        distance_sum /= len(refArr)
        print(label[i],distance_sum, distance_min,distances)
        i+=1
