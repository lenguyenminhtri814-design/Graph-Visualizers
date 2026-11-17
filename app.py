import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network 
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Graph Visualizer & Solver",
    page_icon="",
    layout="wide",
)

# =========================
# KHỞI TẠO DỮ LIỆU
# =========================

# Chọn loại đồ thị
if "graph_type" not in st.session_state:
    st.session_state.graph_type = "Vô hướng"

graph_type = st.sidebar.radio(
    "Chọn loại đồ thị",
    ["Vô hướng", "Có hướng"],
    key="graph_type"
)

is_directed = graph_type == "Có hướng"

# Khởi tạo đồ thị
if "G" not in st.session_state:
    if is_directed:
        st.session_state.G = nx.DiGraph()
    else:
        st.session_state.G = nx.Graph()

else:
    old_G = st.session_state.G

    # Chuyển đổi loại đồ thị khi người dùng thay đổi lựa chọn
    if old_G.is_directed() != is_directed:

        if is_directed:
            new_G = nx.DiGraph()
        else:
            new_G = nx.Graph()

        new_G.add_nodes_from(old_G.nodes(data=True))

        for u, v, data in old_G.edges(data=True):
            new_G.add_edge(u, v, **data)

            # Đồ thị vô hướng chuyển sang có hướng:
            # tạo hai chiều cho mỗi cạnh cũ
            if is_directed and not old_G.is_directed():
                new_G.add_edge(v, u, **data)

        st.session_state.G = new_G

G = st.session_state.G

st.title("GRAPH VISUALIZER & SOLVER")
st.caption("Ứng dụng quản lý, trực quan hóa và giải thuật đồ thị")

# =========================
# THANH BÊN
# =========================

st.sidebar.header("Quản lý đồ thị")

menu = st.sidebar.radio(
    "Chọn chức năng",
    [
        "Tổng quan",
        "Quản lý đỉnh",
        "Quản lý cạnh",
        "Ma trận kề",
        "Thuật toán Euler",
        "Thuật toán Hamilton",
        "Dijkstra",
        "Floyd-Warshall",
    ],
)

# =========================
# TỔNG QUAN
# =========================

if menu == "Tổng quan":
    st.subheader("Thông tin đồ thị")

    c1, c2, c3 = st.columns(3)

    c1.metric("Số đỉnh", G.number_of_nodes())
    c2.metric("Số cạnh", G.number_of_edges())
if menu == "Tổng quan":
    st.subheader("Thông tin đồ thị")

    c1, c2, c3 = st.columns(3)

    c1.metric("Số đỉnh", G.number_of_nodes())
    c2.metric("Số cạnh", G.number_of_edges())

    if G.number_of_nodes() > 0:
        if G.is_directed():
            connected = nx.is_weakly_connected(G)
        else:
            connected = nx.is_connected(G)
    else:
        connected = False

    c3.metric("Liên thông", "Có" if connected else "Không")
    st.divider()

    st.subheader("Đồ thị tương tác")

    if G.number_of_nodes() == 0:
        st.info("Hãy thêm đỉnh để bắt đầu.")
    else:
        net = Network(
            height="650px",
            width="100%",
            directed=G.is_directed(),
            bgcolor="#FFFFFF",
            font_color="#222222",
            cdn_resources="in_line"
        )

        pos = nx.spring_layout(G, seed=42)

        for node in G.nodes():
            net.add_node(
                node,
                label=str(node),
                title=f"Đỉnh: {node}",
                color="#6495ED",
                size=25,
                x=float(pos[node][0] * 500),
                y=float(pos[node][1] * 500),
                physics=False
            )

        for u, v, data in G.edges(data=True):
            weight = data.get("weight", 1)

            net.add_edge(
                u,
                v,
                label=str(weight),
                title=f"Khoảng cách: {weight}",
                color="#888888",
                width=2
            )

        net.toggle_physics(True)
        net.show_buttons(filter_=["physics"])

        html = net.generate_html()

        st.components.v1.html(
            html,
            height=700,
            scrolling=True
        )

