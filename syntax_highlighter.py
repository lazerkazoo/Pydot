import tkinter
from pygments import lex
from pygments.lexers import get_lexer_by_name


class SyntaxHighlighter:
    def __init__(self, text_widget: tkinter.Text, language: str, theme: dict):
        self.text_widget = text_widget
        self.theme = theme
        self.lexer = get_lexer_by_name(language)
        self.setup_tags()

    def setup_tags(self):
        # Get syntax colors from theme, with fallbacks to accent colors
        syntax = self.theme.get("syntax", {})

        # Keywords (if, for, while, def, class, etc.)
        self.text_widget.tag_configure(
            "Token.Keyword",
            foreground=syntax.get("keyword", self.theme.get("accent_blue")),
        )
        self.text_widget.tag_configure(
            "Token.Keyword.Constant",
            foreground=syntax.get("constant", self.theme.get("accent_orange")),
        )
        self.text_widget.tag_configure(
            "Token.Keyword.Namespace",
            foreground=syntax.get("keyword", self.theme.get("accent_blue")),
        )

        # Built-in functions and types
        self.text_widget.tag_configure(
            "Token.Name.Builtin",
            foreground=syntax.get("builtin", self.theme.get("accent_blue")),
        )
        self.text_widget.tag_configure(
            "Token.Name.Builtin.Pseudo",
            foreground=syntax.get("constant", self.theme.get("accent_orange")),
        )  # For 'self', 'cls', etc.

        # Strings
        self.text_widget.tag_configure(
            "Token.String",
            foreground=syntax.get("string", self.theme.get("accent_green")),
        )
        self.text_widget.tag_configure(
            "Token.String.Doc",
            foreground=syntax.get("comment", self.theme.get("text_secondary")),
        )

        # Numbers
        self.text_widget.tag_configure(
            "Token.Number",
            foreground=syntax.get("number", self.theme.get("accent_orange")),
        )
        self.text_widget.tag_configure(
            "Token.Number.Integer",
            foreground=syntax.get("number", self.theme.get("accent_orange")),
        )
        self.text_widget.tag_configure(
            "Token.Number.Float",
            foreground=syntax.get("number", self.theme.get("accent_orange")),
        )

        # Comments
        self.text_widget.tag_configure(
            "Token.Comment",
            foreground=syntax.get("comment", self.theme.get("text_secondary")),
        )
        self.text_widget.tag_configure(
            "Token.Comment.Single",
            foreground=syntax.get("comment", self.theme.get("text_secondary")),
        )

        # Functions
        self.text_widget.tag_configure(
            "Token.Name.Function",
            foreground=syntax.get("function", self.theme.get("accent_blue")),
        )
        self.text_widget.tag_configure(
            "Token.Name.Function.Magic",
            foreground=syntax.get("function", self.theme.get("accent_blue")),
        )

        # Classes
        self.text_widget.tag_configure(
            "Token.Name.Class",
            foreground=syntax.get("class", self.theme.get("accent_orange")),
        )

        # Operators
        self.text_widget.tag_configure(
            "Token.Operator",
            foreground=syntax.get("operator", self.theme.get("accent_red")),
        )
        self.text_widget.tag_configure(
            "Token.Operator.Word",
            foreground=syntax.get("keyword", self.theme.get("accent_blue")),
        )

        # Decorators
        self.text_widget.tag_configure(
            "Token.Name.Decorator",
            foreground=syntax.get("decorator", self.theme.get("accent_orange")),
        )

        # Variables and names
        self.text_widget.tag_configure(
            "Token.Name",
            foreground=syntax.get("variable", self.theme.get("text_primary")),
        )

    def highlight(self, event=None):
        content = self.text_widget.get("1.0", "end-1c")

        # Clear all previous tags
        for tag in self.text_widget.tag_names():
            if tag.startswith("Token."):
                self.text_widget.tag_remove(tag, "1.0", "end")

        # Tokenize and apply new tags
        start_index = "1.0"
        for ttype, tvalue in lex(content, self.lexer):
            end_index = f"{start_index}+{len(tvalue)}c"
            tag_name = str(ttype)
            if tag_name in self.text_widget.tag_names():
                self.text_widget.tag_add(tag_name, start_index, end_index)
            start_index = end_index
