"""Windows TCP and real ROS daemon validation. No ROS dependency stubs."""
import argparse
from contextlib import contextmanager
import os
import socket
import threading
import time
from unittest.mock import patch

import pytest
import rclpy
from ros2cli import daemon
from ros2cli.node import daemon as daemon_node

pytestmark = pytest.mark.skipif(os.name != 'nt', reason='Real Windows socket checks')


@contextmanager
def held_address(listen=False, release_after=None):
    owner = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    owner.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
    owner.bind(('127.0.0.1', 0))
    address = owner.getsockname()
    if listen:
        owner.listen(1)
    timer = None
    try:
        with patch.object(daemon, 'get_address', return_value=address):
            # Establish the actual socket conflict before testing the retry path.
            with pytest.raises(OSError):
                daemon.make_xmlrpc_server()
            if release_after is not None:
                timer = threading.Timer(release_after, owner.close)
                timer.start()
            yield address
    finally:
        owner.close()
        if timer is not None:
            timer.cancel()
            timer.join(6)


def test_reacquires_real_windows_socket_after_shutdown_tail():
    with held_address(release_after=0.25):
        server = daemon_node._make_xmlrpc_server_when_available(argparse.Namespace(), 2.0)
        assert server is not None
        server.server_close()


def test_foreign_bound_socket_is_bounded():
    with held_address():
        start = time.monotonic()
        server = daemon_node._make_xmlrpc_server_when_available(argparse.Namespace(), -1.0)
        elapsed = time.monotonic() - start
        if server is not None:
            server.server_close()
        assert server is None
        assert elapsed < 1.75, elapsed


def test_nonresponsive_listening_socket_is_bounded():
    # A real TCP listener accepts the connection handshake but never serves XML-RPC.
    # Close it after four seconds so a broken implementation cannot hang this job.
    with held_address(listen=True, release_after=4.0):
        start = time.monotonic()
        server = daemon_node._make_xmlrpc_server_when_available(argparse.Namespace(), -1.0)
        elapsed = time.monotonic() - start
        if server is not None:
            server.server_close()
        assert elapsed < 1.75, elapsed
        assert server is None


def test_live_xmlrpc_daemon_is_not_replaced():
    server = daemon.make_xmlrpc_server()
    server.register_introspection_functions()
    worker = threading.Thread(target=server.serve_forever, kwargs={'poll_interval': 0.01})
    worker.start()
    try:
        start = time.monotonic()
        replacement = daemon_node._make_xmlrpc_server_when_available(argparse.Namespace(), 2.0)
        assert replacement is None
        assert time.monotonic() - start < 1.0
    finally:
        server.shutdown()
        worker.join(5)
        server.server_close()


def test_real_daemon_restarts_after_inactivity():
    args = argparse.Namespace()
    print('RMW', rclpy.get_rmw_implementation_identifier())
    try:
        for _ in range(3):
            assert daemon_node.spawn_daemon(args, timeout=10.0, debug=True, inactivity_timeout=0.2)
            # Querying a live daemon resets its inactivity timer, so do not poll it.
            time.sleep(0.7)
            assert not daemon_node.is_daemon_running(args)
    finally:
        daemon_node.shutdown_daemon(args, timeout=10.0)
