from pyeda.inter import expr2bdd, expr, bddvars, bddvar
from graphviz import Source, Digraph, render
import pydot
import json
import re

# Здесь происходит извлечение наименований узлов по метки label. Эти имена сохраняются в два списка.
# Списки затем сравниваются. Также создаётся записываются данные в два словаря. Ключом в словаре является идентификатор
# узла, значением его label. Эти словари в дальнешем понадобятся для проверки идентичности ребёр между узлами
def nodes_comparator(nodeList1, nodeList2, dictGetted, dictGenerated):
    nameList1 = []
    nameList2 = []
    print("-------GETTED NODES--------")
    iterator = 0
    while iterator < len(nodeList1):
        if (nodeList1[iterator].get_name() == "graph") or (nodeList1[iterator].get_name() == "node"):
            nodeList1.remove(nodeList1[iterator])
        else:
            nodeAttr = nodeList1[iterator].get_attributes()
            # Добавляем в словарь соотвествие между вершиной и лейблом
            dictGetted[nodeList1[iterator].get_name()] = (nodeAttr['label']).lower()
            # Изменяем имя на значение label, приводя значение к нижнему регистру
            nodeList1[iterator].set_name(str(nodeAttr['label']).lower())
            nameList1.append(nodeList1[iterator].get_name() + "-" + nodeAttr["shape"])
            iterator += 1

    for node, i in enumerate(nodeList1):
        print(nodeList1[node])
    nameList1 = sorted(nameList1)
    print(nameList1)

    print("------GENERATED NODES-------")
    for node, i in enumerate(nodeList2):
        nodeAttr = nodeList2[node].get_attributes()
        dictGenerated[nodeList2[node].get_name()] = (nodeAttr['label']).lower().replace('"', '')
        nodeList2[node].set_name(str(nodeAttr['label']).lower().replace('"', ''))  # Костыль, чтобы не было кавычек
        nameList2.append(nodeList2[node].get_name() + "-" + nodeAttr["shape"])

    for node, i in enumerate(nodeList2):
        print(nodeList2[node])
    nameList2 = sorted(nameList2)
    print(nameList2)
    print(nameList2 == nameList1)

    return (nameList2 == nameList1)


# Старая версия проверки ребёр между узлами. Записывает информацию о связях между узлами в newEdgeList
# Каждый элемент списка представляет собой pydot.Edge(from, to)
def new_list_of_connections_creator(old_edge_list, new_edge_list, name_label_dict):
    for edge, i in enumerate(old_edge_list):
        edge_attr = old_edge_list[edge].obj_dict
        from_node_name = name_label_dict[edge_attr['points'][0]]
        to_node_name = name_label_dict[edge_attr['points'][1]]
        temp_edge = pydot.Edge(from_node_name, to_node_name)
        if 'style' in edge_attr['attributes']:
            if edge_attr['attributes']['style'] == 'dashed' or edge_attr['attributes']['style'] == 'dotted':
                temp_edge.set('label', '0')
            else:
                temp_edge.set('label', '1')
        else:
            temp_edge.set('label', '1')
        new_edge_list.append(temp_edge)


# Представление списка связей между узлами в виде словаря. Ключом словаря является узел
# значением список из пар [узел, метка ребра]
def implement_edges_as_dictionary_of_connections(edge_list, edge_dict, name_label_dict):
    for edge, i in enumerate(edge_list):
        edge_attr = edge_list[edge].obj_dict
        from_node = edge_list[edge].get_source()
        to_node = name_label_dict[edge_list[edge].get_destination()]
        if from_node not in edge_dict:
            edge_dict.setdefault(from_node, [])
        if 'style' in edge_attr['attributes']:
            if edge_attr['attributes']['style'] == 'dashed' or edge_attr['attributes']['style'] == 'dotted':
                edge_dict[from_node].append([to_node, 0])
            else:
                edge_dict[from_node].append([to_node, 1])
        else:
            edge_dict[from_node].append([to_node, 1])
        print(edge_list[edge])


# Проверка идентичности двух графов. Представляем связи между узлами в
# виде implement_edges_as_dictionary_of_connections
# Сравниваем две структуры данных.
def edges_comparator_new(edgeList1, edgeList2, nameLabelDict1, nameLabelDict2):
    newEdgeDict1 = {}
    newEdgeDict2 = {}
    print("----FIRST----")
    implement_edges_as_dictionary_of_connections(edgeList1, newEdgeDict1, nameLabelDict1)
    print("----SECOND----")
    implement_edges_as_dictionary_of_connections(edgeList2, newEdgeDict2, nameLabelDict2)

    print(nameLabelDict1)
    for i in newEdgeDict1:
        print(i, '{' + nameLabelDict1.get(i) + '}', newEdgeDict1[i])

    print(nameLabelDict2)
    for i in newEdgeDict2:
        print(i, '{' + nameLabelDict2.get(i) + '}',  newEdgeDict2[i])

    number_of_matches = 0
    for key in newEdgeDict1:
        if nameLabelDict1[key] in nameLabelDict2.values():
            first = newEdgeDict1[key]
            keys_list = get_keys_from_dict(nameLabelDict2, nameLabelDict1[key])
            for i in keys_list:
                second = newEdgeDict2[i]
                if sorted(first) == sorted(second):
                    number_of_matches = number_of_matches + 1
                    break
    print(number_of_matches)
    return number_of_matches == len(newEdgeDict1)


