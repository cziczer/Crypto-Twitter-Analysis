import networkx as nx
from networkx.algorithms import community

from db_utils.select.network_data_selector import NetworkDataSelector

import plotly.graph_objects as go

from datetime import datetime


def update_weight(u_id, to_add, nodes):
    if u_id in nodes.keys():
        nodes[u_id] += to_add


def parse_nodes_weights(data, weight, nodes):
    for node in data:
        t_u_id = node['user_id']
        number = node['number']
        update_weight(t_u_id, weight * number, nodes)


def add_edge(user_A, user_B, edges):
    if (user_A, user_B) not in edges and (user_B, user_A) not in edges:
        edges.add((user_A, user_B))


def parse_edges(data, edges):
    for edge in data:
        user_A = edge['user_A']
        user_B = edge['user_B']
        add_edge(user_A, user_B, edges)


def has_edges(node_id, edges):
    for (from_id, to_id) in edges:
        if from_id == node_id or to_id == node_id:
            return True
    return False


def draw_plotly_graph(G, MAX_W, month_name):
    print("Drawing plotly graph...")

    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = G.nodes[edge[0]]['pos']
        x1, y1 = G.nodes[edge[1]]['pos']
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#999999'),
        hoverinfo='none',
        mode='lines')

    node_x = []
    node_y = []
    colors = []
    max_r = 0
    for node in G.nodes():
        x, y = G.nodes[node]['pos']
        max_r = max(max_r, abs(x))
        max_r = max(max_r, abs(y))
        node_x.append(x)
        node_y.append(y)
        com = G.nodes[node]['community']
        if com < len(COLORS_LIST) - 1:
            colors.append(COLORS_LIST[com])
        else:
            colors.append(COLORS_LIST[-1])

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        # mode='markers+text',
        hoverinfo='text',
        marker=dict(
            color=colors,
            line_width=1,
            opacity=1
        ))
    node_trace.text = [node['username'] for (_, node) in list(G.nodes.data())]
    # node_trace.text = [str(has_edges(node)) + G.nodes[node]['screen_name'] for node in G.nodes()]
    node_trace.marker.size = [scaling(node['w']) * MAX_SIZE / MAX_W + MIN_SIZE for (_, node) in list(G.nodes.data())]

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title='<br>Network graph: ' + month_name + '</br>',
                        titlefont_size=16,
                        showlegend=False,
                        hovermode='closest',
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        margin=dict(b=20, l=5, r=5, t=40),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-max_r, max_r]),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-max_r, max_r]))
                    )
    fig.show()


def find_communities(G):
    communities = list(community.greedy_modularity_communities(G))
    shells = []
    i = 0
    for com in communities:
        shell = []
        for node in list(com):
            shell.append(node)
            G.nodes[node]['community'] = i
        i += 1
        shells.append(shell)
    return shells


COLORS_LIST = ['#a6cee3', '#b2df8a', '#fb9a99', '#fdbf6f', '#cab2d6', '#1f78b4', '#33a02c', '#e31a1c', '#ff7f00',
               '#6a3d9a']

RETWEET_W = 0.3
QUOTE_W = 2
REPLY_W = 1
LIKE_W = 1.25
USER_MENTION_W = 2
FOLLOWERS_W = 0.1

# RETWEET_W = 1
# QUOTE_W = 1
# REPLY_W = 1
# USER_MENTION_W = 1
# FOLLOWERS_W = 1

scaling = lambda x: x
MIN_SIZE = 10
MAX_SIZE = 50 + MIN_SIZE


def make_network_graph(db, from_date=None, to_date=None, month_name=None):
    G = nx.DiGraph()

    print("-- GETTING USER NODES --")
    nodes_data = db.get_user_nodes()
    edges = set()  # (from, to)
    nodes = dict()  # id -> w
    # nodes_n = dict()  # id -> com
    for node in nodes_data:
        nodes[node['id']] = 0

    print("--- Node weights ---")
    data = db.get_nodes_weights()
    for node in data:
        t_u_id = node['author_id']
        replies = node['replies']
        quotes = node['quotes']
        retweets = node['retweets']
        likes = node['likes']
        update_weight(t_u_id, REPLY_W * replies, nodes)
        update_weight(t_u_id, QUOTE_W * quotes, nodes)
        update_weight(t_u_id, RETWEET_W * retweets, nodes)
        update_weight(t_u_id, LIKE_W * likes, nodes)

    print("1/3 --> RETWEETS, QUOTES, REPLIES, LIKES")
    parse_nodes_weights(db.get_followers_weights(), FOLLOWERS_W, nodes)
    print("2/3 --> FOLLOWERS")
    parse_nodes_weights(db.get_usermentions_weights(), USER_MENTION_W, nodes)
    print("3/3 --> USER_MENTIONS")

    MAX_W = scaling(max(list(nodes.values())))
    print("----- Edges -----")
    parse_edges(db.get_retweet_edges(from_date, to_date), edges)
    print("1/3 --> RETWEET edges")
    parse_edges(db.get_quote_edges(from_date, to_date), edges)
    print("2/3 --> QUOTE edges")
    parse_edges(db.get_replies_edges(from_date, to_date), edges)
    print("3/3 --> REPLIES edges")


    print("-- Creating networkx --")
    for node in nodes_data:
        if has_edges(node['id'], edges):
            G.add_node(node['id'], username=node['username'], followers_count=node['followers_count'],
                       following_count=node['following_count'], listed_count=node['listed_count'], w=nodes[node['id']])

    for (a, b) in edges:
        G.add_edge(a, b)

    pos = nx.spring_layout(G, k=0.5, iterations=100)
    # pos = nx.spiral_layout(G)
    print(G.number_of_nodes())
    communities = find_communities(G)
    # pos = nx.shell_layout(G, communities)

    for node in G.nodes:
        G.nodes[node]['pos'] = list(pos[node])
    print("-- Graph created --")
    nx.write_edgelist(G, 'results/network_5k.csv', data=False)
    # nx.write_gexf(G, "results/test.gexf")
    # draw_plotly_graph(G, MAX_W, month_name)


if __name__ == "__main__":
    db = NetworkDataSelector()

    march = datetime.strptime("2022-03-01", "%Y-%m-%d").date(), datetime.strptime("2022-03-31",
                                                                                  "%Y-%m-%d").date(), "march"
    april = datetime.strptime("2022-04-01", "%Y-%m-%d").date(), datetime.strptime("2022-04-30",
                                                                                  "%Y-%m-%d").date(), "april"
    # make_network_graph(db, *march)
    make_network_graph(db, *april)
