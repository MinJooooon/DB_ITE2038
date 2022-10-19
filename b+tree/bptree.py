from __future__ import annotations  # Node 클래스 내부에서 Node 타입을 사용하기 위함
import sys  # for command line argument


class Node:
    m: int  # number of keys
    p: dict  # data_node 이면 [int, dict], index_node 이면 [int, Node]
    r: Node  # data_node 이면 right sibling node, index_node 이면 leftmost child node 를 가리킴
    degree: int
    is_index_node: bool
    is_data_node: bool

    def __init__(self, degree=0):
        self.m = 0
        self.p = dict()
        self.r = None
        self.degree = degree
        self.is_index_node = True
        self.is_data_node = True


class bPlusTree:
    root: Node
    degree: int
    key_values: dict[int, dict[int, int]]
    # 큰 dict 의 key 는 포인터 주소의 역할,
    # 큰 dict 의 value 에 key_value pairs 를 저장

    def __init__(self, degree=0):
        self.root = Node(degree)
        self.degree = degree
        self.key_values = dict()


def creation(degree: int) -> bPlusTree:
    new_tree = bPlusTree(degree)
    return new_tree


# node 에 key 삽입 시 ASCENDING order 로 저장하기 위해 사용
def sort_dictionary(dictionary: dict) -> dict:
    sorted_tuple = sorted(dictionary.items())
    sorted_dict = dict((key, value) for key, value in sorted_tuple)
    return sorted_dict


# data_node 의 parent_node 반환
# 해당 node 가 root node 일 경우 None 반환
def find_data_node_parent(tree: bPlusTree, split_key: int) -> Node:
    tmp_node = tree.root
    parent_node = None

    # tmp_node 가 data_node 가 될 때까지 반복
    while not tmp_node.is_data_node:
        parent_node = tmp_node

        # split_key 가 tmp_node 의 모든 key 들보다 작을 경우 tmp_node 의 leftmost child 로 이동
        if list(tmp_node.p.keys())[0] > split_key:
            tmp_node = tmp_node.r

        # split_key 가 tmp_node 의 모든 key 들보다 클 경우 tmp_node 의 rightmost child 로 이동
        elif split_key > list(tmp_node.p.keys())[-1]:
            tmp_node = tmp_node.p[list(tmp_node.p.keys())[-1]]

        # split_key 가 tmp_node 의 keys[i] keys[i + 1] 사이의 범위에 존재하면 keys[i]가 가리키는 child 로 이동
        else:
            # for loop 를 돌며 if 문을 만족하면 tmp_node 이동 후 바로 break for loop
            for i in range(len(list(tmp_node.p.keys())) - 1):
                if list(tmp_node.p.keys())[i] < split_key < list(tmp_node.p.keys())[i + 1]:
                    tmp_node = tmp_node.p[list(tmp_node.p.keys())[i]]
                    break

    return parent_node


# index_node 의 parent_node 반환
# 해당 node 가 root node 일 경우 None 반환
def find_index_node_parent(tree: bPlusTree, split_key: int) -> Node:
    tmp_node = tree.root
    parent_node = None
    while True:
        # while loop 진행 도중 split_key 가 tmp_node 에 존재하는 경우 break while loop
        if split_key in list(tmp_node.p.keys()):
            break

        # 다음 while loop 가 line 82 ~ 83 에 의해 break 된다면 반환해줄 parent node 지정
        parent_node = tmp_node

        # split_key 가 tmp_node 의 모든 key 들보다 작을 경우 tmp_node 의 leftmost child 로 이동
        if list(tmp_node.p.keys())[0] > split_key:
            tmp_node = tmp_node.r
        # split_key 가 tmp_node 의 모든 key 들보다 클 경우 tmp_node 의 rightmost child 로 이동
        elif split_key > list(tmp_node.p.keys())[-1]:
            tmp_node = tmp_node.p[list(tmp_node.p.keys())[-1]]

        # split_key 가 tmp_node 의 keys[i] keys[i + 1] 사이의 범위에 존재하면 keys[i]가 가리키는 child 로 이동
        else:
            # for loop 를 돌며 if 문을 만족하면 tmp_node 이동 후 바로 break for loop
            for i in range(len(list(tmp_node.p.keys())) - 1):
                if list(tmp_node.p.keys())[i] < split_key < list(tmp_node.p.keys())[i + 1]:
                    tmp_node = tmp_node.p[list(tmp_node.p.keys())[i]]
                    break

    # 처음부터 split_key 가 tmp_node 에 존재해 while loop 가 바로 종료되었다면
    # split_key 가 root node 에 존재하는 것이므로 None 반환
    if tmp_node is tree.root:
        return None

    return parent_node