elif menu == "Quản lý đỉnh":
    st.subheader("Quản lý đỉnh")

    with st.form("add_node"):
        name = st.text_input("Tên đỉnh")
        add = st.form_submit_button("Thêm đỉnh")

        if add:
            name = name.strip()
            if not name:
                st.error("Tên đỉnh không được để trống.")
            elif name in G:
                st.warning("Đỉnh đã tồn tại.")
            else:
                G.add_node(name)
                st.success(f"Đã thêm đỉnh {name}")
                st.rerun()

    st.divider()

    if G.number_of_nodes():
        node = st.selectbox("Chọn đỉnh muốn xóa", list(G.nodes()))

        if st.button("Xóa đỉnh"):
            G.remove_node(node)
            st.success("Đã xóa đỉnh.")
            st.rerun()

        st.write("Danh sách đỉnh:", list(G.nodes()))

# =========================
# QUẢN LÝ CẠNH
# =========================

elif menu == "Quản lý cạnh":
    st.subheader("Quản lý cạnh")

    nodes = list(G.nodes())

    if len(nodes) < 2:
        st.warning("Cần ít nhất 2 đỉnh.")
    else:
        with st.form("add_edge"):
            u = st.selectbox("Đỉnh thứ nhất", nodes)
            v = st.selectbox("Đỉnh thứ hai", nodes)
            w = st.number_input("Khoảng cách", min_value=0.0001, value=1.0)

            add = st.form_submit_button("Thêm cạnh")

            if add:
                if u == v:
                    st.error("Không thể nối một đỉnh với chính nó.")
                else:
                    G.add_edge(u, v, weight=w)
                    st.success(f"Đã nối {u} với {v}")
                    st.rerun()

        st.divider()

        edges = list(G.edges())

        if edges:
            edge = st.selectbox(
                "Chọn cạnh muốn xóa",
                edges,
                format_func=lambda e: f"{e[0]} — {e[1]}",
            )

            if st.button("Xóa cạnh"):
                G.remove_edge(*edge)
                st.success("Đã xóa cạnh.")
                st.rerun()

        st.write("Danh sách cạnh:", edges)

# =========================
# MA TRẬN KỀ
# =========================

elif menu == "Ma trận kề":
    st.subheader("Ma trận kề")

    if G.number_of_nodes() == 0:
        st.info("Đồ thị chưa có đỉnh.")
    else:
        nodes = list(G.nodes())

        matrix = nx.to_numpy_array(G, nodelist=nodes, weight=None, dtype=int)
        st.write("Ma trận kề không trọng số:")
        st.dataframe(matrix)

        weighted = nx.to_numpy_array(G, nodelist=nodes, weight="weight")
        st.write("Ma trận trọng số:")
        st.dataframe(weighted)

# =========================
# EULER - NÂNG CẤP TRỰC QUAN HÓA
# =========================

