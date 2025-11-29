# GreenBin: Smart Waste Management System 🌿♻️

GreenBin is a comprehensive, data-driven smart waste management dashboard designed to optimize urban logistics. It simulates a real-time network of smart bins and processing facilities, providing city managers with tools to monitor waste levels, manage collection requests, optimize dispatch routes, and predict future overflows.

This project serves as a practical application of **Data Structures and Algorithms (DSA)**, demonstrating how abstract concepts like Graphs, AVL Trees, and Priority Queues solve real-world problems.

## 🚀 Key Features

*   **📊 Real-Time Dashboard**: Live monitoring of collection stats, CO2 reduction, and waste composition.
*   **🗑️ Dynamic Bin Registry**: Manage a city-wide network of smart bins with real-time fill level updates.
*   **🚚 Smart Dispatch**: 
    *   **Priority Collection**: Uses a **Priority Queue (Max-Heap)** to automatically identify and dispatch trucks to the most urgent bins (≥80% full).
    *   **Route Optimization**: Uses **Dijkstra's Algorithm** on a weighted graph to find the shortest path from bins to facilities.
*   **🗺️ Interactive Map**: Visualizes the road network, bin locations, and optimal routes using Plotly.
*   **🏭 Facility Management**: Indexes recycling centers using an **AVL Tree** for efficient O(log n) retrieval and sorting.
*   **🔮 AI Predictions**: Forecasts bin overflows based on historical data and waste type.
*   **↩️ Global Undo**: Implements a **Stack-based** undo system to revert accidental actions.
*   **📨 Request Queue**: Manages citizen collection requests using a FIFO **Queue**.

## 🛠️ Tech Stack

*   **Language**: Python 3.x
*   **Framework**: [NiceGUI](https://nicegui.io/) (Vue.js based Python wrapper)
*   **Data Processing**: Pandas
*   **Visualization**: Plotly (Maps), Apache ECharts (Charts)
*   **Data Structures**: Custom implementations of AVL Tree, Graph, Priority Queue, Stack, Queue.

## 📂 Project Structure

```
GreenBin/
├── app.py                 # Main application controller
├── views/                 # UI Modules
│   ├── dashboard.py       # Main stats & charts
│   ├── dispatch.py        # Map & routing logic
│   ├── bins.py            # Bin registry
│   └── ...
├── structures/            # Custom Data Structures
│   ├── avl_tree.py
│   ├── graph.py
│   ├── priority_queue.py
│   └── ...
├── algorithms/            # Core Algorithms
│   ├── dijkstra.py
│   └── sorting.py
├── models/                # Data Models (Bin, Facility)
├── services/              # Business Logic
└── data/                  # JSON storage
```

## ⚡ Installation & Usage

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/yaredzb/GreenBin.git
    cd GreenBin
    ```

2.  **Install dependencies**:
    ```bash
    pip install nicegui pandas plotly networkx
    ```

3.  **Run the application**:
    ```bash
    python app.py
    ```

4.  **Access the Dashboard**:
    Open your browser and navigate to `http://localhost:8085`.

## 🧠 Algorithms in Action

| Feature | Data Structure / Algorithm | Complexity |
| :--- | :--- | :--- |
| **Urgent Dispatch** | Priority Queue (Max-Heap) | $O(\log n)$ |
| **Route Optimization** | Graph + Dijkstra's Algo | $O(E + V \log V)$ |
| **Facility Search** | AVL Tree | $O(\log n)$ |
| **Facility Sorting** | Merge Sort | $O(n \log n)$ |
| **Undo System** | Stack (LIFO) | $O(1)$ |
| **Request Queue** | Queue (FIFO) | $O(1)$ |

## 📝 License

This project is open-source and available under the MIT License.
