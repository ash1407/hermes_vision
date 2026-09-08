import sys
import threading
from pathlib import Path

from PyQt5.QtWidgets import QApplication

from core import config_loader
from core.model_client import get_client
from ui.avatar_widget import AvatarWidget, IDLE, THINKING, SPEAKING, WATCHING
from ui.chat_window import ChatWindow


class HermesAssistant:
    def __init__(self):
        self.cfg = config_loader.load()
        self.client = get_client()
        self._history = []

        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        self.chat_window = ChatWindow(on_send=self._handle_user_message)
        self.avatar = AvatarWidget(on_click=self._toggle_chat)

        pos = self.cfg["ui"]["avatar_position"]
        self.avatar.move(pos["x"], pos["y"])

        self.avatar.show()
        self._greet()

    def _toggle_chat(self):
        if self.chat_window.isVisible():
            self.chat_window.hide()
        else:
            self.chat_window.show()
            self.chat_window.raise_()

    def _greet(self):
        name = self.cfg["agent"]["name"]
        greeting = f"Hi! I'm {name}. I'm here to help — click me anytime or just keep working and I'll let you know if I notice something useful."
        self.chat_window.append_message("assistant", greeting)
        self._history.append({"role": "assistant", "content": greeting})

    def _handle_user_message(self, text: str):
        self.avatar.set_state(THINKING)
        self._history.append({"role": "user", "content": text})

        system_msg = {
            "role": "system",
            "content": (
                f"You are {self.cfg['agent']['name']}, a helpful desktop AI assistant. "
                "You are observing the user's screen and camera. "
                "Be concise, friendly, and proactive. "
                "If you notice patterns or issues, mention them naturally."
            ),
        }

        messages = [system_msg] + self._history[-20:]

        try:
            response = self.client.chat(messages)
            reply = self.client.extract_text(response)
        except Exception as e:
            reply = f"Sorry, I ran into an issue: {e}"

        self._history.append({"role": "assistant", "content": reply})
        self.chat_window.append_message("assistant", reply)
        self.avatar.set_state(SPEAKING)

        threading.Timer(2.0, lambda: self.avatar.set_state(WATCHING)).start()

    def push_agent_message(self, text: str):
        """Called by the agent loop to proactively message the user."""
        self.chat_window.append_message("assistant", text)
        self.chat_window.show()
        self.chat_window.raise_()
        self.avatar.set_state(SPEAKING)
        self._history.append({"role": "assistant", "content": text})
        threading.Timer(3.0, lambda: self.avatar.set_state(WATCHING)).start()

    def run(self):
        self.avatar.set_state(WATCHING)
        sys.exit(self.app.exec_())


def main():
    assistant = HermesAssistant()
    assistant.run()


if __name__ == "__main__":
    main()