elif menu == "Thuật toán Euler":
    st.subheader("Kiểm tra và tìm đường đi Euler")

    if G.number_of_nodes() == 0 or G.number_of_edges() == 0:
        st.warning("Đồ thị cần có ít nhất một cạnh.")

    else:
        if st.button("Chạy thuật toán Euler"):

            try:
                # Kiểm tra chu trình Euler và đường đi Euler
                if nx.is_eulerian(G):
                    path = list(nx.eulerian_circuit(G))
                    result_type = "Chu trình Euler"

                elif nx.has_eulerian_path(G):
                    path = list(nx.eulerian_path(G))
                    result_type = "Đường đi Euler"

                else:
                    path = None
                    result_type = None

                if path is None:
                    st.error("Đồ thị không có đường đi Euler.")

                else:
                    # Tạo danh sách đỉnh theo thứ tự
                    route = [path[0][0]] + [v for u, v in path]

                    st.success(f"Đồ thị có {result_type}!")

                    st.write("### Thứ tự đi qua các đỉnh")
                    st.code(" → ".join(map(str, route)))

                    # Tính tổng trọng số
                    total_weight = sum(
                        G[u][v].get("weight", 1)
                        for u, v in path
                    )

                    st.metric("Tổng trọng số", total_weight)
                    st.metric("Số cạnh đã đi qua", len(path))

                    # Vẽ đồ thị Euler
                    st.write("### Đồ thị Euler trực quan")

                    fig, ax = plt.subplots(figsize=(10, 7))
                    pos = nx.spring_layout(G, seed=42)

                    # Lưu thứ tự đi qua từng cạnh
                    edge_order = {}

                    for i, (u, v) in enumerate(path, start=1):
                        if G.is_directed():
                            edge_order[(u, v)] = i
                        else:
                            edge_order[frozenset((u, v))] = i

                    # Tô màu cạnh
                    edge_colors = []

                    for u, v in G.edges():
                        if G.is_directed():
                            key = (u, v)
                        else:
                            key = frozenset((u, v))

                        if key in edge_order:
                            edge_colors.append("red")
                        else:
                            edge_colors.append("gray")

                    nx.draw_networkx_nodes(
                        G, pos,
                        node_color="skyblue",
                        node_size=1600,
                        ax=ax
                    )

                    nx.draw_networkx_labels(
                        G, pos,
                        font_size=12,
                        font_weight="bold",
                        ax=ax
                    )

                    nx.draw_networkx_edges(
                        G, pos,
                        edge_color=edge_colors,
                        width=3,
                        arrows=G.is_directed(),
                        arrowsize=25,
                        ax=ax
                    )

                    # Hiển thị thứ tự và trọng số trên cạnh
                    labels = {}

                    for u, v in G.edges():
                        if G.is_directed():
                            key = (u, v)
                        else:
                            key = frozenset((u, v))

                        order = edge_order.get(key)
                        weight = G[u][v].get("weight", 1)

                        if order is not None:
                            labels[(u, v)] = f"{order} (w={weight})"
                        else:
                            labels[(u, v)] = str(weight)

                    nx.draw_networkx_edge_labels(
                        G, pos,
                        edge_labels=labels,
                        font_size=10,
                        ax=ax
                    )

                    ax.set_title(result_type)
                    ax.axis("off")

                    st.pyplot(fig)
                    plt.close(fig)

                    st.caption(
                        "Đỏ: cạnh thuộc đường đi Euler. "
                        "Số trên cạnh: thứ tự đi qua. "
                        "Mũi tên: chiều của cạnh."
                    )

            except Exception as e:
                st.error(f"Lỗi khi xử lý Euler: {e}")

# =========================
# HAMILTON
# =========================

# =========================
# HAMILTON
# =========================

elif menu == "Thuật toán Hamilton":
    st.subheader("Tìm đường đi / Chu trình Hamilton")

    nodes = list(G.nodes())
    n = len(nodes)

    if n < 2:
        st.warning("Cần ít nhất 2 đỉnh.")
    else:
        start = st.selectbox(
            "Điểm bắt đầu",
            nodes,
            key="h_start"
        )

        end = st.selectbox(
            "Điểm kết thúc",
            nodes,
            key="h_end"
        )

        if st.button("Chạy thuật toán Hamilton"):

            def find_hamilton(current, visited, path):

                if len(path) == n:
                    if current == end:
                        return path.copy()
                    return None

                for neighbor in G.neighbors(current):

                    if neighbor in visited:
                        continue

                    visited.add(neighbor)
                    path.append(neighbor)

                    result = find_hamilton(
                        neighbor, visited, path
                    )

                    if result is not None:
                        return result

                    path.pop()
                    visited.remove(neighbor)

                return None

            if start == end:
                st.info("Đang tìm chu trình Hamilton.")

                def find_cycle(current, visited, path):
                    if len(path) == n:
                        if G.has_edge(current, start):
                            return path.copy() + [start]
                        return None

                    for neighbor in G.neighbors(current):
                        if neighbor in visited:
                            continue

                        visited.add(neighbor)
                        path.append(neighbor)

                        result = find_cycle(
                            neighbor, visited, path
                        )

                        if result is not None:
                            return result

                        path.pop()
                        visited.remove(neighbor)

                    return None

                result = find_cycle(start, {start}, [start])

            else:
                st.info("Đang tìm đường đi Hamilton.")
                result = find_hamilton(
                    start, {start}, [start]
                )

            if result:
                st.success("Tìm thấy kết quả Hamilton!")

                st.write("Đường đi:")
                st.code(" → ".join(map(str, result)))

                distance = sum(
                    G[u][v].get("weight", 1)
                    for u, v in zip(result, result[1:])
                )

                st.metric("Tổng khoảng cách", distance)

            else:
                st.error(
                    "Không tồn tại đường đi Hamilton phù hợp."
                )

# =========================
# DIJKSTRA - TRỰC QUAN HÓA
# =========================