# node 를 받아 split 하여 반환
# parent node 가 있는 data node
# parent node 가 없는 data node
# parent node 가 있는 index node
# parent node 가 없는 index node
# 총 4가지 경우로 나누어서 진행
def split(tree: bPlusTree, node: Node, mid: int) -> Node:
    # split_key 선택
    split_key = list(node.p.keys())[mid]

    parent = Node(tree.degree)
    if node.is_data_node:

        # parent node 가 있는 data node
        if isinstance(find_data_node_parent(tree, split_key), Node):
            # data node 이므로 child node 가 split_key 를 포함하도록 split 진행
            right = Node(node.degree)
            right.p = dict(list(node.p.items())[mid:])
            right.m = len(right.p)
            right.r = node.r
            right.is_index_node = node.is_index_node
            right.is_data_node = node.is_data_node
            
            # parent node 가 있는 경우이므로 parent node 를 찾아 split_key 추가
            parent = find_data_node_parent(tree, split_key)
            parent.p[split_key] = right
            parent.p = sort_dictionary(parent.p)
            parent.m += 1
            
            # 기존 node 에서 split_key 와 right child 노드의 key 삭제
            for k in list(right.p.keys()):
                del node.p[k]
            node.m -= len(list(right.p.keys()))
            node.r = right

            # split_key 가 parent node 에서 제일 작은 key 이면
            # 기존 node 를 parent node 의 leftmost child 로 지정
            if split_key <= list(parent.p.keys())[0]:
                parent.r = node

        # parent node 가 없는 data node
        else:

            # data node 이므로 child node 가 split_key 를 포함하도록 split 진행
            right = Node(node.degree)
            right.p = dict(list(node.p.items())[mid:])
            right.m = len(right.p)
            right.r = node.r
            right.is_index_node = node.is_index_node
            right.is_data_node = node.is_data_node

            # 기존 node 에서 split_key 와 right child 노드의 key 삭제
            for k in list(right.p.keys()):
                del node.p[k]
            node.m -= len(list(right.p.keys()))
            node.r = right

            # parent node 가 없는 경우이므로 새로운 parent node 에 split_key 추가 후 root node 로 지정
            parent.is_data_node = False
            parent.is_index_node = True
            parent.p[split_key] = right
            parent.r = node
            parent.m += 1
            tree.root = parent

    elif node.is_index_node:

        # parent node 가 있는 index node
        if isinstance(find_index_node_parent(tree, split_key), Node):

            # index node 이므로 child node 가 split_key 를 포함하지 않도록 split 진행
            right = Node(node.degree)
            right.p = dict(list(node.p.items())[mid + 1:])
            right.m = len(right.p)
            right.r = node.p[list(node.p.keys())[mid]]
            right.is_index_node = node.is_index_node
            right.is_data_node = node.is_data_node

            # parent node 가 있는 경우이므로 parent node 를 찾아 split_key 추가
            parent = find_index_node_parent(tree, split_key)
            parent.p[split_key] = right
            parent.p = sort_dictionary(parent.p)
            parent.m += 1

            # 기존 node 에서 split_key 와 right child 노드의 key 삭제
            for k in list(right.p.keys()):
                del node.p[k]
            del node.p[split_key]
            node.m -= (len(list(right.p.keys())) + 1)

            # split_key 가 parent node 에서 제일 작은 key 이면
            # 기존 node 를 parent node 의 leftmost child 로 지정
            if split_key <= list(parent.p.keys())[0]:
                parent.r = node

        # parent node 가 없는 index node
        else:

            # index node 이므로 child node 가 split_key 를 포함하지 않도록 split 진행
            right = Node(node.degree)
            right.p = dict(list(node.p.items())[mid + 1:])
            right.m = len(right.p)
            right.r = node.p[list(node.p.keys())[mid]]
            right.is_index_node = node.is_index_node
            right.is_data_node = node.is_data_node

            # 기존 node 에서 split_key 와 right child 노드의 key 삭제
            for k in list(right.p.keys()):
                del node.p[k]
            del node.p[split_key]
            node.m -= (len(list(right.p.keys())) + 1)

            # parent node 가 없는 경우이므로 새로운 parent node 에 split_key 추가 후 root node 로 지정
            parent.is_data_node = False
            parent.is_index_node = True
            parent.p[split_key] = right
            parent.r = node
            parent.m += 1
            tree.root = parent

    return parent


