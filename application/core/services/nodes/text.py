from application.core.services.nodes.node import CanvasElement


class TextMarker(CanvasElement):
    def __init__(self, editor, canvas, x, y, text):
        super().__init__(editor, canvas, x, y)

        self.name = 'TextMarker'

        self.text = text



