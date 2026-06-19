from PySide6.QtWidgets import QWidget, QHBoxLayout
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile


# modified version of this: https://runebook.dev/en/docs/qt/qlabel/wordWrap-prop
def word_wrap(text, max_chars=45):
    "adds zero-width chars that help PySide know when to do a word wrap, it does it either between words or in the middle of a word if it's over 25 chars"
    return " ".join(
        (
            "\u200b".join(w[i : i + max_chars] for i in range(0, len(w), max_chars))
            if len(w) > max_chars
            else w
        )
        for w in text.split(" ")
    )


class MessageBubble(QWidget):
    # parent width is the width of the whole text area
    def __init__(self, text, timestamp, sender, is_me, parent_width):
        super().__init__()
        # https://doc.qt.io/qtforpython-6/PySide6/QtUiTools/QUiLoader.html#PySide6.QtUiTools.QUiLoader

        # configure the labels
        self.__bubble = QUiLoader().load(
            QFile("message_item.ui"), None
        )  # load the .ui file
        self.__bubble.senderLabel.setText(sender)  # type: ignore
        self.__bubble.timeLabel.setText(timestamp)  # type: ignore
        self.__bubble.messageLabel.setText(word_wrap(text))  # type: ignore

        # size the bubble
        max_w = int(
            max(parent_width, 200) * 0.65
        )  # sets a bubble to be 65% the horizontal size of the chat area, least (200*0.65 = 130px) in size
        self.__bubble.setMaximumWidth(max_w)
        self.__bubble.setFixedWidth(  # if there's less than 30 chars in the message try to make the chat bubble smaller
            min(max_w, max(140, self.__bubble.minimumSizeHint().width()))
            if len(text) < 30
            else max_w
        )  # https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QWidget.html#id24
        # minimum size hint returns the smaller dimensions an object can have while still having all content fit (it returns a QSize object, so we use the .width() for it )
        self.__bubble.adjustSize()  # change the actual size

        # style the bubble
        # Copilot helped me generate this, i removed the padding it added, and added the ;background:transparent; to make sure the bubble's background isn't visible
        style_me = "QWidget#messageItemWidget{background:#0078FF;border-radius:14px;}QLabel{color:white;background:transparent;}"
        style_them = "QWidget#messageItemWidget{background:#E9E9EB;border-radius:14px;}QLabel{color:black;background:transparent;}"
        self.__bubble.setStyleSheet(
            style_me if is_me else style_them
        )  # sets the style to be the gray message if the other person sent it, if you did it makes it blue :)

        # position the bubble
        row = QHBoxLayout(
            self
        )  # create a layout box so we can place the message left or right (depending on if you or the other person sent it)
        row.setContentsMargins(10, 4, 10, 4)  # add some padding in px
        if is_me:  # if it's your message add a spacer then bubble (pushes it right)
            row.addStretch()
            row.addWidget(self.__bubble)
        else:  # if it's the other person add the bubble the the spacer after it (pushes left)
            row.addWidget(self.__bubble)
            row.addStretch()