def insertion(tree: bPlusTree, key: int, value: int) -> bPlusTree:
    mid = tree.degree // 2

    # tree 에 data node 만 존재하는 경우
    if tree.root.is_data_node:
        tree.root.is_index_node = False
        tree.key_values[key] = {key: value}
        tree.root.p[key] = tree.key_values[key]
        tree.root.p = sort_dictionary(tree.root.p)  # The keys in a node are stored in an ASCENDING order
        tree.root.m += 1

        # node 에 공간이 없을 경우 split 시행
        if tree.root.m == tree.degree:
            tree.root = split(tree, tree.root, mid)

    # tree 에 index node 와 node node 모두 존재하는 경우
    else:
        tmp_node = tree.root

        # data node 에 도착할 때까지 진행
        while not tmp_node.is_data_node:

            # index node 탐색 도중 key 가 발견 되었다면 그 index node 가 가리키는 child 로 이동
            if key in list(tmp_node.p.keys()):
                tmp_node = tmp_node.p[key]

            # index node 의 number of keys 가 1 일 때
            elif len(tmp_node.p.keys()) == 1:

                # key 가 index node 에 존재하는 key 보다 작으면 index node 의 left child 로 이동
                if key < list(tmp_node.p.keys())[0]:
                    tmp_node = tmp_node.r

                # key 가 index node 에 존재하는 key 보다 크면 index node 의 right child 로 이동
                else:
                    tmp_node = tmp_node.p[list(tmp_node.p.keys())[0]]

            # index node 에 여러개의 key 들이 있을 때
            else:

                # split_key 가 tmp_node 의 모든 key 들보다 작을 경우 tmp_node 의 leftmost child 로 이동
                if key < list(tmp_node.p.keys())[0]:
                    tmp_node = tmp_node.r

                # split_key 가 tmp_node 의 모든 key 들보다 클 경우 tmp_node 의 rightmost child 로 이동
                elif key > list(tmp_node.p.keys())[-1]:
                    tmp_node = tmp_node.p[list(tmp_node.p.keys())[-1]]

                # split_key 가 tmp_node 의 keys[i] keys[i + 1] 사이의 범위에 존재하면 keys[i]가 가리키는 child 로 이동
                else:
                    # for loop 를 돌며 if 문을 만족하면 tmp_node 이동 후 바로 break for loop
                    for i in range(len(list(tmp_node.p.keys())) - 1):
                        if list(tmp_node.p.keys())[i] < key < list(tmp_node.p.keys())[i + 1]:
                            tmp_node = tmp_node.p[list(tmp_node.p.keys())[i]]
                            break

        # 도착한 data node 에 key 삽입
        tree.key_values[key] = {key: value}
        tmp_node.p[key] = tree.key_values[key]
        tmp_node.p = sort_dictionary(tmp_node.p)  # The keys in a node are stored in an ASCENDING order
        tmp_node.m += 1

        # node 에 공간이 없을 경우 split 시행
        # split 완료 후의 node 에 또 공간이 없을 경우, 다시 split 시행
        while tmp_node.m == tree.degree:
            tmp_node = split(tree, tmp_node, mid)

    return tree