elif menu == "Dijkstra":
    st.subheader("Tìm đường đi ngắn nhất - Dijkstra")

    nodes = list(G.nodes())

    if len(nodes) < 2:
        st.warning("Cần ít nhất 2 đỉnh.")

    elif any(data.get("weight", 1) < 0
             for u, v, data in G.edges(data=True)):
        st.error("Dijkstra không hỗ trợ trọng số âm.")

    else:
        c1, c2 = st.columns(2)

        with c1:
            start = st.selectbox(
                "Điểm xuất phát", nodes, key="d_start"
            )

        with c2:
            end = st.selectbox(
                "Điểm đích", nodes, key="d_end"
            )

        if st.button("Tìm đường đi ngắn nhất"):

            try:
                path = nx.dijkstra_path(
                    G, start, end, weight="weight"
                )

                distance = nx.dijkstra_path_length(
                    G, start, end, weight="weight"
                )

                st.success("Đã tìm thấy đường đi ngắn nhất!")

                st.write("### Kết quả")
                st.code(" → ".join(map(str, path)))

                st.metric("Khoảng cách ngắn nhất", distance)

                # Vẽ đồ thị
                st.write("### Trực quan hóa đường đi")

                fig, ax = plt.subplots(figsize=(10, 7))
                pos = nx.spring_layout(G, seed=42)

                path_edges = list(zip(path, path[1:]))

                nx.draw_networkx_nodes(
                    G, pos,
                    node_color="skyblue",
                    node_size=1600,
                    ax=ax
                )

                nx.draw_networkx_labels(
                    G, pos,
                    font_size=12,
                    font_weight="bold",
                    ax=ax
                )

                nx.draw_networkx_edges(
                    G, pos,
                    edge_color="lightgray",
                    width=2,
                    ax=ax
                )

                nx.draw_networkx_edges(
                    G, pos,
                    edgelist=path_edges,
                    edge_color="red",
                    width=4,
                    ax=ax
                )

                edge_labels = {
                    (u, v): data.get("weight", 1)
                    for u, v, data in G.edges(data=True)
                }

                nx.draw_networkx_edge_labels(
                    G, pos,
                    edge_labels=edge_labels,
                    font_size=10,
                    ax=ax
                )

                ax.set_title("Đường đi ngắn nhất - Dijkstra")
                ax.axis("off")

                st.pyplot(fig)
                plt.close(fig)

                st.caption(
                    "Đường màu đỏ: đường đi ngắn nhất."
                )

            except nx.NetworkXNoPath:
                st.error("Không có đường đi giữa hai đỉnh.")
# =========================
# DIJKSTRA - TRỰC QUAN HÓA
# =========================

elif menu == "Dijkstra":
    st.subheader("Tìm đường đi ngắn nhất - Dijkstra")

    nodes = list(G.nodes())

    if len(nodes) < 2:
        st.warning("Cần ít nhất 2 đỉnh.")

    elif any(data.get("weight", 1) < 0
             for u, v, data in G.edges(data=True)):
        st.error("Dijkstra không hỗ trợ trọng số âm.")

    else:
        c1, c2 = st.columns(2)

        with c1:
            start = st.selectbox(
                "Điểm xuất phát", nodes, key="d_start"
            )

        with c2:
            end = st.selectbox(
                "Điểm đích", nodes, key="d_end"
            )

        if st.button("Tìm đường đi ngắn nhất"):

            try:
                path = nx.dijkstra_path(
                    G, start, end, weight="weight"
                )

                distance = nx.dijkstra_path_length(
                    G, start, end, weight="weight"
                )

                st.success("Đã tìm thấy đường đi ngắn nhất!")

                st.write("### Kết quả")
                st.code(" → ".join(map(str, path)))

                st.metric("Khoảng cách ngắn nhất", distance)

                # Vẽ đồ thị
                st.write("### Trực quan hóa đường đi")

                fig, ax = plt.subplots(figsize=(10, 7))
                pos = nx.spring_layout(G, seed=42)

                path_edges = list(zip(path, path[1:]))

                nx.draw_networkx_nodes(
                    G, pos,
                    node_color="skyblue",
                    node_size=1600,
                    ax=ax
                )

                nx.draw_networkx_labels(
                    G, pos,
                    font_size=12,
                    font_weight="bold",
                    ax=ax
                )

                nx.draw_networkx_edges(
                    G, pos,
                    edge_color="lightgray",
                    width=2,
                    ax=ax
                )

                nx.draw_networkx_edges(
                    G, pos,
                    edgelist=path_edges,
                    edge_color="red",
                    width=4,
                    ax=ax
                )

                edge_labels = {
                    (u, v): data.get("weight", 1)
                    for u, v, data in G.edges(data=True)
                }

                nx.draw_networkx_edge_labels(
                    G, pos,
                    edge_labels=edge_labels,
                    font_size=10,
                    ax=ax
                )

                ax.set_title("Đường đi ngắn nhất - Dijkstra")
                ax.axis("off")

                st.pyplot(fig)
                plt.close(fig)

                st.caption(
                    "Đường màu đỏ: đường đi ngắn nhất."
                )

            except nx.NetworkXNoPath:
                st.error("Không có đường đi giữa hai đỉnh.")


