"""Tests de la comprobación de instancia única (puerto del API libre u ocupado)."""

import socket

import main


def test_port_is_free_false_while_held_and_true_after_close():
    holder = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    holder.bind(("127.0.0.1", 0))
    holder.listen(1)
    port = holder.getsockname()[1]
    try:
        assert main.port_is_free("127.0.0.1", port) is False
    finally:
        holder.close()
    assert main.port_is_free("127.0.0.1", port) is True
