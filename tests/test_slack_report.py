import os
import shutil
import tempfile
from unittest.mock import patch

import pytest

from bot.slack_handler import handle_report_command


class DummyCommand:
    def __init__(self, text="", channel_id="#test"):
        self.text = text
        self.channel_id = channel_id


def test_handle_report_command_creates_file(tmp_path):
    # Crée un chemin temporaire pour le fichier simulé
    output_path = tmp_path / "rapport_test.pptx"

    # Simule le comportement du sous-processus de génération
    with (
        patch("subprocess.run") as mock_run,
        patch("bot.slack_handler.client.files_upload") as mock_upload,
        patch("bot.slack_handler.client.chat_postMessage") as mock_msg,
    ):

        mock_run.return_value.returncode = 0

        command = DummyCommand(text=str(output_path), channel_id="#test")
        msg = handle_report_command(
            ack=lambda: None, respond=lambda m: None, command=command
        )

        # Vérifie que le fichier est mentionné dans le message de retour
        assert output_path.name in msg
        mock_run.assert_called_once()
        mock_upload.assert_called_once()
        mock_msg.assert_called_once()