# Функция получения ключа по значению
def get_keys_from_dict(dictionary, value):
    keys_list = []
    for k, v in dictionary.items():
        if v == value:
            keys_list.append(k)
    return keys_list


# Старая версия проверки идентичности двух графов по связям.
def edges_comparator(edgeList1, edgeList2, nameLabelDict1, nameLabelDict2):
    newEdgeList1 = []
    newEdgeList2 = []

    print(edgeList2[1].obj_dict)

    new_list_of_connections_creator(edgeList1, newEdgeList1, nameLabelDict1)
    new_list_of_connections_creator(edgeList2, newEdgeList2, nameLabelDict2)

    for edge, i in enumerate(newEdgeList1):
        newEdgeList1[edge] = newEdgeList1[edge].to_string()
        newEdgeList2[edge] = newEdgeList2[edge].to_string()

    newEdgeList1 = sorted(newEdgeList1)
    newEdgeList2 = sorted(newEdgeList2)

    print(newEdgeList1)
    print(newEdgeList2)

    return newEdgeList1 == newEdgeList2


# Функция извлечения данных из двух DOT файлов и сравнение графов на идентичность
def dot_files_comparator(filePath1, filePath2):
    # Словарь соотвествий имён узлов и их лейблам, которые отображаются
    # Он нужен, чтобы в дальнейшем создать список из связей между узлами в правильных обозначениях, удобных для
    # Сравнения между собой
    nameLabelConformityGetted = {}
    nameLabelConformityGenerated = {}

    # Сначала проверяем на идентичность узлов. Если количество узлов и их наименования совпадают, то смотрим дальше
    # на связи, иначе сразу возвращаем ответ.

    # Файл DOT, полученный после построения учеником диаграммы
    graphGetted = pydot.graph_from_dot_file(filePath1)

    # Файл DOT, полученный автоматически с помощью библиотеки graphviz по функции мат.логики
    graphGenerated = pydot.graph_from_dot_file(filePath2)

    # Получаем список узлов из первого и второго файлов
    nodeListGetted = graphGetted[0].get_node_list()
    nodeListGenerated = graphGenerated[0].get_node_list()

    # Сравниваем узлы на идентичность + записываем значения в словарь
    similar = nodes_comparator(nodeListGetted, nodeListGenerated, nameLabelConformityGetted,
                               nameLabelConformityGenerated)
    if not similar:
        print("Различное наименование и количество узлов")
        return False

    print(nameLabelConformityGetted)
    print(nameLabelConformityGenerated)

    edgeListGetted = graphGetted[0].get_edge_list()
    edgeListGenerated = graphGenerated[0].get_edge_list()

    # Если количество связей разное, то сразу выдаём ответ за неверный
    if len(edgeListGetted) != len(edgeListGenerated):
        print("Неравное количество связей")
        return False

    # similar = edges_comparator(edgeListGetted, edgeListGenerated, nameLabelConformityGetted, nameLabelConformityGenerated)
    similar = edges_comparator_new(edgeListGetted, edgeListGenerated, nameLabelConformityGetted,
                                   nameLabelConformityGenerated)
    if not similar:
        return False
    else:
        return True


def get_dot_from_json(json_data, out_filename):
    dot = Digraph(name="JSON_to_DOT")

    if type(json_data) is dict:
        data = json_data
    else:
        with open(json_data, "r") as read_file:
            data = json.load(read_file)

    for node in data.get("nodes"):
        dot.node(name=str(node.get('id')), label=node.get('title').lower(),
                 shape=("circle" if (node.get('type') == "circle") else "box"))
    for edge in data.get("edges"):
        dot.edge(tail_name=str(edge.get("source")), head_name=str(edge.get("target")),
                 style=("dashed" if edge.get("type") == "dotted" else "solid"))

    gv = Source(dot)
    gv.save(filename=out_filename + ".dot")
    return out_filename + ".dot"

def latex2text(latex):
    rep = {"vee": "|",
           "wedge": "&",
           "overline": "~",
           "oplus":"^",
           '\\': ""}
    rep = dict((re.escape(k), v) for k, v in rep.items())
    pattern = re.compile("|".join(rep.keys()))
    text = pattern.sub(lambda m: rep[re.escape(m.group(0))], latex)
    return text

def text2bddExpr(text):
    formula = expr2bdd(expr(text))
    print(expr(text))
    gv = Source(formula.to_dot())
    file_path = "selfGeneratedDot.dot"
    gv.render(filename=file_path, format='png', view=False)
    return file_path


# text2bddExpr("Or(a,b,c)")

# get_dot_from_json("delete_this.json", "delete_this.dot")

#text2bddExpr("a|b&c")
# render("dot", "png", "delete_this.dot")
# render("delete_this.dot", format='png')