class GraphWrapper():
    def __init__(self, graph, checkpointer):
        self.graph = graph
        self.checkpointer = checkpointer

    def invoke(self, *args, **kwargs):
        return self.graph.invoke(*args, **kwargs)

    def ainvoke(self, *args, **kwargs):
        return self.graph.invoke(*args, **kwargs)

    def delete_thread(self, thread_id):
        self.checkpointer.delete_thread(thread_id=thread_id)