# =========================
# FLOYD-WARSHALL NÂNG CAO
# =========================

elif menu == "Floyd-Warshall":
    st.subheader("Thuật toán Floyd-Warshall")

    nodes = list(G.nodes())

    if len(nodes) < 2:
        st.warning("Cần ít nhất 2 đỉnh.")

    elif any(data.get("weight", 1) < 0
             for u, v, data in G.edges(data=True)):
        st.error("Phiên bản này chưa hỗ trợ trọng số âm.")

    else:
        st.write("### Ma trận khoảng cách ngắn nhất")

        if st.button("Tính ma trận Floyd-Warshall"):

            distances = nx.floyd_warshall_numpy(
                G, nodelist=nodes, weight="weight"
            )

            st.session_state.floyd_distances = distances
            st.session_state.floyd_nodes = nodes

            st.success("Đã tính xong ma trận!")

        if "floyd_distances" in st.session_state:
            distances = st.session_state.floyd_distances
            saved_nodes = st.session_state.floyd_nodes

            st.dataframe(
                distances,
                use_container_width=True
            )

            st.divider()
            st.write("### Tìm đường đi giữa hai đỉnh")

            c1, c2 = st.columns(2)

            with c1:
                start = st.selectbox(
                    "Điểm xuất phát",
                    saved_nodes,
                    key="fw_start"
                )

            with c2:
                end = st.selectbox(
                    "Điểm kết thúc",
                    saved_nodes,
                    key="fw_end"
                )

            if st.button("Tìm đường đi Floyd-Warshall"):

                try:
                    path = nx.reconstruct_path(
                        start,
                        end,
                        nx.floyd_warshall_predecessor_and_distance(
                            G, weight="weight"
                        )[0]
                    )

                    distance = distances[
                        saved_nodes.index(start),
                        saved_nodes.index(end)
                    ]

                    if not path:
                        st.error("Không tìm thấy đường đi.")

                    else:
                        st.success("Đã tìm thấy đường đi!")

                        st.code(
                            " → ".join(map(str, path))
                        )

                        st.metric(
                            "Khoảng cách ngắn nhất",
                            float(distance)
                        )

                        # Trực quan hóa
                        fig, ax = plt.subplots(figsize=(10, 7))
                        pos = nx.spring_layout(G, seed=42)

                        path_edges = list(zip(path, path[1:]))

                        nx.draw_networkx_nodes(
                            G, pos,
                            node_color="skyblue",
                            node_size=1600,
                            ax=ax
                        )

                        nx.draw_networkx_labels(
                            G, pos,
                            font_size=12,
                            font_weight="bold",
                            ax=ax
                        )

                        nx.draw_networkx_edges(
                            G, pos,
                            edge_color="lightgray",
                            width=2,
                            ax=ax
                        )

                        nx.draw_networkx_edges(
                            G, pos,
                            edgelist=path_edges,
                            edge_color="red",
                            width=4,
                            ax=ax
                        )

                        edge_labels = {
                            (u, v): data.get("weight", 1)
                            for u, v, data in G.edges(data=True)
                        }

                        nx.draw_networkx_edge_labels(
                            G, pos,
                            edge_labels=edge_labels,
                            ax=ax
                        )

                        ax.set_title("Floyd-Warshall")
                        ax.axis("off")

                        st.pyplot(fig)
                        plt.close(fig)

                except nx.NetworkXNoPath:
                    st.error("Không có đường đi giữa hai đỉnh.")