def deletion(tree: bPlusTree, key: int) -> bPlusTree:
    pass


# index_file 을 tree 로 옮겨주는 함수
def index_file_to_tree(index_file: str) -> bPlusTree:
    existed_tree = bPlusTree()
    with open(index_file, 'r') as f_index:

        # 기존 노드와 degree 가 같은 빈 tree 생성
        first_line = f_index.readline()
        degree = int(first_line.split(':')[1])
        existed_tree.degree = degree
        existed_tree.root = Node(degree)

        # key,value pairs 저장
        dummy = "dummy string"
        keys = list()
        values = list()
        while True:
            dummy = f_index.readline()
            if dummy == "key,value pairs\n" or not dummy:
                break

        while True:
            line = f_index.readline()
            if not line:
                break
            key = int(line.split(',')[0])
            value = int(line.split(',')[1])
            keys.append(key)
            values.append(value)

        for i in range(len(keys)):  # keys 와 values 의 길이는 반드시 같음
            existed_tree = insertion(existed_tree, keys[i], values[i])

    return existed_tree


# insert 완료한 tree 를 index_file 에 저장
def tree_to_index_file(tree: bPlusTree, index_file: str) -> None:
    tmp_tree = tree
    with open(index_file, 'a') as f_index:
        for k in list(tmp_tree.key_values.keys()):
            f_index.write(str(k) + "," + str(tmp_tree.key_values[k][k]) + "\n")


