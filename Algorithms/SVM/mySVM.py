from numpy import *
from time import sleep


def loadDataSet(file_name) :
    data_mat = []
    label_mat = []
    fr = open(file_name)
    for line in fr.readlines() :
        line_arr = line.strip().split("\t")
        data_mat.append([float(line_arr[0]) , float(line_arr[1])])
        label_mat.append(float(line_arr[2]))
    return data_mat , label_mat

def selectJrand(i , m) :
    j = i
    while (i == j) :
        j = int(random.uniform(0 , m))
    return j

def clipAlpha(aj , h , l) :
    if aj > h :
        aj = h
    if l > aj :
        aj = l
    return aj

def smoSimple(data_mat_in , class_labels , c , toler , max_iter) :
    data_matrix = mat(data_mat_in)
    label_mat = mat(class_labels).transpose()
    b = 0 
    m , n = shape(data_matrix)
    alphas = mat(zeros((m , 1)))
    iter = 0
    while (iter < max_iter) :
        alpha_pairs_changed = 0
        for i in range(m) :
            fxi = float(multiply(alphas , label_mat).T * \
                    (data_matrix * data_matrix[i,:].T)) + b
            ei = fxi - float(label_mat[i])
            if ((label_mat[i] * ei < -toler) and (alphas[i] < c)) or ((label_mat[i] * ei > toler) and (alphas[i] > 0)) :
                j = selectJrand(i , m)
                fxj = float(multiply(alphas , label_mat).T * (data_matrix * data_matrix[j,:].T)) + b
                ej = fxj - float(label_mat[j])
                alphaIold = alphas[i].copy()
                alphaJold = alphas[j].copy()
                if (label_mat[i] != label_mat[j]) :
                    L = max(0 , alphas[j] - alphas[i])
                    H = min(c , c + alphas[j] - alphas[i])
                else :
                    L = max(0 , alphas[j] + alphas[i] - c)
                    H = min(c , alphas[j] + alphas[i])
                if L==H :
                    print("L==H")
                    continue
                eta = 2.0 * data_matrix[i,:] * data_matrix[j,:].T - data_matrix[i,:] * data_matrix[i,:].T - data_matrix[j,:] * data_matrix[j,:].T
                if eta >= 0 :
                    print("eta>=0")
                    continue
                alphas[j] -= label_mat[j] * (ei - ej) / eta
                alphas[j] = clipAlpha(alphas[j] , H , L)
                if (abs(alphas[j] - alphaJold) < 0.00001) :
                    print("j not moving enough")
                    continue
                alphas[i] += label_mat[j] * label_mat[i] * (alphaJold - alphas[j])
                b1 = b - ei - label_mat[i] * (alphas[i] - alphaIold) * data_matrix[i,:] * data_matrix[i,:].T - label_mat[j] * (alphas[j] - alphaJold) * data_matrix[i,:] * data_matrix[j,:].T
                b2 = b - ej - label_mat[i] * (alphas[i] - alphaIold) * data_matrix[i,:] * data_matrix[j,:].T - label_mat[j] * (alphas[j] - alphaJold) * data_matrix[j,:] * data_matrix[j,:].T
                if (0 < alphas[i]) and (c > alphas[i]) :
                    b = b1
                elif (0< alphas[j]) and (c > alphas[j]) :
                    b = b2
                else :
                    b = (b1 + b2) / 2.0
                alpha_pairs_changed += 1
                print("iter: %d i:%d , pairs changed %d" % (iter , i , alpha_pairs_changed))
        if (0 == alpha_pairs_changed) :
            iter += 1
        else :
            iter = 0
        print("iteration number: %d" % iter)
    return b , alphas


if __name__ == "__main__" :
    data_mat , label_mat = loadDataSet("./testSet.txt")
    print("data_mat:\n")
    print(data_mat)
    print("label_mat:\n")
    print(label_mat)
    b , alphas = smoSimple(data_mat , label_mat , 0.6 , 0.001 , 40)
    print("b: " % (b) )
    print("alphas: \n")
    print(alphas[alphas > 0])
    print(shape(alphas[alphas > 0]))
    print(alphas)
