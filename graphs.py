import json
import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout

# JSON data
data = {
  "PEMesh": {
    "libQt6Charts.so.6": {
      "libQt6OpenGLWidgets.so.6": {
        "libQt6OpenGL.so.6": {
          "libQt6Gui.so.6": {
            "libEGL.so.1": {
              "libGLdispatch.so.0": {}
            },
            "libQt6Core.so.6": {
              "libicui18n.so.74": {
                "libicuuc.so.74": {
                  "libicudata.so.74": {}
                }
              },
              "libzstd.so.1": {},
              "libpcre2-16.so.0": {},
              "libb2.so.1": {
                "libgomp.so.1": {}
              },
              "libdouble-conversion.so.3": {},
              "libz.so.1": {},
              "libglib-2.0.so.0": {
                "libpcre2-8.so.0": {}
              },
              "libicuuc.so.74": {}
            },
            "libz.so.1": {},
            "libfreetype.so.6": {
              "libz.so.1": {},
              "libbrotlidec.so.1": {
                "libbrotlicommon.so.1": {}
              },
              "libpng16.so.16": {
                "libz.so.1": {}
              },
              "libbz2.so.1.0": {}
            },
            "libmd4c.so.0": {},
            "libharfbuzz.so.0": {
              "libgraphite2.so.3": {},
              "libglib-2.0.so.0": {},
              "libfreetype.so.6": {}
            },
            "libpng16.so.16": {},
            "libOpenGL.so.0": {
              "libGLdispatch.so.0": {}
            },
            "libGLX.so.0": {
              "libGLdispatch.so.0": {},
              "libX11.so.6": {
                "libxcb.so.1": {
                  "libXau.so.6": {},
                  "libXdmcp.so.6": {
                    "libbsd.so.0": {
                      "libmd.so.0": {}
                    }
                  }
                }
              }
            },
            "libxkbcommon.so.0": {},
            "libQt6DBus.so.6": {
              "libdbus-1.so.3": {
                "libsystemd.so.0": {
                  "libcap.so.2": {},
                  "libzstd.so.1": {},
                  "liblzma.so.5": {},
                  "liblz4.so.1": {},
                  "libgcrypt.so.20": {
                    "libgpg-error.so.0": {}
                  }
                }
              },
              "libQt6Core.so.6": {}
            },
            "libglib-2.0.so.0": {},
            "libX11.so.6": {},
            "libfontconfig.so.1": {
              "libfreetype.so.6": {},
              "libexpat.so.1": {}
            }
          },
          "libQt6Core.so.6": {},
          "libOpenGL.so.0": {}
        },
        "libQt6Core.so.6": {},
        "libQt6Gui.so.6": {},
        "libQt6Widgets.so.6": {
          "libQt6Gui.so.6": {},
          "libQt6Core.so.6": {}
        }
      },
      "libQt6Core.so.6": {},
      "libQt6Gui.so.6": {},
      "libQt6OpenGL.so.6": {},
      "libQt6Widgets.so.6": {}
    },
    "libQt6Core.so.6": {},
    "libQt6Gui.so.6": {},
    "libQt6Widgets.so.6": {},
    "libQt6OpenGLWidgets.so.6": {},
    "libmetis.so.5": {},
    "libGLU.so.1": {
      "libOpenGL.so.0": {}
    },
    "libGL.so.1": {
      "libGLdispatch.so.0": {},
      "libGLX.so.0": {}
    },
    "libQt6Core5Compat.so.6": {
      "libicuuc.so.74": {},
      "libQt6Core.so.6": {}
    }
  },
  "cdt": {
    "libstdc++.so.6":{},
    "libc.so.6":{},
    "libgcc_s.so.1":{},
    "libm.so.6":{}
  }

}


# Function to add edges to the graph
def add_edges(graph, parent, data):
    for key, value in data.items():
        graph.add_edge(parent, key)
        add_edges(graph, key, value)

# Create a directed graph
G = nx.DiGraph()

# Add edges to the graph
root = "PEMesh"
add_edges(G, root, data[root])

# Draw the graph with a tree layout
plt.figure(figsize=(20, 20))
pos = graphviz_layout(G, prog="dot")
nx.draw(G, pos, with_labels=True, node_size=3000, node_color="skyblue", font_size=10, font_weight="bold", arrows=True)
plt.title("Dependency Tree")
plt.savefig("dependency_tree_pemesh.pdf")


# Create a directed graph
G = nx.DiGraph()

# Add edges to the graph
root = "cdt"
add_edges(G, root, data[root])

# Draw the graph with a tree layout
plt.figure(figsize=(8, 8))
pos = graphviz_layout(G, prog="dot")
nx.draw(G, pos, with_labels=True, node_size=3000, node_color="skyblue", font_size=10, font_weight="bold", arrows=True)
plt.title("Dependency Tree")
plt.savefig("dependency_tree_cdt.pdf")