def main():
    tree = bPlusTree()

    # Data File Creation
    if sys.argv[1] == "-c":
        index_file = sys.argv[2]
        degree = int(sys.argv[3])
        tree = creation(degree)
        with open(index_file, 'w') as f_index:
            f_index.write("B+ tree with node size:" + str(degree) + "\n")

    # Insertion of Keys
    elif sys.argv[1] == "-i":
        index_file = sys.argv[2]
        data_file = sys.argv[3]

        # index_file 에 저장되어있던 tree 호출
        tree = index_file_to_tree(index_file)

        # key,value pairs 저장
        keys = list()
        values = list()

        with open(data_file, 'r') as f_data:
            while True:
                line = f_data.readline()
                if not line:
                    break
                key = int(line.split(',')[0])
                value = int(line.split(',')[1])
                keys.append(key)
                values.append(value)

        for i in range(len(keys)):  # keys 와 values 의 길이는 반드시 같음
            tree = insertion(tree, keys[i], values[i])

        with open(index_file, 'w') as f_index:
            f_index.write("B+ tree with node size:" + str(tree.degree) + "\n")

        with open(index_file, 'a') as f_index:
            f_index.write("\n")
            f_index.write("key,value pairs")
            f_index.write("\n")

        tree_to_index_file(tree, index_file)

    # Deletion of Keys
    elif sys.argv[1] == "-d":
        index_file = sys.argv[2]
        data_file = sys.argv[3]

        # index_file 에 저장되어있던 tree 호출
        tree = index_file_to_tree(index_file)
        degree = tree.degree
        # delete 할 key 들 저장
        keys = list()

        with open(data_file, 'r') as f_data:
            while True:
                line = f_data.readline()
                if not line:
                    break
                keys.append(int(line))

        for key in keys:
            tree = deletion(tree, key)

        with open(index_file, 'w') as f_index:
            f_index.write("B+ tree with node size:" + str(degree) + "\n")

        with open(index_file, 'a') as f_index:
            f_index.write("\n")
            f_index.write("key,value pairs")
            f_index.write("\n")

        tree_to_index_file(tree, index_file)

    # Single Key Search
    elif sys.argv[1] == "-s":
        index_file = sys.argv[2]
        key = int(sys.argv[3])

        # index_file 에 저장되어있던 tree 호출
        tree = index_file_to_tree(index_file)
        tmp_node = tree.root

        while True:

            # data_node 에 도달했는데 key 가 없을 경우
            if tmp_node.is_data_node and key not in list(tmp_node.p.keys()):
                # print 'NOT FOUND'
                print("NOT FOUND", end='')
                # 종료
                break

            # key 가 node 에 존재하는 경우: 그 node 가 index_node 인 경우와 data_node 인 경우로 분할
            if key in list(tmp_node.p.keys()):

                # index_node 인 경우
                if tmp_node.is_index_node:

                    # node 의 key 값들 출력
                    for k in list(tmp_node.p.keys()):
                        if k == list(tmp_node.p.keys())[-1]:
                            print(k)
                        else:
                            print(k, end=',')

                    # 해당 key 가 가리키는 child node 로 이동
                    tmp_node = tmp_node.p[key]
                    
                # data_node 인 경우
                elif tmp_node.is_data_node:

                    # key 에 해당하는 value 출력
                    print(tmp_node.p[key][key], end='')
                    # 종료
                    break

            # key 가 node 에 존재하지 않는 경우: 3 가지 경우로 분할

            # key 가 node 의 모든 key 들 보다 작은 경우
            elif list(tmp_node.p.keys())[0] > key:

                # node 의 key 값들 출력
                for k in list(tmp_node.p.keys()):
                    if k == list(tmp_node.p.keys())[-1]:
                        print(k)
                    else:
                        print(k, end=',')

                # node 의 leftmost child 로 이동
                tmp_node = tmp_node.r
                
            # key 가 node 의 모든 key 들 보다 큰 경우
            elif key > list(tmp_node.p.keys())[-1]:

                # node 의 key 값들 출력
                for k in list(tmp_node.p.keys()):
                    if k == list(tmp_node.p.keys())[-1]:
                        print(k)
                    else:
                        print(k, end=',')

                # node 의 rightmost child 로 이동
                tmp_node = tmp_node.p[list(tmp_node.p.keys())[-1]]
                
            # key 가 node 의 key 들의 제일 작은 값과 제일 큰 값 사이에 있는 경우
            else:

                # for loop 를 돌며 if 문을 만족하면 tmp_node 이동 후 바로 break for loop
                for i in range(len(list(tmp_node.p.keys())) - 1):

                    # keys[i] keys[i + 1] 사이의 범위에 존재하면
                    if list(tmp_node.p.keys())[i] < key < list(tmp_node.p.keys())[i + 1]:

                        # node 의 key 값들 출력
                        for k in list(tmp_node.p.keys()):
                            if k == list(tmp_node.p.keys())[-1]:
                                print(k)
                            else:
                                print(k, end=',')
                        break

                # keys[i]가 가리키는 child 로 이동
                tmp_node = tmp_node.p[list(tmp_node.p.keys())[i]]

    # Range Search
    elif sys.argv[1] == "-r":
        index_file = sys.argv[2]
        start_key = int(sys.argv[3])
        end_key = int(sys.argv[4])

        # index_file 에 저장되어있던 tree 호출
        tree = index_file_to_tree(index_file)
        start_node = tree.root
        # start_node 에 start_key 이상이면서 제일 작은 key 를 가진 leaf node 를 저장
        while not start_node.is_data_node:
            if start_key in list(start_node.p.keys()):
                start_node = start_node.p[start_key]

            elif len(start_node.p.keys()) == 1:
                if start_key < list(start_node.p.keys())[0]:
                    start_node = start_node.r
                else:
                    start_node = start_node.p[list(start_node.p.keys())[0]]

            else:
                if start_key < list(start_node.p.keys())[0]:
                    start_node = start_node.r
                elif start_key > list(start_node.p.keys())[-1]:
                    start_node = start_node.p[list(start_node.p.keys())[-1]]
                else:
                    for i in range(len(list(start_node.p.keys())) - 1):
                        if list(start_node.p.keys())[i] < start_key < list(start_node.p.keys())[i + 1]:
                            start_node = start_node.p[list(start_node.p.keys())[i]]
                            break

        end_node = tree.root
        # end_node 에 end_key 이하이면서 제일 큰 key 를 가진 leaf node 를 저장
        while not end_node.is_data_node:
            if end_key in list(end_node.p.keys()):
                end_node = end_node.p[end_key]

            elif len(end_node.p.keys()) == 1:
                if end_key < list(end_node.p.keys())[0]:
                    end_node = end_node.r
                else:
                    end_node = end_node.p[list(end_node.p.keys())[0]]

            else:
                if end_key < list(end_node.p.keys())[0]:
                    end_node = end_node.r
                elif end_key > list(end_node.p.keys())[-1]:
                    end_node = end_node.p[list(end_node.p.keys())[-1]]
                else:
                    for i in range(len(list(end_node.p.keys())) - 1):
                        if list(end_node.p.keys())[i] < end_key < list(end_node.p.keys())[i + 1]:
                            end_node = end_node.p[list(end_node.p.keys())[i]]
                            break

        # start_node 와 end_node 가 같아질 때까지 start_(key,value) 부터 출력 시작
        # start_node 와 end_node 가 처음부터 같을 경우는 while 문 실행하지 않음
        while start_node is not end_node:
            real_start_key = 0
            start_key_in_node = False
            count = 0
            for i in range(len(list(start_node.p.keys()))):
                if start_key > list(start_node.p.keys())[i]:
                    real_start_key = list(start_node.p.keys())[i]
                    count += 1
                elif start_key == list(start_node.p.keys()):
                    real_start_key = start_key
                    start_key_in_node = True
            # start_key 가 node 의 모든 key 들보다 작은 경우
            if real_start_key == 0:
                for k in list(start_node.p.keys()):
                    print(str(k) + "," + str(start_node.p[k][k]))
                start_node = start_node.r
            else:
                # start_key 가 node 안에 존재하는 경우
                if start_key_in_node:
                    for i in range(count, len(list(start_node.p.keys()))):
                        k = list(start_node.p.keys())[i]
                        print(str(k) + "," + str(start_node.p[k][k]))
                    start_node = start_node.r
                else:
                    # start_key 가 node 의 모든 key 들보다 큰 경우
                    if count == tree.degree - 1:
                        start_node = start_node.r
                    # start_key 가 node 안에는 존재하지 않지만 key 들 사이에 존재하는 경우
                    else:
                        for i in range(count, len(list(start_node.p.keys()))):
                            k = list(start_node.p.keys())[i]
                            print(str(k) + "," + str(start_node.p[k][k]))
                        start_node = start_node.r

        # start_node 와 end_node 가 같아지면 end_(key,value) 까지 출력
        # 처음부터 start_node 와 end_node 가 같다면 start_key 이상 end_key 이하의 (key,value) 출력
        real_start_key = 0
        real_end_key = sys.maxsize
        for k in list(start_node.p.keys()):
            if real_start_key < start_key:
                real_start_key = k
        for k in reversed(list(end_node.p.keys())):
            if end_key < real_end_key:
                real_end_key = k
        start_index = list(start_node.p.keys()).index(real_start_key)
        end_index = list(end_node.p.keys()).index(real_end_key)
        for i in range(start_index, end_index + 1):
            k = list(start_node.p.keys())[i]
            print(str(k) + "," + str(start_node.p[k][k]))

    else:
        print("Wrong Command!")
        return


if __name__ == '__main__':
    main()
